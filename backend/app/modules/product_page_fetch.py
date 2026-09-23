from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from app.modules.product_metadata_parser import parse_product_metadata
from app.schemas import CandidateProduct, ProductPageMetadata


class ProductPageFetcher(Protocol):
    def fetch_html(self, url: str) -> str:
        """Fetch product page HTML for a discovered candidate URL."""


class InMemoryHtmlFetcher:
    """Deterministic HTML fetcher for tests and non-network pipeline wiring."""

    def __init__(self, html_by_url: dict[str, str]) -> None:
        self._html_by_url = dict(html_by_url)

    def fetch_html(self, url: str) -> str:
        return self._html_by_url[url]


@dataclass
class HttpxFetcher:
    timeout_seconds: float = 10.0

    def fetch_html(self, url: str) -> str:
        with httpx.Client(timeout=self.timeout_seconds, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text


class PlaywrightFetcher:
    """Placeholder adapter for future Playwright integration."""

    def fetch_html(self, url: str) -> str:
        raise NotImplementedError("PlaywrightFetcher is not implemented in this MVP step.")


def fetch_and_parse_product_page(
    candidate: CandidateProduct,
    fetcher: ProductPageFetcher,
) -> ProductPageMetadata | None:
    """Fetch and parse metadata for a candidate page.

    Only candidate URLs already present in candidate input are used.
    """
    if not candidate.candidate_url:
        return None

    html = fetcher.fetch_html(candidate.candidate_url)
    return parse_product_metadata(html)
