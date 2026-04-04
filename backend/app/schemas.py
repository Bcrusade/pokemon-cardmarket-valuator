from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    CREATED = "created"
    IMAGES_UPLOADED = "images_uploaded"
    ANALYZED = "analyzed"


class CreateJobRequest(BaseModel):
    target_language: str = Field(default="English")
    minimum_condition: str = Field(default="NM")


class JobImageResponse(BaseModel):
    image_id: UUID
    filename: str


class CreateJobResponse(BaseModel):
    job_id: UUID
    status: JobStatus


class CandidateSignals(BaseModel):
    name_exact: bool = False
    set_exact: bool = False
    number_exact: bool = False
    variant_compatible: bool = False
    promo_compatible: bool = False


class CandidateProduct(BaseModel):
    candidate_name: str
    raw_title: str
    set_name: str | None = None
    card_number: str | None = None
    variant: str | None = None
    promo: bool | None = None
    source: Literal["cardmarket_search_stub", "external_candidate_feed", "discovery_input"] = "cardmarket_search_stub"
    candidate_url: str | None = None
    notes: list[str] = Field(default_factory=list)
    confidence_signals: CandidateSignals = Field(default_factory=CandidateSignals)


class DiscoveryCandidateInput(BaseModel):
    title: str
    url: str | None = None
    source: str
    extracted_set_name: str | None = None
    extracted_card_number: str | None = None
    notes: list[str] = Field(default_factory=list)


class DiscoveryIngestRequest(BaseModel):
    results: list[DiscoveryCandidateInput]


class DiscoveryIngestResponse(BaseModel):
    ingested_count: int
    candidates: list[CandidateProduct]




class ProductPageMetadata(BaseModel):
    product_title: str | None = None
    set_name: str | None = None
    card_number: str | None = None
    variant: str | None = None
    raw_fragment: str | None = None


class CandidateHtmlInput(BaseModel):
    candidate_url: str
    html: str


class CandidateHtmlFetchRequest(BaseModel):
    candidate_url: str
    retrieval_mode: Literal["provided", "fetched"]
    provided_html: str | None = None


class CandidateHtmlFetchResponse(BaseModel):
    candidate_url: str
    retrieval_mode: Literal["provided", "fetched"]
    stored: bool
    html_length: int


class ParseCandidateHtmlRequest(BaseModel):
    pages: list[CandidateHtmlInput]


class ParseCandidateHtmlResponse(BaseModel):
    parsed_count: int
    parsed_metadata: dict[str, ProductPageMetadata]


class IdentifiedCard(BaseModel):
    image_id: UUID
    card_name: str
    set_name: str
    card_number: str
    variant: str
    promo: bool
    confidence: float
    notes: list[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    verified: bool
    verified_product_url: str | None = None
    reason: str
    best_match_score: float = 0.0
    threshold_used: float = 0.9


class ListingRow(BaseModel):
    source_candidate_url: str
    price: float | None = None
    condition: str | None = None
    language: str | None = None
    seller_name: str | None = None
    quantity: int | None = None
    flags: list[str] = Field(default_factory=list)
    flagged_anomaly: bool = False
    raw_fragment: str | None = None


class CandidateListingHtmlInput(BaseModel):
    candidate_url: str
    html: str


class ParseListingHtmlRequest(BaseModel):
    pages: list[CandidateListingHtmlInput]


class ParseListingHtmlResponse(BaseModel):
    parsed_count: int
    rows: list[ListingRow]


class FullEvaluationRequest(BaseModel):
    candidate_url: str


class ListingSummary(BaseModel):
    total_rows: int
    anomaly_rows: int
    priced_rows: int


class FullEvaluationResult(BaseModel):
    candidate_url: str
    verification: VerificationResult
    parsed_metadata: ProductPageMetadata
    listing_summary: ListingSummary
    pricing: ValuationResult | None = None
    method_used: str
    notes: list[str] = Field(default_factory=list)


class ValuationRequest(BaseModel):
    candidate_url: str
    verified_filtered_demonstrable: bool = False


class ValuationResult(BaseModel):
    candidate_url: str
    pricing_method: Literal["verified_filtered_avg5", "nm_visible_benchmark"]
    distinct_prices_used: list[float]
    average_price: float
    excluded_rows_count: int
    notes: list[str] = Field(default_factory=list)


class PriceInput(BaseModel):
    amount: float
    flagged_anomaly: bool = False


class PriceOutput(BaseModel):
    pricing_method: Literal["verified_filtered_avg5", "nm_visible_benchmark"]
    average_price: float
    selected_prices: list[float]
    notes: list[str] = Field(default_factory=list)


class CardResult(BaseModel):
    identified_card: IdentifiedCard
    candidates: list[CandidateProduct] = Field(default_factory=list)
    verification: VerificationResult
    pricing: PriceOutput | None = None
    listing_count_visible: int = 0


class CardClarification(BaseModel):
    image_id: UUID
    reason: str
    missing_data: list[str] = Field(default_factory=list)


class JobRecord(BaseModel):
    job_id: UUID
    status: JobStatus
    target_language: str
    minimum_condition: str
    created_at: datetime
    images: list[JobImageResponse] = Field(default_factory=list)
    analysis_results: list[CardResult] = Field(default_factory=list)
    cards_to_clarify: list[CardClarification] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
