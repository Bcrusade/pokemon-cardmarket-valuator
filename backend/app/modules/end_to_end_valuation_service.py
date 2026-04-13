from __future__ import annotations

from uuid import UUID

from app.modules.anomaly_filter import flag_listing_row_anomalies
from app.modules.listing_row_parser import parse_listing_rows
from app.modules.product_metadata_parser import parse_product_metadata
from app.modules.product_verification import verify_product_page
from app.modules.valuation_service import valuate_candidate_from_rows
from app.schemas import CandidateProduct, FullEvaluationResult, ListingRow, ListingSummary
from app.store import InMemoryJobStore


def _get_candidate_for_url(store: InMemoryJobStore, job_id: UUID, candidate_url: str) -> CandidateProduct | None:
    job = store.get_job(job_id)
    for item in job.metadata.get("candidate_discovery_normalized", []):
        if item.get("candidate_url") == candidate_url:
            return CandidateProduct(**item)
    return None


def run_full_evaluation(
    store: InMemoryJobStore,
    job_id: UUID,
    candidate_url: str,
) -> FullEvaluationResult:
    candidate = _get_candidate_for_url(store, job_id, candidate_url)
    if candidate is None:
        raise ValueError("Unknown candidate URL for this job.")

    identified = store.get_identified_card_context(job_id, candidate_url)
    if identified is None:
        raise ValueError("Missing original identified card context for candidate URL.")

    stored_html = store.get_candidate_html(job_id, candidate_url)
    if not stored_html:
        raise ValueError("Missing stored HTML for candidate URL.")

    metadata = parse_product_metadata(stored_html)

    verification = verify_product_page(
        identified,
        [candidate],
        parsed_metadata_by_url={candidate_url: metadata},
    )

    if not verification.verified:
        return FullEvaluationResult(
            candidate_url=candidate_url,
            verification=verification,
            parsed_metadata=metadata,
            listing_summary=ListingSummary(total_rows=0, anomaly_rows=0, priced_rows=0),
            pricing=None,
            method_used="verification_failed",
            notes=["Stopped before pricing because verification failed."],
        )

    job = store.get_job(job_id)
    stored_rows = job.metadata.get("parsed_listing_rows", {}).get(candidate_url)
    rows: list[ListingRow]
    if stored_rows:
        rows = [ListingRow(**row) for row in stored_rows]
    else:
        rows = parse_listing_rows(stored_html, candidate_url)
        rows = flag_listing_row_anomalies(rows)

    anomaly_rows = len([r for r in rows if r.flagged_anomaly])
    priced_rows = len([r for r in rows if r.price is not None and not r.flagged_anomaly])

    if not rows:
        raise ValueError("No listing rows found for candidate URL.")

    if priced_rows == 0:
        raise ValueError("No usable non-anomalous listing rows available for pricing.")

    demonstrable = store.get_verified_filtered_context(job_id, candidate_url)
    valuation = valuate_candidate_from_rows(
        candidate_url=candidate_url,
        rows=rows,
        verified_filtered_demonstrable=demonstrable,
    )

    return FullEvaluationResult(
        candidate_url=candidate_url,
        verification=verification,
        parsed_metadata=metadata,
        listing_summary=ListingSummary(total_rows=len(rows), anomaly_rows=anomaly_rows, priced_rows=priced_rows),
        pricing=valuation,
        method_used=valuation.pricing_method,
        notes=["Full deterministic pipeline executed from stored candidate context."],
    )
