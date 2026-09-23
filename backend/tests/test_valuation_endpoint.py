from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _seed_known_candidate_with_parsed_rows(client: TestClient, job_id: str) -> None:
    client.post(
        f"/jobs/{job_id}/candidates",
        json={
            "results": [
                {
                    "title": "Pikachu - Base Set 58/102 Unlimited",
                    "url": "https://provider.example/result-1",
                    "source": "provider_x",
                }
            ]
        },
    )
    listings_html = (FIXTURES / "listings_complete.html").read_text()
    client.post(
        f"/jobs/{job_id}/candidates/parse-listings",
        json={"pages": [{"candidate_url": "https://provider.example/result-1", "html": listings_html}]},
    )


def test_valuation_endpoint_happy_path() -> None:
    client = TestClient(app)
    job_id = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"}).json()["job_id"]
    _seed_known_candidate_with_parsed_rows(client, job_id)

    response = client.post(
        f"/jobs/{job_id}/candidates/valuate",
        json={"candidate_url": "https://provider.example/result-1", "verified_filtered_demonstrable": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["candidate_url"] == "https://provider.example/result-1"
    assert body["pricing_method"] == "verified_filtered_avg5"


def test_valuation_endpoint_rejects_unknown_candidate_url() -> None:
    client = TestClient(app)
    job_id = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"}).json()["job_id"]

    response = client.post(
        f"/jobs/{job_id}/candidates/valuate",
        json={"candidate_url": "https://provider.example/unknown", "verified_filtered_demonstrable": True},
    )
    assert response.status_code == 400


def test_valuation_endpoint_rejects_no_usable_rows() -> None:
    client = TestClient(app)
    job_id = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"}).json()["job_id"]

    client.post(
        f"/jobs/{job_id}/candidates",
        json={
            "results": [
                {
                    "title": "Pikachu listing",
                    "url": "https://provider.example/result-1",
                    "source": "provider_x",
                }
            ]
        },
    )

    malformed_html = (FIXTURES / "listings_malformed.html").read_text()
    client.post(
        f"/jobs/{job_id}/candidates/parse-listings",
        json={"pages": [{"candidate_url": "https://provider.example/result-1", "html": malformed_html}]},
    )

    response = client.post(
        f"/jobs/{job_id}/candidates/valuate",
        json={"candidate_url": "https://provider.example/result-1", "verified_filtered_demonstrable": False},
    )

    assert response.status_code == 400
