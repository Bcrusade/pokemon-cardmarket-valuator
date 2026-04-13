from __future__ import annotations

import re

from app.schemas import ListingRow

_ROW_RE = re.compile(r"(<tr[^>]*class=\"[^\"]*listing-row[^\"]*\"[^>]*>.*?</tr>)", re.IGNORECASE | re.DOTALL)
_ROW_OPENING_RE = re.compile(r"<tr[^>]*class=\"[^\"]*listing-row[^\"]*\"[^>]*>", re.IGNORECASE | re.DOTALL)
_PRICE_RE = re.compile(r"data-price=\"([0-9]+(?:\.[0-9]+)?)\"", re.IGNORECASE)
_PRICE_TEXT_RE = re.compile(r"(?:€|EUR)?\s*([0-9]+(?:[.,][0-9]{1,2})?)", re.IGNORECASE)
_CONDITION_RE = re.compile(r"data-condition=\"([^\"]+)\"", re.IGNORECASE)
_LANGUAGE_RE = re.compile(r"data-language=\"([^\"]+)\"", re.IGNORECASE)
_SELLER_RE = re.compile(r"data-seller=\"([^\"]+)\"", re.IGNORECASE)
_QUANTITY_RE = re.compile(r"data-quantity=\"([0-9]+)\"", re.IGNORECASE)
_CONDITION_TEXT_RE = re.compile(r"<[^>]*class=\"[^\"]*condition[^\"]*\"[^>]*>(.*?)</[^>]+>", re.IGNORECASE | re.DOTALL)
_LANGUAGE_TEXT_RE = re.compile(r"<[^>]*class=\"[^\"]*language[^\"]*\"[^>]*>(.*?)</[^>]+>", re.IGNORECASE | re.DOTALL)
_SELLER_TEXT_RE = re.compile(r"<[^>]*class=\"[^\"]*(?:seller|seller-name)[^\"]*\"[^>]*>(.*?)</[^>]+>", re.IGNORECASE | re.DOTALL)
_QUANTITY_TEXT_RE = re.compile(r"<[^>]*class=\"[^\"]*(?:amount|quantity)[^\"]*\"[^>]*>(.*?)</[^>]+>", re.IGNORECASE | re.DOTALL)
_FLAGS_RE = re.compile(r"data-flags=\"([^\"]+)\"", re.IGNORECASE)


def _parse_flags(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()


def _extract_float(fragment: str) -> float | None:
    price_match = _PRICE_RE.search(fragment)
    if price_match:
        return float(price_match.group(1))

    text_price = _PRICE_TEXT_RE.search(_strip_tags(fragment))
    if not text_price:
        return None
    return float(text_price.group(1).replace(",", "."))


def _extract_text(fragment: str, data_regex: re.Pattern[str], html_regex: re.Pattern[str]) -> str | None:
    data_match = data_regex.search(fragment)
    if data_match:
        cleaned = data_match.group(1).strip()
        if cleaned:
            return cleaned

    html_match = html_regex.search(fragment)
    if html_match:
        cleaned = _strip_tags(html_match.group(1))
        if cleaned:
            return cleaned
    return None


def _extract_quantity(fragment: str) -> int | None:
    quantity_match = _QUANTITY_RE.search(fragment)
    if quantity_match:
        return int(quantity_match.group(1))

    text_match = _QUANTITY_TEXT_RE.search(fragment)
    if not text_match:
        return None
    text_value = _strip_tags(text_match.group(1))
    digit_match = re.search(r"\d+", text_value)
    if not digit_match:
        return None
    return int(digit_match.group(0))


def parse_listing_rows(html: str, source_candidate_url: str) -> list[ListingRow]:
    rows: list[ListingRow] = []
    row_fragments = _ROW_RE.findall(html)

    # Support self-closing / minimal row tags that still contain listing attributes.
    for opening_tag in _ROW_OPENING_RE.findall(html):
        if "/>" in opening_tag:
            row_fragments.append(opening_tag)

    for fragment in row_fragments:
        flags_match = _FLAGS_RE.search(fragment)

        rows.append(
            ListingRow(
                source_candidate_url=source_candidate_url,
                price=_extract_float(fragment),
                condition=_extract_text(fragment, _CONDITION_RE, _CONDITION_TEXT_RE),
                language=_extract_text(fragment, _LANGUAGE_RE, _LANGUAGE_TEXT_RE),
                seller_name=_extract_text(fragment, _SELLER_RE, _SELLER_TEXT_RE),
                quantity=_extract_quantity(fragment),
                flags=_parse_flags(flags_match.group(1) if flags_match else None),
                raw_fragment=fragment.strip(),
            )
        )
    return rows
