# Architecture

The repository is organised as a command-line research-software package. The main layers are database persistence, framework modelling, ingestion, preprocessing, codebook loading, analysis, annotation, memoing, reporting, and CLI orchestration.

The database layer uses SQLAlchemy models and a PostgreSQL-compatible database URL design. SQLite is the default for local work.

The framework layer models Braun and Clarke's six phases as first-class database records attached to each analysis run. Audit-trail functions are shared by ingestion, preprocessing, codebook loading, coding, theme generation, theme review, reliability, and reporting.

The analysis layer uses editable codebook indicators and does not encode substantive interpretations in code. Candidate themes are created from codebook-defined relationships and remain reviewable.
