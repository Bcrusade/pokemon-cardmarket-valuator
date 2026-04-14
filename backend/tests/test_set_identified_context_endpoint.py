from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app
from app.store import store


def _create_job_and_candidate(client: TestClient) -> tuple[str, str]:
    job_id = client.post('/jobs', json={'target_language': 'English', 'minimum_condition': 'NM'}).json()['job_id']
    candidate_url = 'https://provider.example/candidate-context'
    ingest = client.post(
        f'/jobs/{job_id}/candidates',
        json={
            'results': [
                {
                    'title': 'Pikachu - Base Set 58/102 Unlimited',
                    'url': candidate_url,
                    'source': 'provider_x',
                    'extracted_set_name': 'Base Set',
                    'extracted_card_number': '58/102',
                }
            ]
        },
    )
    assert ingest.status_code == 200
    return job_id, candidate_url


def test_set_identified_context_success() -> None:
    client = TestClient(app)
    job_id, candidate_url = _create_job_and_candidate(client)

    response = client.post(
        f'/jobs/{job_id}/candidates/set-identified-context',
        json={
            'candidate_url': candidate_url,
            'card_name': 'Pikachu',
            'set_name': 'Base Set',
            'card_number': '58/102',
            'variant': 'Unlimited',
            'promo': False,
            'confidence': 0.97,
            'notes': ['manually confirmed from uploaded image'],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'candidate_url': candidate_url, 'stored': True}

    identified = store.get_identified_card_context(UUID(job_id), candidate_url)
    assert identified is not None
    assert identified.card_name == 'Pikachu'
    assert identified.promo is False
    assert identified.confidence == 0.97


def test_set_identified_context_accepts_null_promo() -> None:
    client = TestClient(app)
    job_id, candidate_url = _create_job_and_candidate(client)

    response = client.post(
        f'/jobs/{job_id}/candidates/set-identified-context',
        json={
            'candidate_url': candidate_url,
            'card_name': 'Pikachu',
            'set_name': 'Base Set',
            'card_number': '58/102',
            'variant': 'Unlimited',
            'promo': None,
            'confidence': 0.91,
        },
    )

    assert response.status_code == 200
    identified = store.get_identified_card_context(UUID(job_id), candidate_url)
    assert identified is not None
    assert identified.promo is None


def test_set_identified_context_rejects_unknown_candidate_url() -> None:
    client = TestClient(app)
    job_id, _ = _create_job_and_candidate(client)

    response = client.post(
        f'/jobs/{job_id}/candidates/set-identified-context',
        json={
            'candidate_url': 'https://provider.example/unknown',
            'card_name': 'Pikachu',
            'set_name': 'Base Set',
            'card_number': '58/102',
            'variant': 'Unlimited',
            'promo': False,
            'confidence': 0.97,
        },
    )

    assert response.status_code == 400


def test_set_identified_context_unknown_job_returns_404() -> None:
    client = TestClient(app)
    response = client.post(
        '/jobs/00000000-0000-0000-0000-000000000001/candidates/set-identified-context',
        json={
            'candidate_url': 'https://provider.example/candidate-context',
            'card_name': 'Pikachu',
            'set_name': 'Base Set',
            'card_number': '58/102',
            'variant': 'Unlimited',
            'promo': False,
            'confidence': 0.97,
        },
    )

    assert response.status_code == 404
