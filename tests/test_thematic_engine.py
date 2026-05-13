from sqlalchemy import select

from app.analysis.thematic_engine import apply_rule_based_codes, start_analysis_run
from app.codebook.loader import load_codebook
from app.db.models import AnalysisRun, Annotation, CandidateTheme
from app.ingestion.loaders import ingest_file
from app.preprocessing.segmenters import preprocess_turns


def test_creating_analysis_run_and_rule_based_codes(db_session):
    load_codebook(db_session, "app/codebook/examples/codebook.example.yml")
    ingest_file(db_session, "data/raw/demo_conversations.csv", "csv")
    preprocess_turns(db_session, strategy="turn")
    run = start_analysis_run(db_session, "0.1.0", "demo")
    assert db_session.get(AnalysisRun, run.id) is not None
    created = apply_rule_based_codes(db_session, run.id)
    assert created >= 3
    assert len(db_session.scalars(select(Annotation).where(Annotation.analysis_run_id == run.id)).all()) >= 3
    assert len(db_session.scalars(select(CandidateTheme).where(CandidateTheme.analysis_run_id == run.id)).all()) >= 1
