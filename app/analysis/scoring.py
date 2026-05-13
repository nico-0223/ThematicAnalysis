from __future__ import annotations


def confidence_summary(confidences: list[float | None]) -> dict[str, float]:
    values = [float(c) for c in confidences if c is not None]
    if not values:
        return {"count": 0, "mean": 0.0, "minimum": 0.0, "maximum": 0.0}
    return {
        "count": float(len(values)),
        "mean": sum(values) / len(values),
        "minimum": min(values),
        "maximum": max(values),
    }
