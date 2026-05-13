from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import AdjudicationRecord
from app.framework.audit_trail import record_audit_event


def record_adjudication(session: Session, run_id: int, segment_id: int, decision: str, rationale: str | None = None, code_id: int | None = None) -> AdjudicationRecord:
    record = AdjudicationRecord(analysis_run_id=run_id, segment_id=segment_id, code_id=code_id, decision=decision, rationale=rationale)
    session.add(record)
    session.flush()
    record_audit_event(session, run_id, None, "adjudication", f"Recorded adjudication for segment {segment_id}.", after_state={"decision": decision, "code_id": code_id})
    return record
