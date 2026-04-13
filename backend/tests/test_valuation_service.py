from app.modules.pricing_engine import PricingError
from app.modules.valuation_service import valuate_candidate_from_rows
from app.schemas import ListingRow


def _row(price: float | None, flagged: bool = False) -> ListingRow:
    return ListingRow(
        source_candidate_url="https://provider.example/result-1",
        price=price,
        flagged_anomaly=flagged,
    )


def test_happy_path_with_five_plus_valid_rows() -> None:
    rows = [_row(1), _row(2), _row(3), _row(4), _row(5), _row(6)]
    result = valuate_candidate_from_rows("https://provider.example/result-1", rows, True)

    assert result.pricing_method == "verified_filtered_avg5"
    assert result.distinct_prices_used == [1, 2, 3, 4, 5]
    assert result.average_price == 3.0


def test_duplicate_price_removal() -> None:
    rows = [_row(2), _row(2), _row(3)]
    result = valuate_candidate_from_rows("https://provider.example/result-1", rows, True)
    assert result.distinct_prices_used == [2, 3]


def test_anomaly_exclusion() -> None:
    rows = [_row(1), _row(999, flagged=True), _row(2)]
    result = valuate_candidate_from_rows("https://provider.example/result-1", rows, True)
    assert result.distinct_prices_used == [1, 2]


def test_fewer_than_five_valid_rows() -> None:
    rows = [_row(10), _row(12)]
    result = valuate_candidate_from_rows("https://provider.example/result-1", rows, True)
    assert result.distinct_prices_used == [10, 12]
    assert result.average_price == 11.0


def test_no_valid_rows() -> None:
    try:
        valuate_candidate_from_rows("https://provider.example/result-1", [_row(None), _row(None)], True)
    except PricingError:
        assert True
        return

    raise AssertionError("Expected PricingError")


def test_fallback_labeling_when_not_demonstrable() -> None:
    rows = [_row(4), _row(6)]
    result = valuate_candidate_from_rows("https://provider.example/result-1", rows, False)
    assert result.pricing_method == "nm_visible_benchmark"
    assert any("Fallback applied" in note for note in result.notes)
