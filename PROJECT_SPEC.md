# Pokemon Cardmarket Valuator — Project Specification

## Purpose

Pokemon Cardmarket Valuator is an open-source web application for valuing Pokémon cards from images using Cardmarket product pages as the pricing source.

The system must use AI only for visual card identification and ambiguity handling.
All product verification, listing extraction, filtering logic, and price calculation must be deterministic and code-based.

## Core Objective

Given one or more images of Pokémon cards, the application must:

1. Identify each card from the image.
2. Find the correct Cardmarket product page.
3. Verify that the product page actually matches the visible card.
4. Apply requested filters only after verification.
5. Extract real visible listings.
6. Compute a final price using the average of the first 5 distinct visible prices.
7. Return a structured result with notes and a mandatory "cards_to_clarify" section.

## Non-Negotiable Rules

The system must never:

- manually construct the final Cardmarket product URL from card data alone
- trust a Cardmarket product page only because the URL looks plausible
- use guide prices, trend prices, “from” prices, or price guides as the final value
- use AI to compute pricing once listing rows are already available

The system must always:

- identify cards only from what is actually visible in the image
- verify product pages using name, set, number, and variant compatibility
- use real visible listings as the pricing source
- explicitly mark fallback results when filters cannot be fully verified
- keep uncertain cards out of definitive pricing

## Main Workflow

### Step A — Image Input
The user uploads one or more images.

### Step B — AI Identification
For each visible card, the AI returns a structured result including:

- card name
- set name
- card number
- visible language
- variant
- promo / non-promo
- confidence score
- notes

### Step C — Candidate Search
The backend finds candidate Cardmarket product pages using search logic.

### Step D — Product Verification
The backend verifies candidate pages against the identified card using:

- exact card name
- exact set
- exact card number
- variant compatibility
- promo / non-promo compatibility
- artwork consistency when possible

If the page cannot be verified confidently, the card must go to `cards_to_clarify`.

### Step E — Filter Application
Only after product verification, the backend applies the requested filters, such as:

- target language
- minimum condition

### Step F — Listing Extraction
The backend extracts listing rows visible on the filtered product page.

### Step G — Anomaly Handling
The backend excludes:

- identical duplicate prices
- clearly anomalous offers
- listings not comparable to the target card/version
- ambiguous rows when necessary

### Step H — Pricing
Standard pricing formula:

- take the first 5 distinct visible prices after filtering
- ignore identical duplicates
- exclude anomalies
- compute the average of the remaining distinct prices

If fewer than 5 valid distinct prices are available, average the available ones.

## Fallback Logic

If the exact filter state cannot be verified in a demonstrable way:

- use visible NM listings on the verified correct page as a benchmark
- do not present the result as a fully verified filtered result
- explicitly state the limitation in the output

Allowed pricing methods:

- `verified_filtered_avg5`
- `nm_visible_benchmark`

## Output Requirements

For each successfully priced card, return:

- card name
- set code and number
- target language
- target condition
- average unit price
- quantity
- total price
- verified Cardmarket URL
- pricing method
- notes

The response must also include:

- `cards_to_clarify`

Each card in `cards_to_clarify` must contain:

- reason for uncertainty
- missing or ambiguous data
- image reference if available

## AI Role

AI is allowed for:

- visual card identification
- ambiguity support
- candidate ranking assistance

AI is not allowed for:

- final pricing calculations
- deterministic listing parsing
- replacing pricing rules

## Tech Stack

### Frontend
- Next.js
- TypeScript

### Backend
- FastAPI
- Python

### Database
- PostgreSQL

### Browser Automation
- Playwright

## Suggested Backend Modules

- `image_identification.py`
- `candidate_search.py`
- `product_verification.py`
- `cardmarket_browser.py`
- `listing_parser.py`
- `anomaly_filter.py`
- `pricing_engine.py`

## Suggested API Endpoints

- `POST /jobs`
- `POST /jobs/{job_id}/images`
- `POST /jobs/{job_id}/analyze`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/results`
- `POST /cards/{card_id}/override`
- `POST /cards/{card_id}/reprice`

## Open Source Direction

This repository is open source and intended for public collaboration.

License target:
- AGPL-3.0-or-later

Repository should include:
- README.md
- AGENTS.md
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- SECURITY.md
- LICENSE
- issue templates
- pull request template
- .env.example

## MVP Scope

Initial MVP should support:

- Pokémon cards only
- image upload
- single target language per batch
- single target minimum condition per batch
- deterministic pricing engine
- manual review for uncertain matches

Out of scope for MVP:

- multiple TCGs
- account-based Cardmarket automation
- seller dashboards
- advanced portfolio analytics
- large-scale asynchronous crawling
