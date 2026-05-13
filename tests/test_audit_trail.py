from sqlalchemy import select

from app.codebook.loader import load_codebook
from app.db.models import AuditTrailEntry
from app.framework.audit_trail import record_audit_event


def test_creating_audit_trail_entries(db_session):
    load_codebook(db_session, "app/codebook/examples/codebook.example.yml")
    entry = record_audit_event(db_session, None, 1, "test_action", "Test audit action.", after_state={"ok": True})
    assert entry.id is not None
    assert db_session.scalar(select(AuditTrailEntry).where(AuditTrailEntry.action_type == "test_action")) is not None
