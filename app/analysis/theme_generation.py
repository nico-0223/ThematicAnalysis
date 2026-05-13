from __future__ import annotations

import json
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AnalysisRun, Annotation, CandidateTheme, Code, Theme
from app.framework.audit_trail import record_audit_event


def generate_candidate_themes(session: Session, run_id: int) -> list[CandidateTheme]:
    annotations = session.scalars(select(Annotation).where(Annotation.analysis_run_id == run_id)).all()
    grouped: dict[int, dict[str, set[int]]] = defaultdict(lambda: {"codes": set(), "segments": set()})
    for annotation in annotations:
        code = session.get(Code, annotation.code_id)
        if code is None:
            continue
        grouped[code.theme_id]["codes"].add(code.id)
        grouped[code.theme_id]["segments"].add(annotation.segment_id)
    created: list[CandidateTheme] = []
    for theme_id, support in grouped.items():
        theme = session.get(Theme, theme_id)
        if theme is None:
            continue
        existing = session.scalar(select(CandidateTheme).where(CandidateTheme.analysis_run_id == run_id, CandidateTheme.name == theme.name))
        if existing:
            created.append(existing)
            continue
        candidate = CandidateTheme(
            analysis_run_id=run_id,
            name=theme.name,
            description=theme.description,
            supporting_codes_json=json.dumps(sorted(support["codes"])),
            supporting_segments_json=json.dumps(sorted(support["segments"])),
            review_status="candidate",
            rationale="Generated from configured code-to-theme relationships; requires analyst review.",
        )
        session.add(candidate)
        created.append(candidate)
    session.flush()
    record_audit_event(
        session,
        analysis_run_id=run_id,
        phase_number=3,
        action_type="generate_candidate_themes",
        description=f"Generated or updated {len(created)} candidate themes from coded segments.",
        after_state={"candidate_themes": [theme.name for theme in created]},
    )
    return created
