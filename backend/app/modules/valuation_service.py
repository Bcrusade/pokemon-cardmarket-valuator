from __future__ import annotations

from app.modules.pricing_engine import PricingError, compute_price
from app.schemas import ListingRow, PriceInput, ValuationResult


def valuate_candidate_from_rows(
    candidate_url: str,
    rows: list[ListingRow],
    verified_filtered_demonstrable: bool,
) -> ValuationResult:
    """Compute deterministic valuation from already parsed listing rows."""
    priced_rows = [row for row in rows if row.price is not None]
    if not priced_rows:
        raise PricingError("No usable listing rows with prices.")

    price_inputs = [
        PriceInput(amount=row.price, flagged_anomaly=row.flagged_anomaly)  # type: ignore[arg-type]
        for row in priced_rows
    ]

    pricing = compute_price(
        price_inputs,
        fallback_mode=not verified_filtered_demonstrable,
    )

    excluded_rows_count = len(rows) - len(pricing.selected_prices)

    notes = list(pricing.notes)
    if excluded_rows_count > 0:
        notes.append(f"Excluded {excluded_rows_count} rows due to anomalies, duplicates, or missing price.")

    return ValuationResult(
        candidate_url=candidate_url,
        pricing_method=pricing.pricing_method,
        distinct_prices_used=pricing.selected_prices,
        average_price=pricing.average_price,
        excluded_rows_count=excluded_rows_count,
        notes=notes,
    )
