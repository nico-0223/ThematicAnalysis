from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import ReflexiveJournalEntry
from app.framework.audit_trail import record_audit_event


def add_reflexive_entry(session: Session, text: str, run_id: int | None = None, coder_id: int | None = None, related_phase: str | None = None) -> ReflexiveJournalEntry:
    entry = ReflexiveJournalEntry(analysis_run_id=run_id, coder_id=coder_id, text=text, related_phase=related_phase)
    session.add(entry)
    session.flush()
    record_audit_event(session, run_id, None, "reflexive_journal_entry", "Added reflexive journal entry.", after_state={"entry_id": entry.id, "related_phase": related_phase})
    return entry
