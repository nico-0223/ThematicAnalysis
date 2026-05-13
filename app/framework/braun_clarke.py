from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AnalysisRun, MethodologicalPhase
from app.framework.audit_trail import record_audit_event

BRAUN_CLARKE_REFERENCE = "Braun & Clarke (2006), six-phase thematic analysis"


@dataclass(frozen=True)
class PhaseDefinition:
    number: int
    name: str
    purpose: str


PHASES: tuple[PhaseDefinition, ...] = (
    PhaseDefinition(1, "Familiarisation with the data", "Preserve raw data, read conversations, and write familiarisation memos."),
    PhaseDefinition(2, "Generating initial codes", "Create manual, imported, or rule-based initial codes with evidence and rationale."),
    PhaseDefinition(3, "Searching for themes", "Aggregate codes into editable candidate themes."),
    PhaseDefinition(4, "Reviewing themes", "Check candidate themes against coded data and record refinement decisions."),
    PhaseDefinition(5, "Defining and naming themes", "Require analytical definitions, names, and inclusion/exclusion criteria."),
    PhaseDefinition(6, "Producing the report", "Export method, evidence, audit trail, limitations, and theme summaries."),
)


def get_phase(number: int) -> PhaseDefinition:
    for phase in PHASES:
        if phase.number == number:
            return phase
    raise ValueError(f"Unknown Braun & Clarke phase: {number}")


def create_phase_records(session: Session, analysis_run: AnalysisRun) -> list[MethodologicalPhase]:
    records: list[MethodologicalPhase] = []
    for phase in PHASES:
        existing = session.scalar(
            select(MethodologicalPhase).where(
                MethodologicalPhase.analysis_run_id == analysis_run.id,
                MethodologicalPhase.phase_number == phase.number,
            )
        )
        if existing:
            records.append(existing)
            continue
        record = MethodologicalPhase(
            analysis_run_id=analysis_run.id,
            phase_number=phase.number,
            phase_name=phase.name,
            framework_reference=BRAUN_CLARKE_REFERENCE,
            status="not_started",
            notes=phase.purpose,
        )
        session.add(record)
        records.append(record)
    session.flush()
    record_audit_event(
        session,
        analysis_run_id=analysis_run.id,
        phase_number=None,
        action_type="create_phase_records",
        description="Created Braun & Clarke phase records for the analysis run.",
        after_state={"phases": [p.name for p in PHASES]},
    )
    return records


def set_phase_status(session: Session, run_id: int, phase_number: int, complete: bool = False, notes: str | None = None) -> MethodologicalPhase:
    phase = session.scalar(
        select(MethodologicalPhase).where(
            MethodologicalPhase.analysis_run_id == run_id,
            MethodologicalPhase.phase_number == phase_number,
        )
    )
    if phase is None:
        definition = get_phase(phase_number)
        phase = MethodologicalPhase(
            analysis_run_id=run_id,
            phase_number=definition.number,
            phase_name=definition.name,
            framework_reference=BRAUN_CLARKE_REFERENCE,
            status="not_started",
            notes=definition.purpose,
        )
        session.add(phase)
        session.flush()
    before = {"status": phase.status, "notes": phase.notes}
    phase.started_at = phase.started_at or datetime.now(UTC)
    if complete:
        phase.status = "completed"
        phase.completed_at = datetime.now(UTC)
    else:
        phase.status = "in_progress"
    if notes:
        phase.notes = notes
    session.flush()
    record_audit_event(
        session,
        analysis_run_id=run_id,
        phase_number=phase_number,
        action_type="update_phase_status",
        description=f"Updated phase {phase_number}: {phase.phase_name}.",
        before_state=before,
        after_state={"status": phase.status, "notes": phase.notes},
    )
    return phase
