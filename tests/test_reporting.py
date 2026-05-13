from pathlib import Path

from app.analysis.thematic_engine import apply_rule_based_codes, start_analysis_run
from app.codebook.loader import load_codebook
from app.ingestion.loaders import ingest_file
from app.preprocessing.segmenters import preprocess_turns
from app.reports.exporters import export_report


def test_exporting_report(db_session, tmp_path: Path):
    load_codebook(db_session, "app/codebook/examples/codebook.example.yml")
    ingest_file(db_session, "data/raw/demo_conversations.csv", "csv")
    preprocess_turns(db_session, strategy="turn")
    run = start_analysis_run(db_session, "0.1.0", "demo")
    apply_rule_based_codes(db_session, run.id)
    out = tmp_path / "report.md"
    export_report(db_session, run.id, "markdown", out)
    text = out.read_text(encoding="utf-8")
    assert "Braun" in text
    assert "Audit trail" in text
