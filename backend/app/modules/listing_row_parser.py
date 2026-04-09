from __future__ import annotations

import re

from app.schemas import ListingRow

_ROW_RE = re.compile(r"<tr[^>]*class=\"[^\"]*listing-row[^\"]*\"[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
_PRICE_RE = re.compile(r"data-price=\"([0-9]+(?:\.[0-9]+)?)\"", re.IGNORECASE)
_CONDITION_RE = re.compile(r"data-condition=\"([^\"]+)\"", re.IGNORECASE)
_LANGUAGE_RE = re.compile(r"data-language=\"([^\"]+)\"", re.IGNORECASE)
_SELLER_RE = re.compile(r"data-seller=\"([^\"]+)\"", re.IGNORECASE)
_QUANTITY_RE = re.compile(r"data-quantity=\"([0-9]+)\"", re.IGNORECASE)
_FLAGS_RE = re.compile(r"data-flags=\"([^\"]+)\"", re.IGNORECASE)


def _parse_flags(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_listing_rows(html: str, source_candidate_url: str) -> list[ListingRow]:
    rows: list[ListingRow] = []
    for fragment in _ROW_RE.findall(html):
        price_match = _PRICE_RE.search(fragment)
        condition_match = _CONDITION_RE.search(fragment)
        language_match = _LANGUAGE_RE.search(fragment)
        seller_match = _SELLER_RE.search(fragment)
        quantity_match = _QUANTITY_RE.search(fragment)
        flags_match = _FLAGS_RE.search(fragment)

        rows.append(
            ListingRow(
                source_candidate_url=source_candidate_url,
                price=float(price_match.group(1)) if price_match else None,
                condition=condition_match.group(1).strip() if condition_match else None,
                language=language_match.group(1).strip() if language_match else None,
                seller_name=seller_match.group(1).strip() if seller_match else None,
                quantity=int(quantity_match.group(1)) if quantity_match else None,
                flags=_parse_flags(flags_match.group(1) if flags_match else None),
                raw_fragment=fragment.strip(),
            )
        )
    return rows
