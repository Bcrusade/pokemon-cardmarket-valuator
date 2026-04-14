from uuid import UUID

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import IdentifiedCard
from app.store import store


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _save_identified(job_id: str, url: str, *, name: str = "Pikachu", promo: bool = False) -> None:
    store.save_identified_card_context(
        UUID(job_id),
        url,
        IdentifiedCard(
            image_id="00000000-0000-0000-0000-000000000000",
            card_name=name,
            set_name="Base Set",
            card_number="58/102",
            variant="Unlimited",
            promo=promo,
            confidence=0.95,
            notes=["seeded test context"],
        ),
    )


def _create_job_with_candidate(client: TestClient, *, set_name: str | None, card_number: str | None, title: str) -> tuple[str, str]:
    job_id = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"}).json()["job_id"]
    url = "https://provider.example/candidate-full"
    payload = {
        "title": title,
        "url": url,
        "source": "provider_x",
    }
    if set_name is not None:
        payload["extracted_set_name"] = set_name
    if card_number is not None:
        payload["extracted_card_number"] = card_number

    client.post(f"/jobs/{job_id}/candidates", json={"results": [payload]})
    return job_id, url


def test_full_pipeline_success() -> None:
    client = TestClient(app)
    job_id, url = _create_job_with_candidate(
        client,
        set_name="Base Set",
        card_number="58/102",
        title="Pikachu - Base Set 58/102 Unlimited",
    )
    _save_identified(job_id, url)
    store.save_verified_filtered_context(UUID(job_id), url, True)

    full_html = (
        "<html><h1>Pikachu</h1><div data-set-name=\"Base Set\"></div><span>58/102</span><span>Unlimited</span>"
        "<table><tr class=\"listing-row\"><td data-price=\"1.00\"></td></tr>"
        "<tr class=\"listing-row\"><td data-price=\"2.00\"></td></tr>"
        "<tr class=\"listing-row\"><td data-price=\"3.00\"></td></tr>"
        "<tr class=\"listing-row\"><td data-price=\"4.00\"></td></tr>"
        "<tr class=\"listing-row\"><td data-price=\"5.00\"></td></tr></table></html>"
    )
    client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "provided", "provided_html": full_html},
    )

    response = client.post(f"/jobs/{job_id}/candidates/run-full-evaluation", json={"candidate_url": url})
    assert response.status_code == 200
    body = response.json()
    assert body["verification"]["verified"] is True
    assert body["pricing"]["average_price"] == 3.0


def test_verification_failure_stops_pricing() -> None:
    client = TestClient(app)
    job_id, url = _create_job_with_candidate(client, set_name=None, card_number=None, title="Unknown card")
    _save_identified(job_id, url, name="Completely Different Card")

    incomplete_html = (FIXTURES / "product_page_incomplete.html").read_text()
    client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "provided", "provided_html": incomplete_html},
    )

    response = client.post(f"/jobs/{job_id}/candidates/run-full-evaluation", json={"candidate_url": url})
    assert response.status_code == 200
    body = response.json()
    assert body["verification"]["verified"] is False
    assert body["pricing"] is None


def test_missing_listing_rows_rejected() -> None:
    client = TestClient(app)
    job_id, url = _create_job_with_candidate(
        client,
        set_name="Base Set",
        card_number="58/102",
        title="Pikachu - Base Set 58/102 Unlimited",
    )
    _save_identified(job_id, url)
    no_rows_html = (FIXTURES / "product_page_complete.html").read_text()
    client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "provided", "provided_html": no_rows_html},
    )

    response = client.post(f"/jobs/{job_id}/candidates/run-full-evaluation", json={"candidate_url": url})
    assert response.status_code == 400


def test_anomaly_only_rows_rejected() -> None:
    client = TestClient(app)
    job_id, url = _create_job_with_candidate(
        client,
        set_name="Base Set",
        card_number="58/102",
        title="Pikachu - Base Set 58/102 Unlimited",
    )
    _save_identified(job_id, url)
    anomaly_html = (
        "<html><h1>Pikachu</h1><div data-set-name=\"Base Set\"></div><span>58/102</span><span>Unlimited</span>"
        "<table><tr class=\"listing-row\"><td data-price=\"99999\" data-flags=\"non-comparable\"></td></tr></table></html>"
    )
    client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "provided", "provided_html": anomaly_html},
    )

    response = client.post(f"/jobs/{job_id}/candidates/run-full-evaluation", json={"candidate_url": url})
    assert response.status_code == 400


def test_fallback_pricing_mode() -> None:
    client = TestClient(app)
    job_id, url = _create_job_with_candidate(
        client,
        set_name="Base Set",
        card_number="58/102",
        title="Pikachu - Base Set 58/102 Unlimited",
    )
    _save_identified(job_id, url)

    fallback_html = (
        "<html><h1>Pikachu</h1><table>"
        "<tr class=\"listing-row\"><td data-price=\"4.00\"></td></tr>"
        "<tr class=\"listing-row\"><td data-price=\"6.00\"></td></tr>"
        "</table></html>"
    )
    client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "provided", "provided_html": fallback_html},
    )

    response = client.post(f"/jobs/{job_id}/candidates/run-full-evaluation", json={"candidate_url": url})
    assert response.status_code == 200
    body = response.json()
    assert body["pricing"]["pricing_method"] == "nm_visible_benchmark"


def test_missing_identified_context_rejected() -> None:
    client = TestClient(app)
    job_id, url = _create_job_with_candidate(
        client,
        set_name="Base Set",
        card_number="58/102",
        title="Pikachu - Base Set 58/102 Unlimited",
    )
    html = "<html><h1>Pikachu</h1></html>"
    client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "provided", "provided_html": html},
    )

    response = client.post(f"/jobs/{job_id}/candidates/run-full-evaluation", json={"candidate_url": url})
    assert response.status_code == 400


def test_unknown_promo_stays_unknown_in_candidate() -> None:
    client = TestClient(app)
    job_id, url = _create_job_with_candidate(
        client,
        set_name="Base Set",
        card_number="58/102",
        title="Pikachu - Base Set 58/102 Unlimited",
    )
    _save_identified(job_id, url)

    job = store.get_job(UUID(job_id))
    for candidate in job.metadata["candidate_discovery_normalized"]:
        if candidate["candidate_url"] == url:
            assert candidate["promo"] is None
            break
    else:
        raise AssertionError("Expected candidate entry for URL")


def test_candidate_metadata_alone_cannot_self_validate() -> None:
    client = TestClient(app)
    job_id, url = _create_job_with_candidate(
        client,
        set_name="Base Set",
        card_number="58/102",
        title="Pikachu - Base Set 58/102 Unlimited",
    )
    # Original identified card intentionally conflicts with candidate metadata.
    _save_identified(job_id, url, name="Charizard")

    html = "<html><h1>Pikachu</h1><div data-set-name=\"Base Set\"></div><span>58/102</span><span>Unlimited</span></html>"
    client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "provided", "provided_html": html},
    )

    response = client.post(f"/jobs/{job_id}/candidates/run-full-evaluation", json={"candidate_url": url})
    assert response.status_code == 200
    assert response.json()["verification"]["verified"] is False


def test_realistic_fixtures_produce_verified_pricing_result() -> None:
    client = TestClient(app)
    job_id, url = _create_job_with_candidate(
        client,
        set_name="Base Set",
        card_number="58/102",
        title="Pikachu - Base Set 58/102 Unlimited",
    )
    _save_identified(job_id, url)
    store.save_verified_filtered_context(UUID(job_id), url, True)

    product_html = (FIXTURES / "cardmarket_product_valid.html").read_text()
    listing_html = (FIXTURES / "cardmarket_listings_valid.html").read_text()
    client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "provided", "provided_html": f"{product_html}{listing_html}"},
    )

    response = client.post(f"/jobs/{job_id}/candidates/run-full-evaluation", json={"candidate_url": url})
    assert response.status_code == 200
    body = response.json()
    assert body["verification"]["verified"] is True
    assert body["pricing"]["average_price"] == 4.75
    assert body["pricing"]["pricing_method"] == "verified_filtered_avg5"


def test_realistic_mismatch_fixture_fails_verification_cleanly() -> None:
    client = TestClient(app)
    job_id, url = _create_job_with_candidate(
        client,
        set_name=None,
        card_number=None,
        title="Uncertain card candidate",
    )
    _save_identified(job_id, url, name="Pikachu")
    mismatch_html = (FIXTURES / "cardmarket_product_mismatch.html").read_text()
    client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "provided", "provided_html": mismatch_html},
    )

    response = client.post(f"/jobs/{job_id}/candidates/run-full-evaluation", json={"candidate_url": url})
    assert response.status_code == 200
    body = response.json()
    assert body["verification"]["verified"] is False
    assert body["pricing"] is None
