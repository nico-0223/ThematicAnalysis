from sqlalchemy import select

from app.analysis.thematic_engine import start_analysis_run
from app.codebook.loader import load_codebook
from app.db.models import FrameworkSettings, MethodologicalPhase
from app.framework.braun_clarke import set_phase_status


def test_framework_settings_and_phases(db_session):
    codebook = load_codebook(db_session, "app/codebook/examples/codebook.example.yml")
    settings = db_session.scalar(select(FrameworkSettings).where(FrameworkSettings.codebook_version_id == codebook.id))
    assert settings.primary_framework.startswith("Braun")
    run = start_analysis_run(db_session, "0.1.0", "test")
    phases = db_session.scalars(select(MethodologicalPhase).where(MethodologicalPhase.analysis_run_id == run.id)).all()
    assert len(phases) == 6
    phase = set_phase_status(db_session, run.id, 1, complete=True)
    assert phase.status == "completed"
