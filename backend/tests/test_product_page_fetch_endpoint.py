from fastapi.testclient import TestClient

from app.main import app
from app.modules.product_page_fetch import InMemoryHtmlFetcher


def _seed_candidate(client: TestClient, job_id: str, url: str) -> None:
    client.post(
        f"/jobs/{job_id}/candidates",
        json={"results": [{"title": "Pikachu listing", "url": url, "source": "provider_x"}]},
    )


def test_known_candidate_fetch_succeeds_through_mock_fetcher() -> None:
    client = TestClient(app)
    job_id = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"}).json()["job_id"]
    url = "https://provider.example/result-1"
    _seed_candidate(client, job_id, url)

    app.state.fetch_adapter = InMemoryHtmlFetcher({url: "<html><h1>Pikachu</h1></html>"})

    response = client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "fetched"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stored"] is True
    assert body["retrieval_mode"] == "fetched"


def test_unknown_candidate_url_rejected() -> None:
    client = TestClient(app)
    job_id = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"}).json()["job_id"]

    response = client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": "https://provider.example/unknown", "retrieval_mode": "fetched"},
    )

    assert response.status_code == 400


def test_fetched_html_stored_with_retrieval_metadata() -> None:
    client = TestClient(app)
    job_id = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"}).json()["job_id"]
    url = "https://provider.example/result-2"
    _seed_candidate(client, job_id, url)

    app.state.fetch_adapter = InMemoryHtmlFetcher({url: "<html><h1>Stored</h1></html>"})
    client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={"candidate_url": url, "retrieval_mode": "fetched"},
    )

    job = client.get(f"/jobs/{job_id}").json()
    stored = job["metadata"]["stored_product_html"][url]
    assert stored["html"].startswith("<html>")
    assert stored["retrieval_mode"] == "fetched"
    assert stored["source"] == "product_page_retrieval_service"


def test_provided_html_mode_is_supported_and_stored() -> None:
    client = TestClient(app)
    job_id = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"}).json()["job_id"]
    url = "https://provider.example/result-3"
    _seed_candidate(client, job_id, url)

    response = client.post(
        f"/jobs/{job_id}/candidates/fetch-html",
        json={
            "candidate_url": url,
            "retrieval_mode": "provided",
            "provided_html": "<html><h1>Provided</h1></html>",
        },
    )

    assert response.status_code == 200
    job = client.get(f"/jobs/{job_id}").json()
    assert job["metadata"]["stored_product_html"][url]["retrieval_mode"] == "provided"
