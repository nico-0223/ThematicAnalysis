from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analysis.thematic_engine import get_or_create_coder
from app.db.models import Annotation, Code, CodingDecision
from app.framework.audit_trail import record_audit_event


def add_manual_annotation(
    session: Session,
    run_id: int,
    segment_id: int,
    code_name: str,
    coder_name: str,
    rationale: str,
    confidence: float = 1.0,
    evidence_text: str | None = None,
) -> Annotation:
    code = session.scalar(select(Code).where(Code.name == code_name))
    if code is None:
        raise ValueError(f"No code named {code_name}")
    coder = get_or_create_coder(session, coder_name)
    annotation = Annotation(segment_id=segment_id, code_id=code.id, coder_id=coder.id, analysis_run_id=run_id, confidence=confidence, rationale=rationale, evidence_text=evidence_text)
    session.add(annotation)
    session.flush()
    session.add(CodingDecision(annotation_id=annotation.id, decision_type="manual_annotation", decision_note=rationale, framework_phase="Phase 2: Generating initial codes"))
    record_audit_event(session, run_id, 2, "manual_annotation", f"Added manual annotation for segment {segment_id}.", after_state={"code": code_name, "coder": coder_name})
    return annotation
