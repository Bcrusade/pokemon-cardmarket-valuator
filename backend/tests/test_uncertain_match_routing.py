from fastapi.testclient import TestClient

from app.main import app


def test_uncertain_match_routes_to_cards_to_clarify() -> None:
    client = TestClient(app)

    created = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"})
    job_id = created.json()["job_id"]

    upload = client.post(
        f"/jobs/{job_id}/images",
        files=[("files", ("card.jpg", b"fake", "image/jpeg"))],
    )
    assert upload.status_code == 200

    analyzed = client.post(f"/jobs/{job_id}/analyze")
    assert analyzed.status_code == 200
    body = analyzed.json()

    assert len(body["cards_to_clarify"]) == 1
    assert "Insufficient" in body["cards_to_clarify"][0]["reason"]
