# AGENTS.md

This repository contains an open-source MVP for Pokémon card valuation using Cardmarket product pages.

## Primary Objective

Build a system that identifies Pokémon cards from images, verifies the correct Cardmarket product page, extracts visible listings, and computes deterministic prices.

## Hard Rules

Do not violate these rules:

1. Never manually construct the final Cardmarket product URL from card data alone.
2. Never assume a page is correct just because the URL looks plausible.
3. Never use guide prices, trend prices, or “from” prices as final card values.
4. Never use AI to replace deterministic pricing logic.
5. Never assign definitive prices to uncertain card matches.
6. Always include a `cards_to_clarify` section when uncertainty exists.
7. Always keep fallback results explicitly labeled as fallback.

## AI Usage Policy

AI is allowed for:
- image-based card identification
- ambiguity handling
- confidence scoring
- candidate ranking assistance

AI is not allowed for:
- final pricing computation
- deterministic parsing of listing tables
- overriding hard business rules

## Pricing Rules

Standard method:
- extract first 5 distinct visible prices after verified filtering
- ignore identical duplicate prices
- exclude anomalous or non-comparable listings
- average the remaining valid prices

Fallback method:
- if exact filter verification cannot be demonstrated, use visible NM listings on the verified correct page
- mark result as `nm_visible_benchmark`
- include limitation notes

## Verification Rules

A Cardmarket product page must be verified against:
- card name
- set
- card number
- variant
- promo vs non-promo
- artwork compatibility when possible

If confidence is insufficient, send the card to `cards_to_clarify`.

## Engineering Preferences

- Prefer explicit and testable code.
- Keep pricing logic pure and unit-testable.
- Separate browser automation from parsing logic.
- Store intermediate results for auditability.
- Use typed schemas where possible.
- Favor small, focused modules over large service files.

## Required Deliverables

When scaffolding or modifying the project, preserve or improve:

- `README.md`
- `PROJECT_SPEC.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `LICENSE`
- API endpoint documentation
- tests for pricing and verification rules

## Testing Expectations

At minimum, add tests for:
- duplicate identical price removal
- average of first 5 distinct prices
- fallback behavior
- anomaly exclusion
- uncertain match routing to `cards_to_clarify`

## Contribution Safety

Do not merge logic that weakens verification or hides fallback limitations.
Transparency is a core requirement of the project.
