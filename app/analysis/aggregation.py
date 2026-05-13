from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Annotation, Code, Conversation, Segment, Speaker, Theme, Turn


def theme_frequency_per_conversation(session: Session, run_id: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    annotations = session.scalars(select(Annotation).where(Annotation.analysis_run_id == run_id)).all()
    counter: Counter[tuple[str, str]] = Counter()
    for ann in annotations:
        segment = session.get(Segment, ann.segment_id)
        code = session.get(Code, ann.code_id)
        if not segment or not code:
            continue
        turn = session.get(Turn, segment.turn_id)
        theme = session.get(Theme, code.theme_id)
        conversation = session.get(Conversation, turn.conversation_id) if turn else None
        if conversation and theme:
            counter[(conversation.external_id or str(conversation.id), theme.name)] += 1
    for (conversation_id, theme_name), count in counter.items():
        rows.append({"conversation_id": conversation_id, "theme": theme_name, "count": count})
    return rows


def code_frequency_per_speaker(session: Session, run_id: int) -> list[dict[str, object]]:
    counter: Counter[tuple[str, str]] = Counter()
    for ann in session.scalars(select(Annotation).where(Annotation.analysis_run_id == run_id)).all():
        segment = session.get(Segment, ann.segment_id)
        code = session.get(Code, ann.code_id)
        turn = session.get(Turn, segment.turn_id) if segment else None
        speaker = session.get(Speaker, turn.speaker_id) if turn and turn.speaker_id else None
        if speaker and code:
            counter[(speaker.speaker_label, code.name)] += 1
    return [{"speaker": speaker, "code": code, "count": count} for (speaker, code), count in counter.items()]


def code_cooccurrence(session: Session, run_id: int) -> list[dict[str, object]]:
    by_segment: dict[int, set[str]] = defaultdict(set)
    for ann in session.scalars(select(Annotation).where(Annotation.analysis_run_id == run_id)).all():
        code = session.get(Code, ann.code_id)
        if code:
            by_segment[ann.segment_id].add(code.name)
    counter: Counter[tuple[str, str]] = Counter()
    for codes in by_segment.values():
        for first, second in combinations(sorted(codes), 2):
            counter[(first, second)] += 1
    return [{"code_a": a, "code_b": b, "count": count} for (a, b), count in counter.items()]


def representative_quotes(session: Session, run_id: int, limit_per_code: int = 3) -> dict[str, list[str]]:
    quotes: dict[str, list[str]] = defaultdict(list)
    annotations = session.scalars(select(Annotation).where(Annotation.analysis_run_id == run_id).order_by(Annotation.confidence.desc())).all()
    for ann in annotations:
        code = session.get(Code, ann.code_id)
        segment = session.get(Segment, ann.segment_id)
        if code and segment and len(quotes[code.name]) < limit_per_code:
            quotes[code.name].append(segment.text)
    return dict(quotes)


def theme_development_over_turn_order(session: Session, run_id: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for ann in session.scalars(select(Annotation).where(Annotation.analysis_run_id == run_id)).all():
        segment = session.get(Segment, ann.segment_id)
        code = session.get(Code, ann.code_id)
        turn = session.get(Turn, segment.turn_id) if segment else None
        theme = session.get(Theme, code.theme_id) if code else None
        if turn and theme:
            rows.append({"conversation_id": turn.conversation_id, "turn_index": turn.turn_index, "theme": theme.name})
    return sorted(rows, key=lambda item: (int(item["conversation_id"]), int(item["turn_index"])))
