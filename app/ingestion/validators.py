from __future__ import annotations

REQUIRED_FIELDS = {"conversation_id", "speaker_label", "turn_index", "text"}


def validate_turn_record(record: dict[str, object]) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in record or record[field] in (None, "")]
    if missing:
        raise ValueError(f"Turn record is missing required fields: {', '.join(missing)}")
    try:
        int(record["turn_index"])
    except (TypeError, ValueError) as exc:
        raise ValueError("turn_index must be an integer") from exc
