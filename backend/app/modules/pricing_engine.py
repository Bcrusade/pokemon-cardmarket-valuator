from __future__ import annotations

from app.modules.anomaly_filter import exclude_anomalies
from app.schemas import PriceInput, PriceOutput


class PricingError(ValueError):
    pass


def _distinct_preserve_order(values: list[float]) -> list[float]:
    seen: set[float] = set()
    distinct: list[float] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        distinct.append(value)
    return distinct


def compute_price(
    prices: list[PriceInput],
    fallback_mode: bool = False,
) -> PriceOutput:
    """Compute deterministic card price from listing rows.

    Steps:
    1) remove flagged anomalies
    2) remove identical duplicate prices while preserving order
    3) take first 5 distinct prices
    4) average available prices
    5) label method depending on fallback_mode
    """
    cleaned = exclude_anomalies(prices)
    distinct_prices = _distinct_preserve_order([p.amount for p in cleaned])
    selected = distinct_prices[:5]

    if not selected:
        raise PricingError("No valid prices available after filtering.")

    average = round(sum(selected) / len(selected), 2)
    method = "nm_visible_benchmark" if fallback_mode else "verified_filtered_avg5"

    notes = []
    if fallback_mode:
        notes.append(
            "Fallback applied: exact filter verification was not demonstrable; "
            "used visible NM listings benchmark."
        )

    return PriceOutput(
        pricing_method=method,
        average_price=average,
        selected_prices=selected,
        notes=notes,
    )
