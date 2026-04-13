from pathlib import Path

from app.modules.product_metadata_parser import parse_product_metadata


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_parse_product_metadata_from_fixture_html() -> None:
    html = (FIXTURES / "product_page_complete.html").read_text()
    metadata = parse_product_metadata(html)

    assert metadata.product_title == "Pikachu"
    assert metadata.set_name == "Base Set"
    assert metadata.card_number == "58/102"
    assert metadata.variant == "Unlimited"
    assert metadata.raw_fragment is not None


def test_missing_fields_stay_missing() -> None:
    html = (FIXTURES / "product_page_incomplete.html").read_text()
    metadata = parse_product_metadata(html)

    assert metadata.set_name is None
    assert metadata.card_number is None
    assert metadata.variant is None


def test_parser_does_not_fabricate_card_number_or_variant() -> None:
    html = "<html><body><h1>Pikachu</h1><span>Base Set</span></body></html>"
    metadata = parse_product_metadata(html)

    assert metadata.card_number is None
    assert metadata.variant is None
