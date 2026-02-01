# Permitting + Site Acquisition Agent (Telecom)

Production-minded MVP for small cell + fiber permitting: intake, document review, portal research, portal automation (human-in-the-loop), and outreach.

## Features

- **Intake**: Jurisdiction, address/site details, scope of work, existing docs.
- **Document review**: Ingest PDF/Word, extract key fields, compare to checklist, output "What's Needed" with page/section citations.
- **Portal research**: Crawl official jurisdiction pages (respecting robots.txt, rate-limited); capture requirements, fees, formats, portal links; store sources + timestamps.
- **Portal automation**: Playwright-based submission flow with **approve-each-step** mode; never submits without explicit confirmation.
- **Outreach**: Discover contacts (planning, engineering, ROW, clerk), draft emails, export contact list with source URLs.

## Guardrails

- Respects robots.txt; rate-limited requests; no scraping behind logins unless user supplies credentials.
- Never guesses legal requirements: cites source or marks "uncertain".
- Outputs: structured JSON + human-readable Markdown/PDF reports.

## Setup

```bash
cd permitting_agent
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
playwright install chromium
```

## CLI (first)

```bash
# Intake: create a case from jurisdiction + address + scope
permitting intake --jurisdiction "City of Sample" --address "123 Main St" --scope "small_cell" --output-dir ./output

# Document review: analyze uploaded docs vs checklist
permitting document-review --case-id <id> --docs ./docs --checklist ./config/checklist.yaml --output ./output/report

# Portal research: fetch requirements from jurisdiction (sample adapter)
permitting portal-research --jurisdiction "City of Sample" --output ./output/research

# Portal automation: run Playwright flow with human-in-the-loop (stub)
permitting portal-automation --case-id <id> --approve-each-step

# Outreach: discover contacts and generate drafts
permitting outreach --jurisdiction "City of Sample" --output ./output/outreach
```

## Pluggable jurisdiction adapters

Add adapters under `src/permitting_agent/adapters/`; register in `registry.py`. Sample adapter: `sample_jurisdiction.py`.

## One working path (E2E)

Sample jurisdiction: **City of Sample**. End-to-end:

```bash
# From repo root
cd permitting_agent
pip install -e ".[dev]"
python scripts/run_e2e.py
```

This creates a case, generates `samples/sample.pdf` if missing, runs document review against the sample checklist, and writes `output/e2e_report.json` and `output/e2e_report.md`.

Optional: `pip install fpdf2` so the sample PDF contains extractable text and the parser finds application/site plan/fee mentions.

## Tests

```bash
pytest tests/ -v
```

## Deploy on Render

Repo: [github.com/permitagent/Permitting-Agent](https://github.com/permitagent/Permitting-Agent)

1. **Connect repo** – In [Render](https://render.com): New → Web Service (or Blueprint), connect **Permitting-Agent** repo.
2. **Root Directory** – Leave **blank** (this repo root is the permitting agent).
3. **Build / Start** – Render will use `render.yaml` or set manually:
   - **Build:** `pip install -r requirements.txt && pip install -e .`
   - **Start:** `gunicorn -w 1 -b 0.0.0.0:$PORT app:app`
4. **Blueprint** – New → Blueprint, connect this repo; it will read `render.yaml` and create the web service.

The deployed app serves JSON at `/`, `/health`, and `/adapters`. CLI workflows are for local or worker use.

## License

MIT.
