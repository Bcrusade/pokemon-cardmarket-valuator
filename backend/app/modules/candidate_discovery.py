from __future__ import annotations

import re

from app.schemas import CandidateProduct, CandidateSignals, DiscoveryCandidateInput

_CARD_NUMBER_RE = re.compile(r"\b\d{1,3}/\d{1,3}\b")


def _detect_variant(title: str) -> str | None:
    lowered = title.lower()
    if "1st edition" in lowered:
        return "1st Edition"
    if "unlimited" in lowered:
        return "Unlimited"
    return None


def _normalize_candidate_name(title: str) -> str:
    # Deterministic minimal normalization: keep text before first separator if present.
    for separator in [" - ", " | ", " ("]:
        if separator in title:
            return title.split(separator, 1)[0].strip()
    return title.strip()


def normalize_discovery_input(item: DiscoveryCandidateInput) -> CandidateProduct:
    number_in_title = _CARD_NUMBER_RE.search(item.title)

    return CandidateProduct(
        candidate_name=_normalize_candidate_name(item.title),
        raw_title=item.title,
        set_name=item.extracted_set_name,
        card_number=item.extracted_card_number or (number_in_title.group(0) if number_in_title else None),
        variant=_detect_variant(item.title),
        promo=None,
        source="discovery_input",
        candidate_url=item.url,
        notes=item.notes,
        confidence_signals=CandidateSignals(),
    )


def normalize_discovery_batch(items: list[DiscoveryCandidateInput]) -> list[CandidateProduct]:
    return [normalize_discovery_input(item) for item in items]
