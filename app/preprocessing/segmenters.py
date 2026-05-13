from __future__ import annotations

import json
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Segment, Turn
from app.framework.audit_trail import record_audit_event
from app.preprocessing.cleaners import conservative_clean


def sentence_segments(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+", text.strip())
    return [piece for piece in pieces if piece]


def fixed_size_segments(text: str, size: int = 80) -> list[str]:
    words = text.split()
    if not words:
        return []
    return [" ".join(words[i : i + size]) for i in range(0, len(words), size)]


def segment_text(text: str, strategy: str = "turn", chunk_size: int = 80) -> list[str]:
    cleaned = conservative_clean(text)
    if strategy == "turn":
        return [cleaned] if cleaned else []
    if strategy == "sentence":
        return sentence_segments(cleaned)
    if strategy == "fixed":
        return fixed_size_segments(cleaned, chunk_size)
    if strategy == "custom":
        return [cleaned] if cleaned else []
    raise ValueError(f"Unsupported segmentation strategy: {strategy}")


def preprocess_turns(session: Session, strategy: str = "turn", chunk_size: int = 80) -> int:
    created = 0
    turns = session.scalars(select(Turn).order_by(Turn.conversation_id, Turn.turn_index)).all()
    for turn in turns:
        parts = segment_text(turn.text, strategy=strategy, chunk_size=chunk_size)
        for idx, part in enumerate(parts, start=1):
            existing = session.scalar(select(Segment).where(Segment.turn_id == turn.id, Segment.segment_index == idx, Segment.segmentation_strategy == strategy))
            if existing:
                continue
            session.add(
                Segment(
                    turn_id=turn.id,
                    segment_index=idx,
                    text=part,
                    segmentation_strategy=strategy,
                    original_text=turn.text,
                    metadata_json=json.dumps({"chunk_size": chunk_size}, sort_keys=True),
                )
            )
            created += 1
    session.flush()
    record_audit_event(
        session,
        analysis_run_id=None,
        phase_number=1,
        action_type="preprocess_segments",
        description=f"Created {created} segments using strategy '{strategy}'.",
        after_state={"strategy": strategy, "segments_created": created},
    )
    return created
