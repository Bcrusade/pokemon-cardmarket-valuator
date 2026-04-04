from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_parse_html_endpoint_rejects_unknown_candidate_urls() -> None:
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

    html = (FIXTURES / "product_page_complete.html").read_text()

    parsed = client.post(
        f"/jobs/{job_id}/candidates/parse-html",
        json={
            "pages": [
                {"candidate_url": "https://provider.example/result-1", "html": html},
                {"candidate_url": "https://provider.example/unknown", "html": html},
            ]
        },
    )

    assert parsed.status_code == 400
    assert "unknown_candidate_urls" in parsed.json()["detail"]
