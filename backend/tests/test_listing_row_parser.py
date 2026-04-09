from pathlib import Path

from app.modules.listing_row_parser import parse_listing_rows


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_parse_valid_listing_rows_from_fixture_html() -> None:
    html = (FIXTURES / "listings_complete.html").read_text()
    rows = parse_listing_rows(html, "https://provider.example/result-1")

    assert len(rows) == 2
    assert rows[0].price == 4.5
    assert rows[0].condition == "NM"
    assert rows[0].language == "English"
    assert rows[0].seller_name == "sellerA"
    assert rows[0].quantity == 2


def test_missing_fields_stay_missing_and_not_fabricated() -> None:
    html = (FIXTURES / "listings_incomplete.html").read_text()
    rows = parse_listing_rows(html, "https://provider.example/result-1")

    assert len(rows) == 1
    assert rows[0].language is None
    assert rows[0].quantity is None


def test_reject_invalid_incomplete_listing_html_by_returning_no_rows() -> None:
    html = (FIXTURES / "listings_malformed.html").read_text()
    rows = parse_listing_rows(html, "https://provider.example/result-1")
    assert rows == []
