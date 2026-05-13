from app.analysis.reliability import cohens_kappa_binary
from app.analysis.thematic_engine import import_annotations, start_analysis_run
from app.annotation.human_annotation import add_manual_annotation
from app.codebook.loader import load_codebook
from app.ingestion.loaders import ingest_file
from app.preprocessing.segmenters import preprocess_turns


def test_basic_coder_agreement(db_session):
    load_codebook(db_session, "app/codebook/examples/codebook.example.yml")
    ingest_file(db_session, "data/raw/demo_conversations.csv", "csv")
    preprocess_turns(db_session, strategy="turn")
    run = start_analysis_run(db_session, "0.1.0", "demo")
    import_annotations(db_session, run.id, "data/raw/demo_annotations.csv")
    add_manual_annotation(db_session, run.id, segment_id=1, code_name="Example Code", coder_name="second_coder", rationale="Second coder example.")
    result = cohens_kappa_binary(db_session, run.id)
    assert "kappa" in result
