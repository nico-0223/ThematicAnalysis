from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analysis.coding_rules import match_code
from app.analysis.theme_generation import generate_candidate_themes
from app.db.models import AnalysisRun, Annotation, Code, CodebookVersion, Coder, CodingDecision, Segment
from app.framework.audit_trail import record_audit_event
from app.framework.braun_clarke import set_phase_status

RULE_BASED_CODER = "rule_based_system"


def get_or_create_coder(session: Session, name: str = RULE_BASED_CODER) -> Coder:
    coder = session.scalar(select(Coder).where(Coder.name == name))
    if coder:
        return coder
    coder = Coder(name=name, metadata_json=json.dumps({"type": "system_or_imported"}))
    session.add(coder)
    session.flush()
    return coder


def start_analysis_run(session: Session, codebook_version: str, run_name: str, run_type: str = "rule_based", config: dict | None = None) -> AnalysisRun:
    codebook = session.scalar(select(CodebookVersion).where(CodebookVersion.version == codebook_version, CodebookVersion.is_active == True))  # noqa: E712
    if codebook is None:
        codebook = session.scalar(select(CodebookVersion).where(CodebookVersion.version == codebook_version).order_by(CodebookVersion.id.desc()))
    if codebook is None:
        raise ValueError(f"No codebook version found: {codebook_version}")
    run = AnalysisRun(codebook_version_id=codebook.id, run_name=run_name, run_type=run_type, config_json=json.dumps(config or {}, sort_keys=True))
    session.add(run)
    session.flush()
    from app.framework.braun_clarke import create_phase_records

    create_phase_records(session, run)
    record_audit_event(
        session,
        analysis_run_id=run.id,
        phase_number=None,
        action_type="start_analysis_run",
        description=f"Started analysis run '{run_name}' using codebook {codebook.version}.",
        after_state={"run_id": run.id, "codebook_version": codebook.version, "run_type": run_type},
    )
    return run


def apply_rule_based_codes(session: Session, run_id: int) -> int:
    run = session.get(AnalysisRun, run_id)
    if run is None:
        raise ValueError(f"No analysis run found: {run_id}")
    coder = get_or_create_coder(session)
    codes = session.scalars(
        select(Code).join(Code.theme).where(Code.theme.has(codebook_version_id=run.codebook_version_id))
    ).all()
    segments = session.scalars(select(Segment).order_by(Segment.id)).all()
    created = 0
    set_phase_status(session, run_id, 2, complete=False)
    for segment in segments:
        for code in codes:
            rule_match = match_code(segment.text, code)
            if not rule_match.matched:
                continue
            existing = session.scalar(
                select(Annotation).where(
                    Annotation.segment_id == segment.id,
                    Annotation.code_id == code.id,
                    Annotation.coder_id == coder.id,
                    Annotation.analysis_run_id == run_id,
                )
            )
            if existing:
                continue
            annotation = Annotation(
                segment_id=segment.id,
                code_id=code.id,
                coder_id=coder.id,
                analysis_run_id=run_id,
                confidence=rule_match.confidence,
                rationale=rule_match.rationale,
                evidence_text=rule_match.evidence,
            )
            session.add(annotation)
            session.flush()
            session.add(
                CodingDecision(
                    annotation_id=annotation.id,
                    decision_type="rule_based_initial_code",
                    decision_note=rule_match.rationale,
                    framework_phase="Phase 2: Generating initial codes",
                )
            )
            created += 1
    session.flush()
    record_audit_event(
        session,
        analysis_run_id=run_id,
        phase_number=2,
        action_type="apply_rule_based_codes",
        description=f"Created {created} annotations using editable codebook indicators.",
        after_state={"annotations_created": created},
    )
    generate_candidate_themes(session, run_id)
    return created


def import_annotations(session: Session, run_id: int, path: str | Path) -> int:
    frame = pd.read_csv(path)
    required = {"segment_id", "code_name", "coder_name"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Annotation import missing columns: {', '.join(sorted(missing))}")
    created = 0
    for row in frame.fillna("").to_dict(orient="records"):
        code = session.scalar(select(Code).where(Code.name == row["code_name"]))
        if code is None:
            continue
        coder = get_or_create_coder(session, str(row["coder_name"]))
        existing = session.scalar(
            select(Annotation).where(
                Annotation.segment_id == int(row["segment_id"]),
                Annotation.code_id == code.id,
                Annotation.coder_id == coder.id,
                Annotation.analysis_run_id == run_id,
            )
        )
        if existing:
            continue
        annotation = Annotation(
            segment_id=int(row["segment_id"]),
            code_id=code.id,
            coder_id=coder.id,
            analysis_run_id=run_id,
            confidence=float(row.get("confidence") or 1.0),
            rationale=str(row.get("rationale") or "Imported manual annotation."),
            evidence_text=str(row.get("evidence_text") or ""),
        )
        session.add(annotation)
        session.flush()
        session.add(CodingDecision(annotation_id=annotation.id, decision_type="imported_annotation", decision_note=annotation.rationale, framework_phase="Phase 2: Generating initial codes"))
        created += 1
    session.flush()
    record_audit_event(session, run_id, 2, "import_annotations", f"Imported {created} annotations from {path}.", after_state={"imported": created})
    generate_candidate_themes(session, run_id)
    return created
