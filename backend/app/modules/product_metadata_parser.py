from __future__ import annotations

import re

from app.schemas import ProductPageMetadata

_CARD_NUMBER_RE = re.compile(r"\b\d{1,3}/\d{1,3}\b")
_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_SET_RE = re.compile(r"data-set-name=\"([^\"]+)\"", re.IGNORECASE)
_SET_FALLBACK_RE = re.compile(r"<span[^>]*class=\"[^\"]*set-name[^\"]*\"[^>]*>(.*?)</span>", re.IGNORECASE | re.DOTALL)
_BREADCRUMB_SET_RE = re.compile(
    r"<nav[^>]*class=\"[^\"]*breadcrumb[^\"]*\"[^>]*>.*?<a[^>]*>(.*?)</a>.*?</nav>",
    re.IGNORECASE | re.DOTALL,
)
_EXPANSION_SET_RE = re.compile(
    r"<[^>]*class=\"[^\"]*(?:expansion-name|product-expansion)[^\"]*\"[^>]*>(.*?)</[^>]+>",
    re.IGNORECASE | re.DOTALL,
)
_LABEL_VALUE_RE = re.compile(
    r"<dt[^>]*>\s*(Set|Card Number|Number|No\.|Version|Variant)\s*</dt>\s*<dd[^>]*>(.*?)</dd>",
    re.IGNORECASE | re.DOTALL,
)


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()


def _detect_variant(html: str) -> str | None:
    for label, value in _LABEL_VALUE_RE.findall(html):
        normalized = _strip_tags(label).lower()
        if normalized in {"version", "variant"}:
            cleaned = _strip_tags(value)
            return cleaned or None

    lowered = html.lower()
    if "1st edition" in lowered:
        return "1st Edition"
    if "unlimited" in lowered:
        return "Unlimited"
    if "reverse holo" in lowered:
        return "Reverse Holo"
    return None


def _extract_set_name(html: str) -> str | None:
    set_match = _SET_RE.search(html) or _SET_FALLBACK_RE.search(html) or _BREADCRUMB_SET_RE.search(html) or _EXPANSION_SET_RE.search(html)
    if set_match:
        cleaned = _strip_tags(set_match.group(1))
        if cleaned:
            return cleaned

    for label, value in _LABEL_VALUE_RE.findall(html):
        if _strip_tags(label).lower() == "set":
            cleaned = _strip_tags(value)
            return cleaned or None
    return None


def _extract_card_number(html: str) -> str | None:
    for label, value in _LABEL_VALUE_RE.findall(html):
        if _strip_tags(label).lower() in {"card number", "number", "no."}:
            direct = _CARD_NUMBER_RE.search(_strip_tags(value))
            if direct:
                return direct.group(0)
    number_match = _CARD_NUMBER_RE.search(html)
    return number_match.group(0) if number_match else None


def parse_product_metadata(html: str) -> ProductPageMetadata:
    h1 = _H1_RE.search(html)
    product_title = _strip_tags(h1.group(1)) if h1 else None
    set_name = _extract_set_name(html)
    card_number = _extract_card_number(html)
    variant = _detect_variant(html)

    fragment_parts = []
    if product_title:
        fragment_parts.append(product_title)
    if set_name:
        fragment_parts.append(set_name)
    if card_number:
        fragment_parts.append(card_number)
    if variant:
        fragment_parts.append(variant)

    return ProductPageMetadata(
        product_title=product_title,
        set_name=set_name,
        card_number=card_number,
        variant=variant,
        raw_fragment=" | ".join(fragment_parts) if fragment_parts else None,
    )
