from __future__ import annotations

from app.schemas import CandidateProduct, IdentifiedCard, ProductPageMetadata, VerificationResult


MATCH_THRESHOLD = 0.9


def _normalize(text: str | None) -> str:
    return (text or "").strip().lower()


def _score_field(candidate_value: str | None, metadata_value: str | None, target_value: str) -> tuple[float, bool]:
    """Return score contribution and mismatch flag for one field.

    Candidate value has precedence; metadata is used as deterministic fallback.
    """
    value = candidate_value if candidate_value is not None else metadata_value
    if _normalize(value) == _normalize(target_value):
        return 1.0, False
    return 0.0, True


def _score_candidate(
    card: IdentifiedCard,
    candidate: CandidateProduct,
    metadata: ProductPageMetadata | None,
) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    v, mismatch = _score_field(candidate.candidate_name, metadata.product_title if metadata else None, card.card_name)
    score += 0.25 * v
    if mismatch:
        reasons.append("name_mismatch")

    v, mismatch = _score_field(candidate.set_name, metadata.set_name if metadata else None, card.set_name)
    score += 0.25 * v
    if mismatch:
        reasons.append("set_mismatch")

    v, mismatch = _score_field(candidate.card_number, metadata.card_number if metadata else None, card.card_number)
    score += 0.25 * v
    if mismatch:
        reasons.append("card_number_mismatch")

    v, mismatch = _score_field(candidate.variant, metadata.variant if metadata else None, card.variant)
    score += 0.15 * v
    if mismatch:
        reasons.append("variant_mismatch")

    if candidate.promo is None:
        reasons.append("promo_unknown")
    elif candidate.promo == card.promo:
        score += 0.10
    else:
        reasons.append("promo_mismatch")

    return score, reasons


def verify_product_page(
    card: IdentifiedCard,
    candidates: list[CandidateProduct],
    parsed_metadata_by_url: dict[str, ProductPageMetadata] | None = None,
) -> VerificationResult:
    """Deterministic verifier with strict URL non-fabrication guarantees."""
    if card.confidence < 0.6:
        return VerificationResult(
            verified=False,
            verified_product_url=None,
            reason="Insufficient card identification confidence for verification.",
            best_match_score=0.0,
            threshold_used=MATCH_THRESHOLD,
        )

    if not candidates:
        return VerificationResult(
            verified=False,
            verified_product_url=None,
            reason="No candidates supplied by deterministic candidate provider.",
            best_match_score=0.0,
            threshold_used=MATCH_THRESHOLD,
        )

    metadata_lookup = parsed_metadata_by_url or {}
    scored: list[tuple[float, CandidateProduct, list[str]]] = []
    for candidate in candidates:
        metadata = metadata_lookup.get(candidate.candidate_url or "") if candidate.candidate_url else None
        score, mismatches = _score_candidate(card, candidate, metadata)
        scored.append((score, candidate, mismatches))

    best_score, best_candidate, mismatches = max(scored, key=lambda item: item[0])

    if best_score < MATCH_THRESHOLD:
        return VerificationResult(
            verified=False,
            verified_product_url=None,
            reason=f"Candidate score below threshold; mismatches={','.join(mismatches)}",
            best_match_score=round(best_score, 3),
            threshold_used=MATCH_THRESHOLD,
        )

    if not best_candidate.candidate_url:
        return VerificationResult(
            verified=False,
            verified_product_url=None,
            reason="Match score passed but candidate has no real upstream candidate_url.",
            best_match_score=round(best_score, 3),
            threshold_used=MATCH_THRESHOLD,
        )

    return VerificationResult(
        verified=True,
        verified_product_url=best_candidate.candidate_url,
        reason="Exact deterministic verification passed.",
        best_match_score=round(best_score, 3),
        threshold_used=MATCH_THRESHOLD,
    )
