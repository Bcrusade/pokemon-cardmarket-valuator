from __future__ import annotations

import re

from app.schemas import ProductPageMetadata

_CARD_NUMBER_RE = re.compile(r"\b\d{1,3}/\d{1,3}\b")
_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_SET_RE = re.compile(r"data-set-name=\"([^\"]+)\"", re.IGNORECASE)
_SET_FALLBACK_RE = re.compile(r"<span[^>]*class=\"[^\"]*set-name[^\"]*\"[^>]*>(.*?)</span>", re.IGNORECASE | re.DOTALL)


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()


def _detect_variant(html: str) -> str | None:
    lowered = html.lower()
    if "1st edition" in lowered:
        return "1st Edition"
    if "unlimited" in lowered:
        return "Unlimited"
    if "reverse holo" in lowered:
        return "Reverse Holo"
    return None


def parse_product_metadata(html: str) -> ProductPageMetadata:
    h1 = _H1_RE.search(html)
    set_match = _SET_RE.search(html) or _SET_FALLBACK_RE.search(html)
    number_match = _CARD_NUMBER_RE.search(html)

    product_title = _strip_tags(h1.group(1)) if h1 else None
    set_name = _strip_tags(set_match.group(1)) if set_match else None

    fragment_parts = []
    if product_title:
        fragment_parts.append(product_title)
    if set_name:
        fragment_parts.append(set_name)
    if number_match:
        fragment_parts.append(number_match.group(0))

    return ProductPageMetadata(
        product_title=product_title,
        set_name=set_name,
        card_number=number_match.group(0) if number_match else None,
        variant=_detect_variant(html),
        raw_fragment=" | ".join(fragment_parts) if fragment_parts else None,
    )
