from __future__ import annotations

from app.schemas import ListingRow, PriceInput


ANOMALY_PRICE_MIN = 0.01
ANOMALY_PRICE_MAX = 10000.0


def exclude_anomalies(prices: list[PriceInput]) -> list[PriceInput]:
    """Basic anomaly filter using pre-flagged rows."""
    return [price for price in prices if not price.flagged_anomaly]


def flag_listing_row_anomalies(rows: list[ListingRow]) -> list[ListingRow]:
    """Deterministically mark listing row anomalies without dropping audit data."""
    flagged_rows: list[ListingRow] = []
    for row in rows:
        is_anomaly = False
        if row.price is None:
            is_anomaly = True
        elif row.price < ANOMALY_PRICE_MIN or row.price > ANOMALY_PRICE_MAX:
            is_anomaly = True
        if any(flag.lower() in {"non-comparable", "damaged-lot"} for flag in row.flags):
            is_anomaly = True

        flagged_rows.append(row.model_copy(update={"flagged_anomaly": is_anomaly}))
    return flagged_rows
