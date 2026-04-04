from __future__ import annotations

from app.schemas import IdentifiedCard, JobImageResponse


def identify_card_from_image(image: JobImageResponse) -> IdentifiedCard:
    """Placeholder AI module. Returns deterministic fake payload for MVP wiring."""
    return IdentifiedCard(
        image_id=image.image_id,
        card_name="Pikachu",
        set_name="Base Set",
        card_number="58/102",
        variant="Unlimited",
        promo=False,
        confidence=0.51,
        notes=["placeholder identification result"],
    )
