from __future__ import annotations


def parse_visible_listings(_verified_product_url: str, _minimum_condition: str) -> list[dict]:
    """Stub parser returning deterministic visible listings scaffold."""
    return [
        {"price": 4.0, "flagged_anomaly": False},
        {"price": 4.0, "flagged_anomaly": False},
        {"price": 5.0, "flagged_anomaly": False},
        {"price": 6.0, "flagged_anomaly": False},
        {"price": 999.0, "flagged_anomaly": True},
        {"price": 7.0, "flagged_anomaly": False},
        {"price": 8.0, "flagged_anomaly": False},
    ]
