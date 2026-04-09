from __future__ import annotations

from typing import Protocol

from app.schemas import CandidateProduct, CandidateSignals, IdentifiedCard


class CandidateProvider(Protocol):
    def fetch_candidates(self, card: IdentifiedCard) -> list[CandidateProduct]:
        """Return externally discovered candidate pages/details."""


class StubCandidateProvider:
    """Deterministic provider stub with extension point for real implementations."""

    def fetch_candidates(self, card: IdentifiedCard) -> list[CandidateProduct]:
        return [
            CandidateProduct(
                candidate_name=card.card_name,
                raw_title=f"{card.card_name} {card.set_name} {card.card_number}",
                set_name=card.set_name,
                card_number=card.card_number,
                variant=card.variant,
                promo=card.promo,
                source="cardmarket_search_stub",
                candidate_url=None,
                confidence_signals=CandidateSignals(
                    name_exact=True,
                    set_exact=True,
                    number_exact=True,
                    variant_compatible=True,
                    promo_compatible=True,
                ),
            )
        ]


def search_cardmarket_candidates(
    card: IdentifiedCard,
    provider: CandidateProvider | None = None,
) -> list[CandidateProduct]:
    """Search extension entrypoint.

    Important: this function does not fabricate final Cardmarket product URLs.
    """
    active_provider = provider or StubCandidateProvider()
    return active_provider.fetch_candidates(card)
