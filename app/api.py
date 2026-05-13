from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analysis.coding_rules import match_code
from app.analysis.reliability import cohens_kappa_binary, coder_comparison, disagreement_table
from app.analysis.thematic_engine import apply_rule_based_codes, get_or_create_coder, start_analysis_run
from app.codebook.loader import load_codebook
from app.codebook.validators import load_and_validate_codebook
from app.config import get_settings
from app.db.database import init_database, session_scope
from app.db.models import (
    AdjudicationRecord,
    AnalysisRun,
    Annotation,
    AuditTrailEntry,
    CandidateTheme,
    Code,
    CodebookVersion,
    Conversation,
    ExportRecord,
    Memo,
    MethodologicalPhase,
    Segment,
    Theme,
    Turn,
)
from app.framework.audit_trail import record_audit_event
from app.framework.braun_clarke import create_phase_records, set_phase_status
from app.ingestion.loaders import ingest_file
from app.preprocessing.segmenters import preprocess_turns
from app.reports.exporters import export_report

settings = get_settings()
app = FastAPI(title="Conversation Thematic Analysis API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunCreate(BaseModel):
    name: str
    codebook_id: str | None = None
    codebook_version: str | None = None
    run_type: str = "rule_based"
    configuration: dict[str, Any] | None = None


class PhaseUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


class PreprocessingRequest(BaseModel):
    strategy: str = "turn"
    fixed_size: int | None = None


class AnnotationBody(BaseModel):
    segment_id: str
    code_id: str
    confidence: float | None = None
    rationale: str | None = None
    evidence: str | None = None
    decision_note: str | None = None
    source: str = "human"


class MemoBody(BaseModel):
    type: str = "general"
    title: str | None = None
    body: str
    link_type: str | None = None
    link_id: str | None = None
    phase_number: int | None = None


class ExportBody(BaseModel):
    run_id: str
    format: str = "markdown"


class ThemePatch(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    review_rationale: str | None = None


class ThemeMerge(BaseModel):
    ids: list[str]
    name: str


class ThemeSplit(BaseModel):
    parts: list[dict[str, Any]]


class DisagreementPatch(BaseModel):
    resolved: bool
    note: str | None = None


def _json(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _require_int(value: str, label: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"{label} must be an integer") from exc


def _format_input(filename: str) -> str:
    suffix = Path(filename).suffix.lower().lstrip(".")
    if suffix in {"csv", "json", "jsonl", "txt"}:
        return suffix
    raise HTTPException(status_code=400, detail="Unsupported conversation file type")


def _write_upload(upload: UploadFile) -> Path:
    suffix = Path(upload.filename or "").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(upload.file.read())
        return Path(handle.name)


def _conversation(session: Session, conversation: Conversation) -> dict[str, Any]:
    speakers = [speaker.speaker_label for speaker in conversation.speakers]
    segment_count = session.scalar(
        select(func.count(Segment.id)).join(Turn).where(Turn.conversation_id == conversation.id)
    )
    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "source": conversation.source,
        "speakers": speakers,
        "turns_count": len(conversation.turns),
        "segments_count": segment_count or 0,
        "imported_at": conversation.created_at.isoformat(),
    }


def _turn(turn: Turn) -> dict[str, Any]:
    return {
        "id": str(turn.id),
        "conversation_id": str(turn.conversation_id),
        "index": turn.turn_index,
        "speaker": turn.speaker.speaker_label if turn.speaker else None,
        "text": turn.text,
    }


def _segment(segment: Segment) -> dict[str, Any]:
    turn = segment.turn
    return {
        "id": str(segment.id),
        "conversation_id": str(turn.conversation_id),
        "turn_id": str(segment.turn_id),
        "index": segment.segment_index,
        "text": segment.text,
        "speaker": turn.speaker.speaker_label if turn.speaker else None,
    }


def _code(code: Code) -> dict[str, Any]:
    return {
        "id": str(code.id),
        "name": code.name,
        "description": code.description,
        "indicators": _json(code.indicators_json, []),
        "inclusion_criteria": _json(code.inclusion_criteria, []),
        "exclusion_criteria": _json(code.exclusion_criteria, []),
        "examples": _json(code.examples_json, []),
        "counterexamples": _json(code.counterexamples_json, []),
    }


def _codebook(session: Session, codebook: CodebookVersion, full: bool = False) -> dict[str, Any]:
    themes = session.scalars(select(Theme).where(Theme.codebook_version_id == codebook.id).order_by(Theme.id)).all()
    codes_count = session.scalar(select(func.count(Code.id)).join(Theme).where(Theme.codebook_version_id == codebook.id))
    data: dict[str, Any] = {
        "id": str(codebook.id),
        "name": codebook.name,
        "version": codebook.version,
        "framework": codebook.theoretical_framework,
        "themes_count": len(themes),
        "codes_count": codes_count or 0,
        "updated_at": codebook.created_at.isoformat(),
    }
    if full:
        data.update(
            {
                "metadata": {"description": codebook.description, "active": codebook.is_active},
                "framework_settings": {"theoretical_framework": _json(codebook.theoretical_framework, {})},
                "themes": [
                    {
                        "id": str(theme.id),
                        "name": theme.name,
                        "description": theme.description,
                        "codes": [_code(code) for code in sorted(theme.codes, key=lambda item: item.id)],
                    }
                    for theme in themes
                ],
            }
        )
    return data


def _run(session: Session, run: AnalysisRun) -> dict[str, Any]:
    codebook = session.get(CodebookVersion, run.codebook_version_id)
    annotations = session.scalar(select(func.count(Annotation.id)).where(Annotation.analysis_run_id == run.id)) or 0
    candidates = session.scalar(select(func.count(CandidateTheme.id)).where(CandidateTheme.analysis_run_id == run.id)) or 0
    completed_phase = session.scalar(
        select(MethodologicalPhase).where(
            MethodologicalPhase.analysis_run_id == run.id,
            MethodologicalPhase.phase_number == 6,
            MethodologicalPhase.status == "completed",
        )
    )
    return {
        "id": str(run.id),
        "name": run.run_name,
        "codebook_id": str(run.codebook_version_id),
        "codebook_version": codebook.version if codebook else None,
        "run_type": run.run_type,
        "status": "completed" if completed_phase else "running" if annotations else "draft",
        "configuration": _json(run.config_json, {}),
        "created_at": run.created_at.isoformat(),
        "annotation_count": annotations,
        "candidate_theme_count": candidates,
    }


def _phase(phase: MethodologicalPhase) -> dict[str, Any]:
    return {
        "id": str(phase.id),
        "run_id": str(phase.analysis_run_id),
        "number": phase.phase_number,
        "name": phase.phase_name,
        "description": phase.framework_reference,
        "status": phase.status,
        "notes": phase.notes,
        "started_at": phase.started_at.isoformat() if phase.started_at else None,
        "completed_at": phase.completed_at.isoformat() if phase.completed_at else None,
    }


def _annotation(annotation: Annotation) -> dict[str, Any]:
    source = "rule_based" if annotation.coder.name == "rule_based_system" else "human"
    return {
        "id": str(annotation.id),
        "run_id": str(annotation.analysis_run_id),
        "segment_id": str(annotation.segment_id),
        "conversation_id": str(annotation.segment.turn.conversation_id),
        "code_id": str(annotation.code_id),
        "code_name": annotation.code.name,
        "source": source,
        "confidence": annotation.confidence,
        "rationale": annotation.rationale,
        "evidence": annotation.evidence_text,
        "created_at": annotation.created_at.isoformat(),
    }


def _candidate_theme(theme: CandidateTheme) -> dict[str, Any]:
    return {
        "id": str(theme.id),
        "run_id": str(theme.analysis_run_id),
        "name": theme.name,
        "description": theme.description,
        "status": theme.review_status,
        "supporting_code_ids": [str(item) for item in _json(theme.supporting_codes_json, [])],
        "supporting_segment_ids": [str(item) for item in _json(theme.supporting_segments_json, [])],
        "review_rationale": theme.rationale,
    }


def _memo(memo: Memo) -> dict[str, Any]:
    return {
        "id": str(memo.id),
        "type": memo.memo_type,
        "body": memo.text,
        "link_type": "conversation" if memo.conversation_id else "segment" if memo.segment_id else None,
        "link_id": str(memo.conversation_id or memo.segment_id) if memo.conversation_id or memo.segment_id else None,
        "phase_number": int(memo.related_phase) if memo.related_phase and memo.related_phase.isdigit() else None,
        "created_at": memo.created_at.isoformat(),
    }


def _audit(entry: AuditTrailEntry) -> dict[str, Any]:
    return {
        "id": str(entry.id),
        "timestamp": entry.created_at.isoformat(),
        "run_id": str(entry.analysis_run_id) if entry.analysis_run_id else None,
        "phase_number": entry.phase_number,
        "action_type": entry.action_type,
        "description": entry.description,
        "before": _json(entry.before_state_json, None),
        "after": _json(entry.after_state_json, None),
    }


def _export(record: ExportRecord) -> dict[str, Any]:
    return {
        "id": str(record.id),
        "run_id": str(record.analysis_run_id),
        "format": record.export_format,
        "status": "ready" if Path(record.path).exists() else "failed",
        "file_url": f"/api/exports/{record.id}/download",
        "created_at": record.created_at.isoformat(),
    }


@app.on_event("startup")
def startup() -> None:
    init_database()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/codebooks")
def list_codebooks() -> list[dict[str, Any]]:
    with session_scope() as session:
        rows = session.scalars(select(CodebookVersion).order_by(CodebookVersion.created_at.desc())).all()
        return [_codebook(session, row) for row in rows]


@app.get("/api/codebooks/{codebook_id}")
def get_codebook(codebook_id: str) -> dict[str, Any]:
    with session_scope() as session:
        codebook = session.get(CodebookVersion, _require_int(codebook_id, "codebook_id"))
        if not codebook:
            raise HTTPException(status_code=404, detail="Codebook not found")
        return _codebook(session, codebook, full=True)


@app.post("/api/codebooks/upload")
def upload_codebook(file: UploadFile = File(...)) -> dict[str, Any]:
    path = _write_upload(file)
    try:
        with session_scope() as session:
            codebook = load_codebook(session, path)
            return _codebook(session, codebook, full=True)
    finally:
        path.unlink(missing_ok=True)


@app.post("/api/codebooks/validate")
def validate_codebook(file: UploadFile = File(...)) -> dict[str, Any]:
    path = _write_upload(file)
    try:
        load_and_validate_codebook(path)
        return {"valid": True, "errors": []}
    except Exception as exc:
        return {"valid": False, "errors": [str(exc)]}
    finally:
        path.unlink(missing_ok=True)


@app.get("/api/codebooks/{codebook_id}/versions")
def codebook_versions(codebook_id: str) -> list[dict[str, str]]:
    with session_scope() as session:
        codebook = session.get(CodebookVersion, _require_int(codebook_id, "codebook_id"))
        if not codebook:
            raise HTTPException(status_code=404, detail="Codebook not found")
        rows = session.scalars(select(CodebookVersion).where(CodebookVersion.name == codebook.name).order_by(CodebookVersion.created_at.desc())).all()
        return [{"version": row.version, "created_at": row.created_at.isoformat()} for row in rows]


@app.get("/api/conversations")
def list_conversations() -> list[dict[str, Any]]:
    with session_scope() as session:
        rows = session.scalars(select(Conversation).order_by(Conversation.created_at.desc())).unique().all()
        return [_conversation(session, row) for row in rows]


@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str) -> dict[str, Any]:
    with session_scope() as session:
        conversation = session.get(Conversation, _require_int(conversation_id, "conversation_id"))
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return _conversation(session, conversation)


@app.get("/api/conversations/{conversation_id}/turns")
def conversation_turns(conversation_id: str) -> list[dict[str, Any]]:
    with session_scope() as session:
        rows = session.scalars(select(Turn).where(Turn.conversation_id == _require_int(conversation_id, "conversation_id")).order_by(Turn.turn_index)).all()
        return [_turn(row) for row in rows]


@app.get("/api/conversations/{conversation_id}/segments")
def conversation_segments(conversation_id: str, speaker: str | None = None, q: str | None = None) -> list[dict[str, Any]]:
    with session_scope() as session:
        rows = session.scalars(select(Segment).join(Turn).where(Turn.conversation_id == _require_int(conversation_id, "conversation_id")).order_by(Segment.id)).all()
        data = [_segment(row) for row in rows]
        if speaker:
            data = [row for row in data if row.get("speaker") == speaker]
        if q:
            data = [row for row in data if q.lower() in row["text"].lower()]
        return data


@app.post("/api/conversations/import")
def import_conversations(file: UploadFile = File(...)) -> dict[str, Any]:
    path = _write_upload(file)
    try:
        with session_scope() as session:
            before = {row.id for row in session.scalars(select(Conversation)).all()}
            imported = ingest_file(session, path, _format_input(file.filename or ""))
            after = {row.id for row in session.scalars(select(Conversation)).all()}
            return {"imported": imported, "conversation_ids": [str(item) for item in sorted(after - before)]}
    finally:
        path.unlink(missing_ok=True)


@app.post("/api/preprocessing")
def preprocessing(body: PreprocessingRequest) -> dict[str, Any]:
    strategy = {"fixed_size": "fixed", "custom_placeholder": "custom"}.get(body.strategy, body.strategy)
    with session_scope() as session:
        count = preprocess_turns(session, strategy=strategy, chunk_size=body.fixed_size or 80)
        preview_rows = session.scalars(select(Segment).order_by(Segment.id.desc()).limit(5)).all()
        return {
            "segments_created": count,
            "conversations_processed": session.scalar(select(func.count(Conversation.id))) or 0,
            "preview": [
                {"conversation_id": str(row.turn.conversation_id), "segment_id": str(row.id), "text": row.text}
                for row in reversed(preview_rows)
            ],
        }


@app.get("/api/runs")
def list_runs() -> list[dict[str, Any]]:
    with session_scope() as session:
        return [_run(session, row) for row in session.scalars(select(AnalysisRun).order_by(AnalysisRun.created_at.desc())).all()]


@app.post("/api/runs")
def create_run(body: RunCreate) -> dict[str, Any]:
    with session_scope() as session:
        codebook = None
        if body.codebook_id:
            codebook = session.get(CodebookVersion, _require_int(body.codebook_id, "codebook_id"))
        if codebook is None and body.codebook_version:
            codebook = session.scalar(select(CodebookVersion).where(CodebookVersion.version == body.codebook_version).order_by(CodebookVersion.id.desc()))
        if codebook is None:
            raise HTTPException(status_code=404, detail="Codebook not found")
        run = start_analysis_run(session, codebook.version, body.name, body.run_type, body.configuration)
        return _run(session, run)


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    with session_scope() as session:
        run = session.get(AnalysisRun, _require_int(run_id, "run_id"))
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return _run(session, run)


@app.post("/api/runs/{run_id}/start")
def start_run(run_id: str) -> dict[str, Any]:
    with session_scope() as session:
        run = session.get(AnalysisRun, _require_int(run_id, "run_id"))
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        apply_rule_based_codes(session, run.id)
        return _run(session, run)


@app.post("/api/runs/{run_id}/cancel")
def cancel_run(run_id: str) -> dict[str, Any]:
    with session_scope() as session:
        run = session.get(AnalysisRun, _require_int(run_id, "run_id"))
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        record_audit_event(session, run.id, None, "cancel_run", f"Cancelled run '{run.run_name}'.")
        return _run(session, run)


@app.get("/api/runs/{run_id}/phases")
def list_phases(run_id: str) -> list[dict[str, Any]]:
    with session_scope() as session:
        run = session.get(AnalysisRun, _require_int(run_id, "run_id"))
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        create_phase_records(session, run)
        rows = session.scalars(select(MethodologicalPhase).where(MethodologicalPhase.analysis_run_id == run.id).order_by(MethodologicalPhase.phase_number)).all()
        return [_phase(row) for row in rows]


@app.patch("/api/runs/{run_id}/phases/{phase_number}")
def update_phase(run_id: str, phase_number: int, body: PhaseUpdate) -> dict[str, Any]:
    with session_scope() as session:
        phase = set_phase_status(
            session,
            _require_int(run_id, "run_id"),
            phase_number,
            complete=body.status == "completed",
            notes=body.notes,
        )
        if body.status == "not_started":
            phase.status = "not_started"
        return _phase(phase)


@app.get("/api/runs/{run_id}/annotations")
def list_annotations(run_id: str) -> list[dict[str, Any]]:
    with session_scope() as session:
        rows = session.scalars(select(Annotation).where(Annotation.analysis_run_id == _require_int(run_id, "run_id")).order_by(Annotation.created_at.desc())).all()
        return [_annotation(row) for row in rows]


@app.post("/api/runs/{run_id}/annotations")
def upsert_annotation(run_id: str, body: AnnotationBody) -> dict[str, Any]:
    with session_scope() as session:
        coder = get_or_create_coder(session, "human")
        annotation = Annotation(
            analysis_run_id=_require_int(run_id, "run_id"),
            segment_id=_require_int(body.segment_id, "segment_id"),
            code_id=_require_int(body.code_id, "code_id"),
            coder_id=coder.id,
            confidence=body.confidence,
            rationale=body.rationale or body.decision_note,
            evidence_text=body.evidence,
        )
        session.add(annotation)
        session.flush()
        return _annotation(annotation)


@app.delete("/api/runs/{run_id}/annotations/{annotation_id}", status_code=204)
def delete_annotation(run_id: str, annotation_id: str) -> None:
    with session_scope() as session:
        annotation = session.get(Annotation, _require_int(annotation_id, "annotation_id"))
        if annotation and annotation.analysis_run_id == _require_int(run_id, "run_id"):
            session.delete(annotation)


@app.get("/api/runs/{run_id}/segments/{segment_id}/suggestions")
def annotation_suggestions(run_id: str, segment_id: str) -> list[dict[str, Any]]:
    with session_scope() as session:
        run = session.get(AnalysisRun, _require_int(run_id, "run_id"))
        segment = session.get(Segment, _require_int(segment_id, "segment_id"))
        if not run or not segment:
            raise HTTPException(status_code=404, detail="Run or segment not found")
        codes = session.scalars(select(Code).join(Theme).where(Theme.codebook_version_id == run.codebook_version_id)).all()
        suggestions = []
        for code in codes:
            rule_match = match_code(segment.text, code)
            if rule_match.matched:
                suggestions.append(
                    {
                        "id": f"suggestion-{code.id}",
                        "run_id": run_id,
                        "segment_id": segment_id,
                        "code_id": str(code.id),
                        "code_name": code.name,
                        "source": "rule_based",
                        "confidence": rule_match.confidence,
                        "rationale": rule_match.rationale,
                        "evidence": rule_match.evidence,
                    }
                )
        return suggestions


@app.get("/api/runs/{run_id}/candidate-themes")
def list_candidate_themes(run_id: str) -> list[dict[str, Any]]:
    with session_scope() as session:
        rows = session.scalars(select(CandidateTheme).where(CandidateTheme.analysis_run_id == _require_int(run_id, "run_id")).order_by(CandidateTheme.id)).all()
        return [_candidate_theme(row) for row in rows]


@app.patch("/api/runs/{run_id}/candidate-themes/{theme_id}")
def update_candidate_theme(run_id: str, theme_id: str, body: ThemePatch) -> dict[str, Any]:
    with session_scope() as session:
        theme = session.get(CandidateTheme, _require_int(theme_id, "theme_id"))
        if not theme or theme.analysis_run_id != _require_int(run_id, "run_id"):
            raise HTTPException(status_code=404, detail="Candidate theme not found")
        if body.name is not None:
            theme.name = body.name
        if body.description is not None:
            theme.description = body.description
        if body.status is not None:
            theme.review_status = body.status
        if body.review_rationale is not None:
            theme.rationale = body.review_rationale
        session.flush()
        return _candidate_theme(theme)


@app.post("/api/runs/{run_id}/candidate-themes/merge")
def merge_candidate_themes(run_id: str, body: ThemeMerge) -> dict[str, Any]:
    with session_scope() as session:
        ids = [_require_int(item, "theme_id") for item in body.ids]
        themes = session.scalars(select(CandidateTheme).where(CandidateTheme.id.in_(ids), CandidateTheme.analysis_run_id == _require_int(run_id, "run_id"))).all()
        codes = sorted({code for theme in themes for code in _json(theme.supporting_codes_json, [])})
        segments = sorted({segment for theme in themes for segment in _json(theme.supporting_segments_json, [])})
        merged = CandidateTheme(
            analysis_run_id=_require_int(run_id, "run_id"),
            name=body.name,
            description="Merged candidate theme.",
            supporting_codes_json=json.dumps(codes),
            supporting_segments_json=json.dumps(segments),
            review_status="merged",
            rationale=f"Merged from candidate theme ids: {', '.join(body.ids)}",
        )
        for theme in themes:
            theme.review_status = "merged"
        session.add(merged)
        session.flush()
        return _candidate_theme(merged)


@app.post("/api/runs/{run_id}/candidate-themes/{theme_id}/split")
def split_candidate_theme(run_id: str, theme_id: str, body: ThemeSplit) -> list[dict[str, Any]]:
    with session_scope() as session:
        original = session.get(CandidateTheme, _require_int(theme_id, "theme_id"))
        if not original or original.analysis_run_id != _require_int(run_id, "run_id"):
            raise HTTPException(status_code=404, detail="Candidate theme not found")
        original.review_status = "split"
        created = []
        for part in body.parts:
            candidate = CandidateTheme(
                analysis_run_id=original.analysis_run_id,
                name=str(part.get("name") or f"{original.name} split"),
                description=original.description,
                supporting_codes_json=json.dumps(part.get("supporting_code_ids") or []),
                supporting_segments_json=original.supporting_segments_json,
                review_status="candidate",
                rationale=f"Split from candidate theme {original.id}.",
            )
            session.add(candidate)
            created.append(candidate)
        session.flush()
        return [_candidate_theme(row) for row in created]


@app.get("/api/memos")
def list_memos() -> list[dict[str, Any]]:
    with session_scope() as session:
        rows = session.scalars(select(Memo).order_by(Memo.created_at.desc())).all()
        return [_memo(row) for row in rows]


@app.post("/api/memos")
def create_memo(body: MemoBody) -> dict[str, Any]:
    with session_scope() as session:
        memo = Memo(
            memo_type=body.type,
            text=body.body,
            related_phase=str(body.phase_number) if body.phase_number else None,
            conversation_id=_require_int(body.link_id, "link_id") if body.link_type == "conversation" and body.link_id else None,
            segment_id=_require_int(body.link_id, "link_id") if body.link_type == "segment" and body.link_id else None,
        )
        session.add(memo)
        session.flush()
        return _memo(memo)


@app.put("/api/memos/{memo_id}")
def update_memo(memo_id: str, body: MemoBody) -> dict[str, Any]:
    with session_scope() as session:
        memo = session.get(Memo, _require_int(memo_id, "memo_id"))
        if not memo:
            raise HTTPException(status_code=404, detail="Memo not found")
        memo.memo_type = body.type
        memo.text = body.body
        memo.related_phase = str(body.phase_number) if body.phase_number else None
        session.flush()
        return _memo(memo)


@app.delete("/api/memos/{memo_id}", status_code=204)
def delete_memo(memo_id: str) -> None:
    with session_scope() as session:
        memo = session.get(Memo, _require_int(memo_id, "memo_id"))
        if memo:
            session.delete(memo)


@app.get("/api/audit")
def list_audit(run_id: str | None = None, phase_number: int | None = None, action_type: str | None = None) -> list[dict[str, Any]]:
    with session_scope() as session:
        query = select(AuditTrailEntry).order_by(AuditTrailEntry.created_at.desc())
        if run_id:
            query = query.where(AuditTrailEntry.analysis_run_id == _require_int(run_id, "run_id"))
        if phase_number:
            query = query.where(AuditTrailEntry.phase_number == phase_number)
        if action_type:
            query = query.where(AuditTrailEntry.action_type == action_type)
        return [_audit(row) for row in session.scalars(query).all()]


@app.get("/api/runs/{run_id}/reliability")
@app.post("/api/runs/{run_id}/reliability")
def reliability(run_id: str) -> dict[str, Any]:
    run_id_int = _require_int(run_id, "run_id")
    with session_scope() as session:
        comparison = coder_comparison(session, run_id_int)
        disagreements = disagreement_table(session, run_id_int)
        return {
            "run_id": run_id,
            "cohens_kappa": cohens_kappa_binary(session, run_id_int).get("cohens_kappa"),
            "comparison": comparison,
            "disagreements": [{"id": str(idx + 1), **row} for idx, row in enumerate(disagreements)],
        }


@app.patch("/api/runs/{run_id}/reliability/disagreements/{disagreement_id}", status_code=204)
def resolve_disagreement(run_id: str, disagreement_id: str, body: DisagreementPatch) -> None:
    with session_scope() as session:
        session.add(
            AdjudicationRecord(
                analysis_run_id=_require_int(run_id, "run_id"),
                segment_id=_require_int(disagreement_id, "disagreement_id"),
                decision="resolved" if body.resolved else "unresolved",
                rationale=body.note,
            )
        )


@app.get("/api/exports")
def list_exports(run_id: str | None = None) -> list[dict[str, Any]]:
    with session_scope() as session:
        query = select(ExportRecord).order_by(ExportRecord.created_at.desc())
        if run_id:
            query = query.where(ExportRecord.analysis_run_id == _require_int(run_id, "run_id"))
        return [_export(row) for row in session.scalars(query).all()]


@app.post("/api/exports")
def create_export(body: ExportBody) -> dict[str, Any]:
    with session_scope() as session:
        suffix = "md" if body.format == "markdown" else body.format
        path = settings.project_root / "data" / "exports" / f"run_{body.run_id}.{suffix}"
        export_report(session, _require_int(body.run_id, "run_id"), body.format, path)
        record = session.scalar(select(ExportRecord).where(ExportRecord.path == str(path)).order_by(ExportRecord.id.desc()))
        assert record is not None
        return _export(record)


@app.get("/api/exports/{export_id}/download")
def download_export(export_id: str) -> FileResponse:
    with session_scope() as session:
        record = session.get(ExportRecord, _require_int(export_id, "export_id"))
        if not record or not Path(record.path).exists():
            raise HTTPException(status_code=404, detail="Export not found")
        return FileResponse(record.path, filename=Path(record.path).name)
