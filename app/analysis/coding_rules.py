from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.db.models import Code
from app.preprocessing.normalizers import normalize_for_matching


@dataclass(frozen=True)
class RuleMatch:
    matched: bool
    evidence: str | None
    confidence: float
    rationale: str


def load_indicators(code: Code) -> list[str]:
    if not code.indicators_json:
        return []
    try:
        return list(json.loads(code.indicators_json))
    except json.JSONDecodeError:
        return []


def match_code(segment_text: str, code: Code) -> RuleMatch:
    indicators = load_indicators(code)
    if not indicators:
        return RuleMatch(False, None, 0.0, "No indicators configured for this code.")
    lowered = normalize_for_matching(segment_text)
    matches: list[str] = []
    for indicator in indicators:
        if indicator.startswith("regex:"):
            pattern = indicator.removeprefix("regex:").strip()
            if re.search(pattern, segment_text, flags=re.IGNORECASE):
                matches.append(indicator)
        elif normalize_for_matching(indicator) in lowered:
            matches.append(indicator)
    if not matches:
        return RuleMatch(False, None, 0.0, "No configured indicators were found in the segment.")
    confidence = min(1.0, 0.55 + 0.15 * len(matches))
    return RuleMatch(True, "; ".join(matches), confidence, f"Matched configured indicator(s): {', '.join(matches)}")
