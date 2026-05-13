from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Speaker, Turn
from app.framework.audit_trail import record_audit_event
from app.ingestion.parsers import parse_records
from app.ingestion.validators import validate_turn_record


def _clean_metadata(record: dict[str, Any]) -> str | None:
    known = {"conversation_id", "external_id", "title", "source", "speaker_label", "role", "turn_index", "text", "timestamp", "metadata_json"}
    metadata = {k: v for k, v in record.items() if k not in known and v not in (None, "")}
    if record.get("metadata_json"):
        try:
            metadata.update(json.loads(str(record["metadata_json"])))
        except json.JSONDecodeError:
            metadata["metadata_json_raw"] = record["metadata_json"]
    return json.dumps(metadata, ensure_ascii=False, sort_keys=True) if metadata else None


def _get_or_create_conversation(session: Session, external_id: str, title: str | None, source: str | None) -> Conversation:
    conversation = session.scalar(select(Conversation).where(Conversation.external_id == external_id))
    if conversation:
        return conversation
    conversation = Conversation(external_id=external_id, title=title or external_id, source=source, metadata_json=None)
    session.add(conversation)
    session.flush()
    return conversation


def _get_or_create_speaker(session: Session, conversation_id: int, label: str, role: str | None) -> Speaker:
    speaker = session.scalar(select(Speaker).where(Speaker.conversation_id == conversation_id, Speaker.speaker_label == label))
    if speaker:
        return speaker
    speaker = Speaker(conversation_id=conversation_id, speaker_label=label, role=role, metadata_json=None)
    session.add(speaker)
    session.flush()
    return speaker


def ingest_file(session: Session, path: str | Path, input_format: str) -> int:
    records = parse_records(path, input_format)
    imported = 0
    for raw in records:
        record = dict(raw)
        validate_turn_record(record)
        external_id = str(record.get("conversation_id") or record.get("external_id"))
        conversation = _get_or_create_conversation(session, external_id, str(record.get("title") or external_id), str(record.get("source") or Path(path).name))
        speaker = _get_or_create_speaker(session, conversation.id, str(record["speaker_label"]), str(record.get("role") or "participant"))
        turn_index = int(record["turn_index"])
        existing = session.scalar(select(Turn).where(Turn.conversation_id == conversation.id, Turn.turn_index == turn_index))
        if existing:
            continue
        turn = Turn(
            conversation_id=conversation.id,
            speaker_id=speaker.id,
            turn_index=turn_index,
            text=str(record["text"]),
            timestamp=str(record.get("timestamp") or "") or None,
            metadata_json=_clean_metadata(record),
        )
        session.add(turn)
        imported += 1
    session.flush()
    record_audit_event(
        session,
        analysis_run_id=None,
        phase_number=1,
        action_type="ingest_conversations",
        description=f"Ingested {imported} turns from {path}.",
        after_state={"path": str(path), "format": input_format, "turns_imported": imported},
    )
    return imported
