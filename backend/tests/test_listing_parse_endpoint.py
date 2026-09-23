from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_listing_parse_endpoint_rejects_unknown_candidate_urls() -> None:
    client = TestClient(app)
    created = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"})
    job_id = created.json()["job_id"]

    html = (FIXTURES / "listings_complete.html").read_text()
    response = client.post(
        f"/jobs/{job_id}/candidates/parse-listings",
        json={"pages": [{"candidate_url": "https://provider.example/unknown", "html": html}]},
    )

    assert response.status_code == 400
    assert "unknown_candidate_urls" in response.json()["detail"]


def test_listing_parse_endpoint_parses_and_flags_anomalies() -> None:
    client = TestClient(app)
    created = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"})
    job_id = created.json()["job_id"]

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

    html = (FIXTURES / "listings_complete.html").read_text()
    parsed = client.post(
        f"/jobs/{job_id}/candidates/parse-listings",
        json={"pages": [{"candidate_url": "https://provider.example/result-1", "html": html}]},
    )

    assert parsed.status_code == 200
    body = parsed.json()
    assert body["parsed_count"] == 2
    assert body["rows"][0]["flagged_anomaly"] is False
    assert body["rows"][1]["flagged_anomaly"] is True

    job = client.get(f"/jobs/{job_id}")
    parsed_rows = job.json()["metadata"]["parsed_listing_rows"]["https://provider.example/result-1"]
    assert len(parsed_rows) == 2
