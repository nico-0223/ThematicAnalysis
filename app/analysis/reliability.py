from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Annotation, Code, Coder
from app.framework.audit_trail import record_audit_event


def _coder_assignments(session: Session, run_id: int) -> dict[str, dict[int, set[str]]]:
    data: dict[str, dict[int, set[str]]] = defaultdict(lambda: defaultdict(set))
    annotations = session.scalars(select(Annotation).where(Annotation.analysis_run_id == run_id)).all()
    for ann in annotations:
        coder = session.get(Coder, ann.coder_id)
        code = session.get(Code, ann.code_id)
        if coder and code:
            data[coder.name][ann.segment_id].add(code.name)
    return data


def coder_comparison(session: Session, run_id: int) -> list[dict[str, object]]:
    assignments = _coder_assignments(session, run_id)
    names = sorted(assignments)
    rows: list[dict[str, object]] = []
    for i, first in enumerate(names):
        for second in names[i + 1 :]:
            segment_ids = sorted(set(assignments[first]) | set(assignments[second]))
            agreements = 0
            disagreements = 0
            for segment_id in segment_ids:
                if assignments[first].get(segment_id, set()) == assignments[second].get(segment_id, set()):
                    agreements += 1
                else:
                    disagreements += 1
            rows.append({"coder_a": first, "coder_b": second, "segments": len(segment_ids), "agreements": agreements, "disagreements": disagreements})
    return rows


def cohens_kappa_binary(session: Session, run_id: int, coder_a: str | None = None, coder_b: str | None = None) -> dict[str, float | str]:
    assignments = _coder_assignments(session, run_id)
    names = sorted(assignments)
    if len(names) < 2:
        return {"status": "not_applicable", "kappa": 0.0, "reason": "At least two coders are required."}
    a = coder_a or names[0]
    b = coder_b or names[1]
    segment_ids = sorted(set(assignments[a]) | set(assignments[b]))
    if not segment_ids:
        return {"status": "not_applicable", "kappa": 0.0, "reason": "No overlapping segments."}
    agree_yes = agree_no = a_yes_b_no = a_no_b_yes = 0
    all_codes = sorted({code for coder in assignments.values() for labels in coder.values() for code in labels})
    for segment_id in segment_ids:
        a_codes = assignments[a].get(segment_id, set())
        b_codes = assignments[b].get(segment_id, set())
        for code in all_codes:
            av = code in a_codes
            bv = code in b_codes
            if av and bv:
                agree_yes += 1
            elif not av and not bv:
                agree_no += 1
            elif av and not bv:
                a_yes_b_no += 1
            else:
                a_no_b_yes += 1
    total = agree_yes + agree_no + a_yes_b_no + a_no_b_yes
    observed = (agree_yes + agree_no) / total if total else 0.0
    p_a_yes = (agree_yes + a_yes_b_no) / total if total else 0.0
    p_b_yes = (agree_yes + a_no_b_yes) / total if total else 0.0
    p_a_no = 1 - p_a_yes
    p_b_no = 1 - p_b_yes
    expected = p_a_yes * p_b_yes + p_a_no * p_b_no
    kappa = (observed - expected) / (1 - expected) if expected != 1 else 1.0
    record_audit_event(session, run_id, None, "calculate_reliability", "Calculated optional binary Cohen's kappa.", after_state={"coder_a": a, "coder_b": b, "kappa": kappa})
    return {"status": "ok", "coder_a": a, "coder_b": b, "kappa": round(kappa, 4), "observed_agreement": round(observed, 4)}


def disagreement_table(session: Session, run_id: int) -> list[dict[str, object]]:
    rows = []
    assignments = _coder_assignments(session, run_id)
    names = sorted(assignments)
    if len(names) < 2:
        return rows
    a, b = names[0], names[1]
    for segment_id in sorted(set(assignments[a]) | set(assignments[b])):
        if assignments[a].get(segment_id, set()) != assignments[b].get(segment_id, set()):
            rows.append({"segment_id": segment_id, a: sorted(assignments[a].get(segment_id, set())), b: sorted(assignments[b].get(segment_id, set()))})
    return rows
