from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Memo
from app.framework.audit_trail import record_audit_event


def add_memo(session: Session, text: str, memo_type: str, related_phase: str | None = None, conversation_id: int | None = None, segment_id: int | None = None, coder_id: int | None = None, run_id: int | None = None) -> Memo:
    memo = Memo(conversation_id=conversation_id, segment_id=segment_id, coder_id=coder_id, memo_type=memo_type, text=text, related_phase=related_phase)
    session.add(memo)
    session.flush()
    record_audit_event(session, run_id, None, "memo", f"Added {memo_type} memo.", after_state={"memo_id": memo.id, "related_phase": related_phase})
    return memo
