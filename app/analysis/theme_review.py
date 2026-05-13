from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CandidateTheme
from app.framework.audit_trail import record_audit_event


def review_candidate_themes(session: Session, run_id: int, min_segments: int = 1) -> list[CandidateTheme]:
    candidates = session.scalars(select(CandidateTheme).where(CandidateTheme.analysis_run_id == run_id)).all()
    for candidate in candidates:
        support = json.loads(candidate.supporting_segments_json or "[]")
        before = candidate.review_status
        candidate.review_status = "needs_more_evidence" if len(set(support)) < min_segments else "supported_pending_definition"
        candidate.rationale = f"Review check used minimum segment support = {min_segments}. Analyst should split, merge, rename, or reject if needed."
        record_audit_event(
            session,
            analysis_run_id=run_id,
            phase_number=4,
            action_type="review_candidate_theme",
            description=f"Reviewed candidate theme '{candidate.name}'.",
            before_state={"review_status": before},
            after_state={"review_status": candidate.review_status, "supporting_segments": len(set(support))},
        )
    session.flush()
    return list(candidates)
