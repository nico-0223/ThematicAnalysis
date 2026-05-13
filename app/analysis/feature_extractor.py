from __future__ import annotations

from app.db.models import CodingFeature


def extract_rule_based_features(segment_text: str, features: list[CodingFeature]) -> dict[str, str | None]:
    values: dict[str, str | None] = {}
    text = segment_text.casefold()
    for feature in features:
        value: str | None = None
        if feature.name == "explanatory_depth":
            markers = ["because", "therefore", "reason", "cause", "goal", "in order to", "so that"]
            count = sum(1 for marker in markers if marker in text)
            value = "high" if count >= 2 else "medium" if count == 1 else "low"
        elif feature.name == "speaker_positioning":
            if any(marker in text for marker in ["maybe", "perhaps", "i think", "not sure"]):
                value = "uncertain"
            elif any(marker in text for marker in ["we", "together", "shared"]):
                value = "collaborative"
            else:
                value = None
        values[feature.name] = value
    return values
