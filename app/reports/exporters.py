from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analysis.aggregation import code_cooccurrence, code_frequency_per_speaker, representative_quotes, theme_development_over_turn_order, theme_frequency_per_conversation
from app.analysis.reliability import cohens_kappa_binary, disagreement_table
from app.db.models import AnalysisRun, Annotation, AuditTrailEntry, Code, CodebookVersion, Conversation, ExportRecord, FrameworkSettings, Memo, MethodologicalPhase, Segment, Theme, Turn
from app.framework.trustworthiness import methods_section_text, trustworthiness_summary
from app.reports.templates import REFERENCES_APA, markdown_table


def build_report_data(session: Session, run_id: int) -> dict[str, object]:
    run = session.get(AnalysisRun, run_id)
    if run is None:
        raise ValueError(f"No analysis run found: {run_id}")
    codebook = session.get(CodebookVersion, run.codebook_version_id)
    settings = session.scalar(select(FrameworkSettings).where(FrameworkSettings.codebook_version_id == run.codebook_version_id))
    phases = session.scalars(select(MethodologicalPhase).where(MethodologicalPhase.analysis_run_id == run_id).order_by(MethodologicalPhase.phase_number)).all()
    annotations = session.scalars(select(Annotation).where(Annotation.analysis_run_id == run_id)).all()
    theme_rows = []
    for theme in session.scalars(select(Theme).where(Theme.codebook_version_id == run.codebook_version_id)).all():
        codes = session.scalars(select(Code).where(Code.theme_id == theme.id)).all()
        code_ids = [code.id for code in codes]
        count = sum(1 for ann in annotations if ann.code_id in code_ids)
        theme_rows.append({"theme": theme.name, "status": theme.status, "coded_segments": count, "definition": theme.analytical_definition or ""})
    code_rows = []
    for code in session.scalars(select(Code).join(Theme).where(Theme.codebook_version_id == run.codebook_version_id)).all():
        count = sum(1 for ann in annotations if ann.code_id == code.id)
        code_rows.append({"code": code.name, "count": count, "definition": code.analytical_definition or ""})
    audit = session.scalars(select(AuditTrailEntry).where((AuditTrailEntry.analysis_run_id == run_id) | (AuditTrailEntry.analysis_run_id.is_(None))).order_by(AuditTrailEntry.created_at)).all()
    memos = session.scalars(select(Memo).order_by(Memo.created_at)).all()
    return {
        "run": {"id": run.id, "name": run.run_name, "type": run.run_type, "created_at": str(run.created_at)},
        "codebook": {"name": codebook.name if codebook else "", "version": codebook.version if codebook else "", "description": codebook.description if codebook else ""},
        "framework": {
            "primary": settings.primary_framework if settings else "Braun & Clarke 2006 six-phase thematic analysis",
            "supporting": json.loads(settings.supporting_frameworks_json or "[]") if settings else [],
            "analysis_orientation": settings.analysis_orientation if settings else "",
            "coding_orientation": settings.coding_orientation if settings else "",
            "theme_orientation": settings.theme_orientation if settings else "",
            "epistemological_position": settings.epistemological_position if settings else "",
            "semantic_or_latent": settings.semantic_or_latent if settings else "",
            "inductive_or_deductive": settings.inductive_or_deductive if settings else "",
        },
        "counts": {
            "conversations": session.scalar(select(func.count(Conversation.id))) or 0,
            "turns": session.scalar(select(func.count(Turn.id))) or 0,
            "segments": session.scalar(select(func.count(Segment.id))) or 0,
            "annotations": len(annotations),
        },
        "phases": [{"number": p.phase_number, "name": p.phase_name, "status": p.status, "notes": p.notes or ""} for p in phases],
        "themes": theme_rows,
        "codes": code_rows,
        "theme_frequency_per_conversation": theme_frequency_per_conversation(session, run_id),
        "code_frequency_per_speaker": code_frequency_per_speaker(session, run_id),
        "code_cooccurrence": code_cooccurrence(session, run_id),
        "theme_development_over_turn_order": theme_development_over_turn_order(session, run_id),
        "representative_quotes": representative_quotes(session, run_id),
        "trustworthiness": trustworthiness_summary(session, run_id),
        "reliability": cohens_kappa_binary(session, run_id),
        "disagreements": disagreement_table(session, run_id),
        "memos": [{"type": m.memo_type, "phase": m.related_phase, "text": m.text} for m in memos],
        "audit_trail": [{"phase": a.phase_number, "action": a.action_type, "description": a.description, "created_at": str(a.created_at)} for a in audit],
        "references": REFERENCES_APA,
        "limitations": [
            "Rule-based coding depends entirely on editable indicators in the codebook.",
            "Candidate themes are generated from configured code-to-theme relationships and require analyst review.",
            "Inter-coder agreement is optional and appropriate only for analytic orientations that use comparable coder assignments.",
            "The software records methodological structure and traceability; it does not determine the final interpretation.",
        ],
    }


def render_markdown(report: dict[str, object]) -> str:
    run = report["run"]  # type: ignore[index]
    codebook = report["codebook"]  # type: ignore[index]
    framework = report["framework"]  # type: ignore[index]
    counts = report["counts"]  # type: ignore[index]
    lines: list[str] = []
    lines.append(f"# Thematic Analysis Report: {run['name']}")
    lines.append("")
    lines.append("## Methodological framework")
    lines.append(methods_section_text())
    lines.append("")
    lines.append(f"Primary framework: {framework['primary']}")
    lines.append(f"Supporting frameworks: {', '.join(framework['supporting'])}")
    lines.append(f"Analysis orientation: {framework['analysis_orientation']}")
    lines.append(f"Coding orientation: {framework['coding_orientation']}")
    lines.append(f"Theme orientation: {framework['theme_orientation']}")
    lines.append(f"Epistemological position: {framework['epistemological_position']}")
    lines.append("")
    lines.append("## Codebook version")
    lines.append(f"{codebook['name']} — version {codebook['version']}. {codebook['description']}")
    lines.append("")
    lines.append("## Dataset counts")
    lines.append(markdown_table([counts]))
    lines.append("## Braun & Clarke phase status")
    lines.append(markdown_table(report["phases"]))  # type: ignore[arg-type]
    lines.append("## Theme summaries")
    lines.append(markdown_table(report["themes"]))  # type: ignore[arg-type]
    lines.append("## Code summaries")
    lines.append(markdown_table(report["codes"]))  # type: ignore[arg-type]
    lines.append("## Theme frequency per conversation")
    lines.append(markdown_table(report["theme_frequency_per_conversation"]))  # type: ignore[arg-type]
    lines.append("## Code frequency per speaker")
    lines.append(markdown_table(report["code_frequency_per_speaker"]))  # type: ignore[arg-type]
    lines.append("## Code co-occurrence")
    lines.append(markdown_table(report["code_cooccurrence"]))  # type: ignore[arg-type]
    lines.append("## Representative quotes")
    for code, quotes in report["representative_quotes"].items():  # type: ignore[union-attr]
        lines.append(f"### {code}")
        for quote in quotes:
            lines.append(f"> {quote}")
    lines.append("")
    lines.append("## Trustworthiness and auditability")
    lines.append(markdown_table([report["trustworthiness"]]))  # type: ignore[list-item]
    lines.append("## Reliability and adjudication")
    lines.append(markdown_table([report["reliability"]]))  # type: ignore[list-item]
    lines.append("### Disagreements")
    lines.append(markdown_table(report["disagreements"]))  # type: ignore[arg-type]
    lines.append("## Memos")
    lines.append(markdown_table(report["memos"]))  # type: ignore[arg-type]
    lines.append("## Audit trail summary")
    lines.append(markdown_table(report["audit_trail"]))  # type: ignore[arg-type]
    lines.append("## Limitations")
    lines.extend(f"- {item}" for item in report["limitations"])  # type: ignore[union-attr]
    lines.append("")
    lines.append("## References")
    lines.extend(f"- {ref}" for ref in report["references"])  # type: ignore[union-attr]
    return "\n".join(lines) + "\n"


def export_report(session: Session, run_id: int, output_format: str, out_path: str | Path) -> Path:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    report = build_report_data(session, run_id)
    fmt = output_format.lower()
    if fmt == "json":
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    elif fmt == "markdown" or fmt == "md":
        path.write_text(render_markdown(report), encoding="utf-8")
    elif fmt == "html":
        markdown = render_markdown(report)
        body = markdown.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        path.write_text(f"<html><body><pre>{body}</pre></body></html>", encoding="utf-8")
    elif fmt == "csv":
        rows = report["themes"] if report["themes"] else []
        pd.DataFrame(rows).to_csv(path, index=False)
    else:
        raise ValueError(f"Unsupported export format: {output_format}")
    session.add(ExportRecord(analysis_run_id=run_id, export_format=fmt, path=str(path)))
    session.flush()
    return path
