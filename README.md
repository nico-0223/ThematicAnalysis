# Conversation Thematic Analysis

A unified Python + SQL backend and React frontend for configurable thematic analysis of conversations.

The repository is one coherent project with a clean boundary between layers:

- `app/` contains backend application logic, persistence, validation, CLI commands, and the HTTP API.
- `web/` contains the React/Vite frontend. It talks to the backend only through HTTP calls in `web/src/api/*`.
- `tests/` contains backend tests.
- `web/src/test/` contains frontend tests.
- `data/` contains local demo inputs, SQLite data, and generated exports.
- `docs/` contains methodological and database documentation.

The backend remains the source of truth for analysis logic, data access, validation, persistence, audit trails, reports, and server-side operations. The frontend presents and controls those workflows through the API boundary; it must not import backend Python code, read backend files, or access the database directly.

The application encodes methodological workflow and traceability. It does not infer the final meaning of a dataset, determine the user's research question, or hard-code substantive themes. The analyst edits the codebook, framework settings, features, indicators, examples, counterexamples, memo prompts, and scoring rules.

## Academic framework

Primary framework:

- Braun, V., & Clarke, V. (2006). Using thematic analysis in psychology. *Qualitative Research in Psychology, 3*, 77–101.

Supporting framework for rigour and traceability:

- Nowell, L. S., Norris, J. M., White, D. E., & Moules, N. J. (2017). Thematic Analysis: Striving to Meet the Trustworthiness Criteria. *International Journal of Qualitative Methods, 16*, 1–13.

Supporting framework for editable codebook structure:

- Boyatzis, R. E. (1998). *Transforming Qualitative Information: Thematic Analysis and Code Development*. Sage.

## What the app does

- Ingests CSV, JSON, JSONL, and TXT conversation data.
- Stores conversations, speakers, turns, and segments in SQL.
- Loads editable YAML codebooks.
- Represents Braun and Clarke's six phases as database records attached to analysis runs.
- Applies rule-based coding using user-defined indicators, phrases, regex patterns, and codebook structures.
- Imports manual annotations.
- Generates editable candidate themes from configured code-to-theme relationships.
- Supports theme review, audit trails, memos, coding decisions, reliability summaries, adjudication records, and exports.
- Exports Markdown, HTML, JSON, and CSV reports.

## What the app does not do

- It does not create final themes without analyst review.
- It does not define the research question or epistemological position.
- It does not require or implement a real LLM provider.
- It does not treat inter-coder agreement as mandatory for all forms of thematic analysis.
- It does not remove discourse features aggressively during cleaning.

## Braun and Clarke phases in the application

1. Familiarisation with the data: raw conversations and turns are preserved; preprocessing and memos are logged.
2. Generating initial codes: manual, imported, or configurable rule-based codes are stored with evidence and rationale.
3. Searching for themes: coded segments are aggregated into candidate themes using editable codebook relationships.
4. Reviewing themes: candidate themes can be checked for support and flagged for splitting, merging, renaming, or rejection.
5. Defining and naming themes: themes contain analytical definitions, inclusion criteria, exclusion criteria, examples, and counterexamples.
6. Producing the report: exports include framework references, codebook version, phase status, evidence, memos, limitations, and audit-trail summaries.

## Trustworthiness support

The application operationalises Nowell et al.-style transparency through audit trail entries, phase records, memos, coding-decision logs, codebook versions, representative evidence, explicit inclusion/exclusion criteria, unresolved-disagreement records, and exportable methods sections.

These records support methodological transparency. They do not replace interpretive judgement.

## Boyatzis-style codebook structure

The YAML codebook supports themes, codes, subcode-ready code structures, indicators, units of analysis, inclusion criteria, exclusion criteria, examples, counterexamples, configurable features, and scoring-related hints.

Edit:

- `app/codebook/examples/codebook.example.yml` for themes, codes, indicators, features, memo prompts, and framework settings.
- `app/db/migrations/schema.sql` for the reference SQL schema.
- `app/db/models.py` for runtime SQLAlchemy models.

## Local installation

```bash
python -m venv .venv
source .venv/bin/activate
make install-backend
npm --prefix web install
```

Or install both with:

```bash
make install
```

## Environment configuration

Copy the backend example and adjust values for your machine:

```bash
cp .env.example .env
```

Backend variables:

| Name | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///data/thematic_analysis.db` | SQLAlchemy database URL |
| `APP_ENV` | `development` | Backend environment label |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated frontend origins allowed to call the API |
| `BACKEND_HOST` | `127.0.0.1` | Local backend bind host used by `make backend` |
| `BACKEND_PORT` | `8000` | Local backend port used by `make backend` |

Copy the frontend example when running Vite locally:

```bash
cp web/.env.example web/.env
```

Frontend variables:

| Name | Default | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000/api` | Backend API base URL |
| `VITE_APP_NAME` | `Conversation Thematic Analysis` | App title shown in the UI |
| `VITE_AUTH_MODE` | `disabled` | Reserved for a future auth layer |

Do not commit real `.env` files or secrets.

## Run the backend API locally

```bash
make backend
```

The API runs at `http://127.0.0.1:8000` by default. Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

The CLI remains available for backend workflows and automation:

```bash
python -m app.cli.commands --help
```

## Run the frontend locally

```bash
npm --prefix web run dev
# or
make frontend
```

The Vite dev server runs at `http://localhost:5173` and uses `VITE_API_BASE_URL` for backend communication.

## Run both locally

```bash
make dev
```

This starts the backend API and Vite frontend from one command. Stop both processes with `Ctrl+C`; if your shell leaves a background process running, stop it with your usual process manager.

## Run tests

```bash
make test
```

Individual suites:

```bash
make test-backend
make test-frontend
```

Backend tests run with `pytest`. Frontend tests run with Vitest through `npm --prefix web run test`.

## Build for production

```bash
make build
```

This builds the frontend into `web/dist/`. The backend is a Python package served by `uvicorn app.api:app`.

## Run the demo locally

```bash
make clean
make demo
```

Equivalent explicit commands:

```bash
python -m app.cli.commands init-db
python -m app.cli.commands load-codebook --path app/codebook/examples/codebook.example.yml
python -m app.cli.commands ingest --path data/raw/demo_conversations.csv --format csv
python -m app.cli.commands preprocess --strategy turn
python -m app.cli.commands start-run --codebook-version 0.1.0 --run-name demo
python -m app.cli.commands analyze --run-id 1
python -m app.cli.commands export --run-id 1 --format markdown --out data/exports/demo_report.md
```

The demo report is written to:

```text
data/exports/demo_report.md
```

## Docker deployment

```bash
docker compose build
docker compose up
```

Services:

- `api`: Python backend at `http://localhost:8000`.
- `web`: Nginx-served frontend at `http://localhost:8080`, proxying `/api` to the backend service.

You can still run CLI operations inside the backend container:

```bash
docker compose run --rm api python -m app.cli.commands init-db
docker compose run --rm api python -m app.cli.commands load-codebook --path app/codebook/examples/codebook.example.yml
docker compose run --rm api python -m app.cli.commands ingest --path data/raw/demo_conversations.csv --format csv
docker compose run --rm api python -m app.cli.commands preprocess --strategy turn
docker compose run --rm api python -m app.cli.commands start-run --codebook-version 0.1.0 --run-name demo
docker compose run --rm api python -m app.cli.commands analyze --run-id 1
docker compose run --rm api python -m app.cli.commands export --run-id 1 --format markdown --out data/exports/demo_report.md
```

For other platforms, deploy the backend as an ASGI app (`app.api:app`) and serve `web/dist/` with `VITE_API_BASE_URL` pointing at the deployed API.

## Frontend-backend communication

All browser-to-backend traffic goes through `web/src/api/client.ts`, which reads `VITE_API_BASE_URL`. Resource-specific API modules in `web/src/api/*.ts` define the endpoint paths. The backend exposes those routes from `app/api.py` under `/api`.

Keep shared behavior on the backend. If a workflow needs new business logic, validation, data loading, reporting, or persistence, add it to the backend and expose it through the API. The frontend should only hold UI state, form state, display formatting, and API request orchestration.

## Inspect the SQLite database

```bash
sqlite3 data/thematic_analysis.db
.tables
.schema annotations
SELECT * FROM methodological_phases;
SELECT * FROM audit_trail_entries;
```

## Input formats

CSV requires:

```text
conversation_id,speaker_label,turn_index,text
```

Optional columns include:

```text
timestamp,title,source,role,metadata_json
```

JSON may be a list of turn records or a mapping with a `turns` list. JSONL expects one turn record per line. TXT treats each non-empty line as a turn and supports `Speaker: text` format.

## Add an LLM provider later

Implement `AIAnnotationProvider` in `app/annotation/ai_annotation_interface.py`. Keep provider credentials in environment variables, not in code. Use the interface methods:

- `suggest_codes(segment_text, codebook_context)`
- `extract_features(segment_text, feature_schema)`
- `generate_rationale(segment_text, assigned_code)`
- `suggest_candidate_themes(coded_segments, codebook_context)`

The base application works without an API key.

## Repository quality checks

This repository was validated with:

```bash
python -m compileall app
pytest
make demo
```
# ThematicAnalysis
