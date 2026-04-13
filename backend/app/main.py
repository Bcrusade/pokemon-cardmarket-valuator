from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.modules.anomaly_filter import flag_listing_row_anomalies
from app.modules.candidate_discovery import normalize_discovery_batch
from app.modules.end_to_end_valuation_service import run_full_evaluation
from app.modules.listing_row_parser import parse_listing_rows
from app.modules.valuation_service import valuate_candidate_from_rows
from app.modules.pricing_engine import PricingError
from app.modules.product_metadata_parser import parse_product_metadata
from app.modules.product_page_retrieval_service import retrieve_candidate_html
from app.schemas import (
    CreateJobRequest,
    CandidateHtmlFetchRequest,
    CandidateHtmlFetchResponse,
    CreateJobResponse,
    DiscoveryIngestRequest,
    FullEvaluationRequest,
    FullEvaluationResult,
    DiscoveryIngestResponse,
    JobRecord,
    ListingRow,
    ParseCandidateHtmlRequest,
    ParseCandidateHtmlResponse,
    ParseListingHtmlRequest,
    ParseListingHtmlResponse,
    ProductPageMetadata,
    ValuationRequest,
    ValuationResult,
)
from app.store import store

app = FastAPI(title="Pokemon Cardmarket Valuator API", version="0.1.0")

# ✅ CORS FIX (fondamentale per il frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/jobs", response_model=CreateJobResponse)
def create_job(payload: CreateJobRequest) -> CreateJobResponse:
    job = store.create_job(
        target_language=payload.target_language,
        minimum_condition=payload.minimum_condition,
    )
    return CreateJobResponse(job_id=job.job_id, status=job.status)


@app.post("/jobs/{job_id}/images")
def upload_job_images(job_id: UUID, files: list[UploadFile] = File(...)) -> dict:
    try:
        images = [store.add_image(job_id, f.filename or "unnamed-image") for f in files]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    return {"job_id": job_id, "uploaded_images": images}


@app.post("/jobs/{job_id}/candidates", response_model=DiscoveryIngestResponse)
def ingest_discovered_candidates(job_id: UUID, payload: DiscoveryIngestRequest) -> DiscoveryIngestResponse:
    try:
        store.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    normalized = normalize_discovery_batch(payload.results)
    store.save_discovery_candidates(
        job_id,
        raw_items=[item.model_dump() for item in payload.results],
        normalized=normalized,
    )

    return DiscoveryIngestResponse(ingested_count=len(normalized), candidates=normalized)


@app.post("/jobs/{job_id}/candidates/fetch-html", response_model=CandidateHtmlFetchResponse)
def fetch_candidate_html(job_id: UUID, payload: CandidateHtmlFetchRequest) -> CandidateHtmlFetchResponse:
    try:
        known_urls = store.known_candidate_urls(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    if payload.candidate_url not in known_urls:
        raise HTTPException(status_code=400, detail="Unknown candidate URL for this job.")

    fetcher = getattr(app.state, "fetch_adapter", None)
    try:
        html, mode = retrieve_candidate_html(
            candidate_url=payload.candidate_url,
            mode=payload.retrieval_mode,
            fetcher=fetcher,
            provided_html=payload.provided_html,
        )
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    store.save_candidate_html(job_id, payload.candidate_url, html, mode)
    return CandidateHtmlFetchResponse(
        candidate_url=payload.candidate_url,
        retrieval_mode=mode,
        stored=True,
        html_length=len(html),
    )


@app.post("/jobs/{job_id}/candidates/parse-html", response_model=ParseCandidateHtmlResponse)
def parse_candidate_html(job_id: UUID, payload: ParseCandidateHtmlRequest) -> ParseCandidateHtmlResponse:
    try:
        known_urls = store.known_candidate_urls(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    unknown_urls = [page.candidate_url for page in payload.pages if page.candidate_url not in known_urls]
    if unknown_urls:
        raise HTTPException(status_code=400, detail={"unknown_candidate_urls": unknown_urls})

    parsed_models: dict[str, ProductPageMetadata] = {}
    for page in payload.pages:
        html = page.html or (store.get_candidate_html(job_id, page.candidate_url) or "")
        metadata = parse_product_metadata(html)
        parsed_models[page.candidate_url] = metadata

    store.save_parsed_product_metadata(job_id, parsed_models)

    return ParseCandidateHtmlResponse(
        parsed_count=len(parsed_models),
        parsed_metadata=parsed_models,
    )


@app.post("/jobs/{job_id}/candidates/parse-listings", response_model=ParseListingHtmlResponse)
def parse_candidate_listing_html(job_id: UUID, payload: ParseListingHtmlRequest) -> ParseListingHtmlResponse:
    try:
        known_urls = store.known_candidate_urls(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    unknown_urls = [page.candidate_url for page in payload.pages if page.candidate_url not in known_urls]
    if unknown_urls:
        raise HTTPException(status_code=400, detail={"unknown_candidate_urls": unknown_urls})

    rows_by_url = {}
    all_rows = []
    for page in payload.pages:
        rows = parse_listing_rows(page.html, page.candidate_url)
        flagged_rows = flag_listing_row_anomalies(rows)
        rows_by_url[page.candidate_url] = flagged_rows
        all_rows.extend(flagged_rows)

    store.save_parsed_listing_rows(job_id, rows_by_url)
    return ParseListingHtmlResponse(parsed_count=len(all_rows), rows=all_rows)


@app.post("/jobs/{job_id}/candidates/valuate", response_model=ValuationResult)
def valuate_candidate(job_id: UUID, payload: ValuationRequest) -> ValuationResult:
    try:
        known_urls = store.known_candidate_urls(job_id)
        job = store.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    if payload.candidate_url not in known_urls:
        raise HTTPException(status_code=400, detail="Unknown candidate URL for this job.")

    rows_data = job.metadata.get("parsed_listing_rows", {}).get(payload.candidate_url)
    if not rows_data:
        raise HTTPException(status_code=400, detail="No parsed listing rows available for candidate URL.")

    try:
        valuation = valuate_candidate_from_rows(
            candidate_url=payload.candidate_url,
            rows=[ListingRow(**row) for row in rows_data],
            verified_filtered_demonstrable=payload.verified_filtered_demonstrable,
        )
    except PricingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    store.save_valuation(job_id, valuation)
    return valuation


@app.post("/jobs/{job_id}/candidates/run-full-evaluation", response_model=FullEvaluationResult)
def run_candidate_full_evaluation(job_id: UUID, payload: FullEvaluationRequest) -> FullEvaluationResult:
    try:
        evaluation = run_full_evaluation(store, job_id, payload.candidate_url)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    store.save_full_evaluation(job_id, evaluation)
    return evaluation


@app.get("/jobs/{job_id}", response_model=JobRecord)
def get_job(job_id: UUID) -> JobRecord:
    try:
        return store.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc


@app.get("/jobs/{job_id}/results")
def get_job_results(job_id: UUID) -> dict:
    try:
        job = store.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    return {
        "job_id": job_id,
        "status": job.status,
        "results": job.analysis_results,
        "cards_to_clarify": job.cards_to_clarify,
    }