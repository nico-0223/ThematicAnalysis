# Conversation Thematic Analysis

A production-oriented Python + SQL command-line application for configurable thematic analysis of conversations.

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
pip install -e .[test]
```

## Run tests

```bash
pytest
# or
make test
```

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

## Docker demo

```bash
docker compose build
docker compose run --rm app python -m app.cli.commands init-db
docker compose run --rm app python -m app.cli.commands load-codebook --path app/codebook/examples/codebook.example.yml
docker compose run --rm app python -m app.cli.commands ingest --path data/raw/demo_conversations.csv --format csv
docker compose run --rm app python -m app.cli.commands preprocess --strategy turn
docker compose run --rm app python -m app.cli.commands start-run --codebook-version 0.1.0 --run-name demo
docker compose run --rm app python -m app.cli.commands analyze --run-id 1
docker compose run --rm app python -m app.cli.commands export --run-id 1 --format markdown --out data/exports/demo_report.md
```

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
