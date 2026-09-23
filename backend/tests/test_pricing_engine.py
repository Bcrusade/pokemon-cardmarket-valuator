from app.modules.pricing_engine import PricingError, compute_price
from app.schemas import PriceInput


def test_duplicate_identical_price_removal() -> None:
    result = compute_price(
        [
            PriceInput(amount=2.0),
            PriceInput(amount=2.0),
            PriceInput(amount=3.0),
        ]
    )
    assert result.selected_prices == [2.0, 3.0]


def test_average_of_first_five_distinct_prices() -> None:
    result = compute_price(
        [
            PriceInput(amount=1.0),
            PriceInput(amount=2.0),
            PriceInput(amount=3.0),
            PriceInput(amount=4.0),
            PriceInput(amount=5.0),
            PriceInput(amount=6.0),
        ]
    )
    assert result.selected_prices == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert result.average_price == 3.0


def test_fallback_mode_labels_result() -> None:
    result = compute_price([PriceInput(amount=10.0)], fallback_mode=True)
    assert result.pricing_method == "nm_visible_benchmark"
    assert any("Fallback applied" in note for note in result.notes)


def test_anomaly_exclusion() -> None:
    result = compute_price(
        [
            PriceInput(amount=1.0),
            PriceInput(amount=999.0, flagged_anomaly=True),
            PriceInput(amount=2.0),
        ]
    )
    assert result.selected_prices == [1.0, 2.0]
    assert result.average_price == 1.5


def test_no_valid_price_raises() -> None:
    try:
        compute_price([PriceInput(amount=100.0, flagged_anomaly=True)])
    except PricingError:
        assert True
        return

    raise AssertionError("Expected PricingError")
