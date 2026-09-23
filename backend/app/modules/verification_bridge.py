from __future__ import annotations

from app.modules.product_page_fetch import ProductPageFetcher, fetch_and_parse_product_page
from app.modules.product_verification import verify_product_page
from app.schemas import CandidateProduct, IdentifiedCard, ProductPageMetadata, VerificationResult


def build_parsed_metadata_lookup(
    candidates: list[CandidateProduct],
    fetcher: ProductPageFetcher,
) -> dict[str, ProductPageMetadata]:
    parsed: dict[str, ProductPageMetadata] = {}
    for candidate in candidates:
        if not candidate.candidate_url:
            continue
        metadata = fetch_and_parse_product_page(candidate, fetcher)
        if metadata is not None:
            parsed[candidate.candidate_url] = metadata
    return parsed


def verify_with_product_page_metadata(
    card: IdentifiedCard,
    candidates: list[CandidateProduct],
    fetcher: ProductPageFetcher,
) -> VerificationResult:
    metadata_lookup = build_parsed_metadata_lookup(candidates, fetcher)
    return verify_product_page(card, candidates, parsed_metadata_by_url=metadata_lookup)
