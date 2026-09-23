from __future__ import annotations

from app.modules.product_page_fetch import ProductPageFetcher


def retrieve_candidate_html(
    candidate_url: str,
    mode: str,
    fetcher: ProductPageFetcher | None = None,
    provided_html: str | None = None,
) -> tuple[str, str]:
    """Retrieve candidate HTML in deterministic, auditable modes.

    Returns: (html, retrieval_mode)
    """
    if mode == "provided":
        if provided_html is None:
            raise ValueError("provided_html is required when mode='provided'.")
        return provided_html, "provided"

    if mode == "fetched":
        if fetcher is None:
            raise ValueError("A fetch adapter is required when mode='fetched'.")
        return fetcher.fetch_html(candidate_url), "fetched"

    raise ValueError("Unsupported retrieval mode.")
