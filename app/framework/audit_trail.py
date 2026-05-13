from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AuditTrailEntry


def _json(data: Any) -> str | None:
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)


def record_audit_event(
    session: Session,
    analysis_run_id: int | None,
    phase_number: int | None,
    action_type: str,
    description: str,
    before_state: Any | None = None,
    after_state: Any | None = None,
) -> AuditTrailEntry:
    entry = AuditTrailEntry(
        analysis_run_id=analysis_run_id,
        phase_number=phase_number,
        action_type=action_type,
        description=description,
        before_state_json=_json(before_state),
        after_state_json=_json(after_state),
    )
    session.add(entry)
    session.flush()
    return entry
