from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.schemas import CandidateProduct, FullEvaluationResult, IdentifiedCard, JobImageResponse, JobRecord, JobStatus, ListingRow, ProductPageMetadata, ValuationResult


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[UUID, JobRecord] = {}

    def create_job(self, target_language: str, minimum_condition: str) -> JobRecord:
        job = JobRecord(
            job_id=uuid4(),
            status=JobStatus.CREATED,
            target_language=target_language,
            minimum_condition=minimum_condition,
            created_at=datetime.now(timezone.utc),
            metadata={
                "candidate_discovery_raw": [],
                "candidate_discovery_normalized": [],
                "stored_product_html": {},
                "parsed_product_metadata": {},
                "parsed_listing_rows": {},
                "valuations": {},
                "full_evaluations": {},
                "identified_card_context": {},
                "verified_filtered_context": {},
            },
        )
        self._jobs[job.job_id] = job
        return job

    def get_job(self, job_id: UUID) -> JobRecord:
        return self._jobs[job_id]

    def add_image(self, job_id: UUID, filename: str) -> JobImageResponse:
        image = JobImageResponse(image_id=uuid4(), filename=filename)
        job = self.get_job(job_id)
        job.images.append(image)
        job.status = JobStatus.IMAGES_UPLOADED
        return image

    def save_discovery_candidates(
        self,
        job_id: UUID,
        raw_items: list[dict],
        normalized: list[CandidateProduct],
    ) -> None:
        job = self.get_job(job_id)
        job.metadata.setdefault("candidate_discovery_raw", [])
        job.metadata.setdefault("candidate_discovery_normalized", [])
        job.metadata["candidate_discovery_raw"].extend(raw_items)
        job.metadata["candidate_discovery_normalized"].extend([item.model_dump() for item in normalized])

    def known_candidate_urls(self, job_id: UUID) -> set[str]:
        job = self.get_job(job_id)
        normalized = job.metadata.get("candidate_discovery_normalized", [])
        return {item.get("candidate_url") for item in normalized if item.get("candidate_url")}

    def save_candidate_html(
        self,
        job_id: UUID,
        candidate_url: str,
        html: str,
        retrieval_mode: str,
    ) -> None:
        job = self.get_job(job_id)
        job.metadata.setdefault("stored_product_html", {})
        job.metadata["stored_product_html"][candidate_url] = {
            "html": html,
            "retrieval_mode": retrieval_mode,
            "source": "product_page_retrieval_service",
        }

    def get_candidate_html(self, job_id: UUID, candidate_url: str) -> str | None:
        job = self.get_job(job_id)
        return job.metadata.get("stored_product_html", {}).get(candidate_url, {}).get("html")


    def save_identified_card_context(
        self,
        job_id: UUID,
        candidate_url: str,
        identified_card: IdentifiedCard,
    ) -> None:
        job = self.get_job(job_id)
        job.metadata.setdefault("identified_card_context", {})
        job.metadata["identified_card_context"][candidate_url] = identified_card.model_dump()

    def get_identified_card_context(self, job_id: UUID, candidate_url: str) -> IdentifiedCard | None:
        job = self.get_job(job_id)
        raw = job.metadata.get("identified_card_context", {}).get(candidate_url)
        if not raw:
            return None
        return IdentifiedCard(**raw)

    def save_verified_filtered_context(
        self,
        job_id: UUID,
        candidate_url: str,
        demonstrable: bool,
    ) -> None:
        job = self.get_job(job_id)
        job.metadata.setdefault("verified_filtered_context", {})
        job.metadata["verified_filtered_context"][candidate_url] = demonstrable

    def get_verified_filtered_context(self, job_id: UUID, candidate_url: str) -> bool:
        job = self.get_job(job_id)
        return bool(job.metadata.get("verified_filtered_context", {}).get(candidate_url, False))


    def save_parsed_product_metadata(
        self,
        job_id: UUID,
        metadata_by_url: dict[str, ProductPageMetadata],
    ) -> None:
        job = self.get_job(job_id)
        job.metadata.setdefault("parsed_product_metadata", {})
        for url, metadata in metadata_by_url.items():
            job.metadata["parsed_product_metadata"][url] = metadata.model_dump()

    def save_parsed_listing_rows(
        self,
        job_id: UUID,
        rows_by_url: dict[str, list[ListingRow]],
    ) -> None:
        job = self.get_job(job_id)
        job.metadata.setdefault("parsed_listing_rows", {})
        for url, rows in rows_by_url.items():
            job.metadata["parsed_listing_rows"][url] = [row.model_dump() for row in rows]

    def save_valuation(
        self,
        job_id: UUID,
        valuation: ValuationResult,
    ) -> None:
        job = self.get_job(job_id)
        job.metadata.setdefault("valuations", {})
        job.metadata["valuations"][valuation.candidate_url] = valuation.model_dump()

    def save_full_evaluation(
        self,
        job_id: UUID,
        evaluation: FullEvaluationResult,
    ) -> None:
        job = self.get_job(job_id)
        job.metadata.setdefault("full_evaluations", {})
        job.metadata["full_evaluations"][evaluation.candidate_url] = evaluation.model_dump()


store = InMemoryJobStore()
