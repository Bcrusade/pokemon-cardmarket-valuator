from pathlib import Path

from app.modules.product_metadata_parser import parse_product_metadata
from app.modules.product_page_fetch import InMemoryHtmlFetcher
from app.modules.product_verification import verify_product_page
from app.modules.verification_bridge import verify_with_product_page_metadata
from app.schemas import CandidateProduct, CandidateSignals, IdentifiedCard


FIXTURES = Path(__file__).resolve().parent / "fixtures"


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


def test_verification_uses_parsed_metadata_to_improve_confidence() -> None:
    url = "https://provider.example/candidate-bridge"
    html = (FIXTURES / "product_page_complete.html").read_text()
    candidate = CandidateProduct(
        candidate_name="Pikachu",
        raw_title="Pikachu listing",
        set_name=None,
        card_number=None,
        variant=None,
        promo=False,
        source="discovery_input",
        candidate_url=url,
        confidence_signals=CandidateSignals(),
    )

    direct_result = verify_product_page(_identified_card(), [candidate])
    assert direct_result.verified is False

    fetcher = InMemoryHtmlFetcher({url: html})
    bridged_result = verify_with_product_page_metadata(_identified_card(), [candidate], fetcher)
    assert bridged_result.verified is True
    assert bridged_result.verified_product_url == url


def test_invalid_or_incomplete_product_html_does_not_verify_match() -> None:
    url = "https://provider.example/candidate-incomplete"
    html = (FIXTURES / "product_page_incomplete.html").read_text()
    candidate = CandidateProduct(
        candidate_name="Pikachu",
        raw_title="Pikachu listing",
        set_name=None,
        card_number=None,
        variant=None,
        promo=False,
        source="discovery_input",
        candidate_url=url,
        confidence_signals=CandidateSignals(),
    )

    fetcher = InMemoryHtmlFetcher({url: html})
    result = verify_with_product_page_metadata(_identified_card(), [candidate], fetcher)

    assert result.verified is False
    assert result.verified_product_url is None


def test_urls_are_only_used_when_present_in_candidate_input() -> None:
    html = (FIXTURES / "product_page_complete.html").read_text()
    parsed = parse_product_metadata(html)

    candidate = CandidateProduct(
        candidate_name="Pikachu",
        raw_title="Pikachu listing",
        set_name=None,
        card_number=None,
        variant=None,
        promo=False,
        source="discovery_input",
        candidate_url=None,
        confidence_signals=CandidateSignals(),
    )

    # even with parseable metadata, no candidate URL means no verification path
    result = verify_product_page(
        _identified_card(),
        [candidate],
        parsed_metadata_by_url={"https://provider.example/not-linked": parsed},
    )

    assert result.verified is False
    assert result.verified_product_url is None
