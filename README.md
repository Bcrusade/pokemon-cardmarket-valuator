# Pokemon Cardmarket Valuator

Open-source MVP for valuing Pokémon cards from images using verified Cardmarket product pages and deterministic pricing.

## Stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Database: PostgreSQL (planned integration, MVP currently uses in-memory job store)
- Browser automation: Playwright (module dependency included)

## API Endpoints (MVP)

- `POST /jobs` — create a pricing job with target language and minimum condition
- `POST /jobs/{job_id}/images` — upload one or more card images
- `POST /jobs/{job_id}/candidates` — ingest externally discovered candidate search results
- `POST /jobs/{job_id}/candidates/fetch-html` — fetch/store product page HTML for a known candidate URL
- `POST /jobs/{job_id}/candidates/parse-html` — parse provided product-page HTML for known candidate URLs
- `POST /jobs/{job_id}/candidates/parse-listings` — parse provided listing HTML for known candidate URLs
- `POST /jobs/{job_id}/candidates/valuate` — compute deterministic valuation from stored parsed listing rows
- `POST /jobs/{job_id}/candidates/run-full-evaluation` — run deterministic end-to-end evaluation from stored candidate HTML
- `POST /jobs/{job_id}/analyze` — **legacy/deprecated** pre-pipeline workflow (kept for backward compatibility)
- `GET /jobs/{job_id}` — fetch job status and stored details
- `GET /jobs/{job_id}/results` — fetch analysis results and `cards_to_clarify`

### Primary workflow

Use candidate-driven endpoints (`/candidates/*`), especially `POST /jobs/{job_id}/candidates/run-full-evaluation`, as the main deterministic path.

## Deterministic Pricing Rules

`pricing_engine` implementation:
1. Remove flagged anomalies.
2. Remove identical duplicate prices.
3. Keep first 5 distinct prices.
4. Average available selected prices.
5. Label result as:
   - `verified_filtered_avg5` (standard)
   - `nm_visible_benchmark` (fallback)

## Important Governance Rules

- Never manually construct final Cardmarket product URLs from card data alone.
- Never trust product pages solely because URL strings look correct.
- Never use guide/trend/from prices as final card values.
- Never use AI for final pricing computations.
- Always return `cards_to_clarify` when card/page verification is uncertain.
- Always mark fallback results explicitly as fallback.

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
pytest -q
```

## Repository Structure

```text
backend/
  app/
    main.py
    schemas.py
    store.py
    modules/
      anomaly_filter.py
      candidate_search.py
      image_identification.py
      listing_parser.py
      pricing_engine.py
      product_verification.py
  tests/
frontend/
  app/
```

## License

AGPL-3.0-or-later
