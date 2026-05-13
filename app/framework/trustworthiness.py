from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import AuditTrailEntry, CodingDecision, Memo, MethodologicalPhase


def trustworthiness_summary(session: Session, run_id: int) -> dict[str, int]:
    return {
        "audit_trail_entries": session.scalar(select(func.count(AuditTrailEntry.id)).where(AuditTrailEntry.analysis_run_id == run_id)) or 0,
        "phase_records": session.scalar(select(func.count(MethodologicalPhase.id)).where(MethodologicalPhase.analysis_run_id == run_id)) or 0,
        "coding_decisions": session.scalar(select(func.count(CodingDecision.id))) or 0,
        "memos": session.scalar(select(func.count(Memo.id))) or 0,
    }


def methods_section_text() -> str:
    return (
        "The application structures the analytic workflow using Braun and Clarke's six phases. "
        "Trustworthiness is supported through audit trail entries, phase records, memos, coding-decision logs, "
        "codebook versioning, and explicit inclusion and exclusion criteria. These records support transparency; "
        "they do not replace researcher interpretation."
    )
