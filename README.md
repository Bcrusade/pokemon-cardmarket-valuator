# Pokemon Cardmarket Valuator

Open-source web app for valuing Pokémon cards from images using verified Cardmarket product pages and deterministic pricing rules.

## What it does

The app:

1. reads card images
2. identifies the card with AI
3. finds candidate Cardmarket product pages
4. verifies the correct product page
5. applies requested filters only after verification
6. parses real visible listings
7. calculates price using the average of the first 5 distinct visible prices

## Key Principles

- Do not manually construct final Cardmarket product URLs from card data alone.
- Do not trust a page only because the URL looks correct.
- Do not use “from”, trend, or guide prices as final values.
- Use AI only for identification and ambiguity handling.
- Use deterministic code for parsing and pricing.

## Pricing Methods

### `verified_filtered_avg5`
Used when the requested filters are verified and visible listings can be parsed correctly.

### `nm_visible_benchmark`
Used when exact filter verification is not demonstrable. In this case, visible Near Mint listings from the verified correct page are used as a benchmark and the limitation is explicitly reported.

## Planned Stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Database: PostgreSQL
- Browser automation: Playwright

## Repository Goals

This is an open-source project intended for public collaboration.

Goals:
- transparent pricing logic
- reproducible verification flow
- community contribution
- strict separation between AI-assisted identification and deterministic valuation

## Project Status

Early MVP specification and scaffold stage.

## Local Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Variables

See `.env.example`.

Expected variables will likely include:

- database connection string
- OpenAI API key
- Playwright/browser configuration
- app environment settings

## Repository Structure

```text
frontend/
backend/
docs/
.github/
```

## Documentation

- `PROJECT_SPEC.md` — functional specification
- `AGENTS.md` — repository instructions for coding agents
- `CONTRIBUTING.md` — contribution workflow
- `SECURITY.md` — security reporting policy

## Contributing

Please read `CONTRIBUTING.md` before opening pull requests.

## License

AGPL-3.0-or-later
