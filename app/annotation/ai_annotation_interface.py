from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIAnnotationProvider(ABC):
    @abstractmethod
    def suggest_codes(self, segment_text: str, codebook_context: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def extract_features(self, segment_text: str, feature_schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_rationale(self, segment_text: str, assigned_code: dict[str, Any]) -> str:
        raise NotImplementedError

    @abstractmethod
    def suggest_candidate_themes(self, coded_segments: list[dict[str, Any]], codebook_context: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError


class DummyAIAnnotationProvider(AIAnnotationProvider):
    """Deterministic test double. It is not a production LLM provider."""

    def suggest_codes(self, segment_text: str, codebook_context: dict[str, Any]) -> list[dict[str, Any]]:
        return [{"code": "dummy", "confidence": 0.0, "reason": "Dummy provider does not infer substantive codes."}]

    def extract_features(self, segment_text: str, feature_schema: dict[str, Any]) -> dict[str, Any]:
        return {"provider": "dummy", "features": {}}

    def generate_rationale(self, segment_text: str, assigned_code: dict[str, Any]) -> str:
        return "Dummy rationale for tests only."

    def suggest_candidate_themes(self, coded_segments: list[dict[str, Any]], codebook_context: dict[str, Any]) -> list[dict[str, Any]]:
        return []
