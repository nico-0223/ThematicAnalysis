# Database schema

The runtime schema is defined in `app/db/models.py`. A reference SQL schema is provided in `app/db/migrations/schema.sql`.

Core tables include conversations, speakers, turns, segments, codebook versions, framework settings, methodological phases, themes, candidate themes, codes, coding features, annotations, coders, coding decisions, memos, reflexive journal entries, audit trail entries, adjudication records, analysis runs, and exports.

The schema preserves original turns and segment text. Annotations link segments, codes, coders, and analysis runs. Audit trail entries can be global or tied to a specific run and phase.
