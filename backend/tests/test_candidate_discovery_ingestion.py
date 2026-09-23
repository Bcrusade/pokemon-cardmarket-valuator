from fastapi.testclient import TestClient

from app.main import app


def test_candidate_discovery_ingestion_normalizes_and_stores_raw_input() -> None:
    client = TestClient(app)
    created = client.post("/jobs", json={"target_language": "English", "minimum_condition": "NM"})
    job_id = created.json()["job_id"]

    payload = {
        "results": [
            {
                "title": "Pikachu - Base Set 58/102 Unlimited",
                "url": "https://provider.example/result-1",
                "source": "provider_x",
                "extracted_set_name": "Base Set",
                "extracted_card_number": "58/102",
                "notes": ["top result"],
            },
            {
                "title": "Pikachu listing",
                "url": None,
                "source": "provider_y",
            },
        ]
    }

    ingested = client.post(f"/jobs/{job_id}/candidates", json=payload)
    assert ingested.status_code == 200
    body = ingested.json()
    assert body["ingested_count"] == 2
    assert body["candidates"][0]["candidate_url"] == "https://provider.example/result-1"
    assert body["candidates"][1]["candidate_url"] is None

    job = client.get(f"/jobs/{job_id}")
    assert job.status_code == 200
    metadata = job.json()["metadata"]
    assert len(metadata["candidate_discovery_raw"]) == 2
    assert len(metadata["candidate_discovery_normalized"]) == 2
