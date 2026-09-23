from app.modules.candidate_discovery import normalize_discovery_input
from app.modules.product_verification import verify_product_page
from app.schemas import CandidateProduct, CandidateSignals, DiscoveryCandidateInput, IdentifiedCard


def _identified_card() -> IdentifiedCard:
    return IdentifiedCard(
        image_id="00000000-0000-0000-0000-000000000000",
        card_name="Pikachu",
        set_name="Base Set",
        card_number="58/102",
        variant="Unlimited",
        promo=False,
        confidence=0.95,
        notes=[],
    )


def _candidate(**overrides: object) -> CandidateProduct:
    payload = {
        "candidate_name": "Pikachu",
        "raw_title": "Pikachu Base Set 58/102 Unlimited",
        "set_name": "Base Set",
        "card_number": "58/102",
        "variant": "Unlimited",
        "promo": False,
        "source": "external_candidate_feed",
        "candidate_url": None,
        "confidence_signals": CandidateSignals(
            name_exact=True,
            set_exact=True,
            number_exact=True,
            variant_compatible=True,
            promo_compatible=True,
        ),
    }
    payload.update(overrides)
    return CandidateProduct(**payload)


def test_exact_match_verification_without_url_stays_unverified() -> None:
    result = verify_product_page(_identified_card(), [_candidate()])
    assert result.best_match_score >= result.threshold_used
    assert result.verified is False
    assert result.verified_product_url is None


def test_mismatch_on_set_fails_verification() -> None:
    result = verify_product_page(_identified_card(), [_candidate(set_name="Jungle")])
    assert result.verified is False
    assert result.verified_product_url is None
    assert "set_mismatch" in result.reason


def test_mismatch_on_card_number_fails_verification() -> None:
    result = verify_product_page(_identified_card(), [_candidate(card_number="59/102")])
    assert result.verified is False
    assert result.verified_product_url is None
    assert "card_number_mismatch" in result.reason


def test_mismatch_on_variant_fails_verification() -> None:
    result = verify_product_page(_identified_card(), [_candidate(variant="1st Edition")])
    assert result.verified is False
    assert result.verified_product_url is None
    assert "variant_mismatch" in result.reason


def test_unverifiable_candidates_stay_unverified() -> None:
    result = verify_product_page(_identified_card(), [_candidate(candidate_url=None)])
    assert result.verified is False
    assert result.verified_product_url is None
    assert "no real upstream candidate_url" in result.reason


def test_verified_candidate_with_real_upstream_url_is_allowed() -> None:
    upstream_url = "https://example.com/upstream-verified-candidate-url"
    result = verify_product_page(_identified_card(), [_candidate(candidate_url=upstream_url)])
    assert result.verified is True
    assert result.verified_product_url == upstream_url
    assert result.best_match_score >= result.threshold_used


def test_verification_on_normalized_discovery_candidate() -> None:
    discovery = DiscoveryCandidateInput(
        title="Pikachu - Base Set 58/102 Unlimited",
        url="https://provider.example/candidate-1",
        source="provider_x",
        extracted_set_name="Base Set",
        extracted_card_number="58/102",
        notes=["from provider x"],
    )
    candidate = normalize_discovery_input(discovery)
    candidate.promo = False

    result = verify_product_page(_identified_card(), [candidate])

    assert result.verified is True
    assert result.verified_product_url == "https://provider.example/candidate-1"


def test_incomplete_discovery_input_is_not_upgraded_to_fully_qualified_candidate() -> None:
    discovery = DiscoveryCandidateInput(
        title="Pikachu card listing",
        url=None,
        source="provider_x",
    )

    candidate = normalize_discovery_input(discovery)

    assert candidate.candidate_url is None
    assert candidate.set_name is None
    assert candidate.card_number is None
    assert candidate.variant is None
