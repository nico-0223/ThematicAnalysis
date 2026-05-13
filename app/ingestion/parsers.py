from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd


def parse_csv(path: str | Path) -> list[dict[str, object]]:
    frame = pd.read_csv(path)
    return frame.fillna("").to_dict(orient="records")


def parse_json(path: str | Path) -> list[dict[str, object]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "turns" in data:
        return list(data["turns"])
    if isinstance(data, list):
        return data
    raise ValueError("JSON input must be a list of turn records or a mapping with a 'turns' list.")


def parse_jsonl(path: str | Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def parse_txt(path: str | Path) -> list[dict[str, object]]:
    text = Path(path).read_text(encoding="utf-8")
    records: list[dict[str, object]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        speaker = "unknown"
        content = line
        if ":" in line:
            left, right = line.split(":", 1)
            if left.strip() and right.strip():
                speaker = left.strip()
                content = right.strip()
        records.append({"conversation_id": Path(path).stem, "speaker_label": speaker, "turn_index": idx, "text": content})
    return records


def parse_records(path: str | Path, input_format: str) -> list[dict[str, object]]:
    fmt = input_format.lower()
    if fmt == "csv":
        return parse_csv(path)
    if fmt == "json":
        return parse_json(path)
    if fmt == "jsonl":
        return parse_jsonl(path)
    if fmt == "txt":
        return parse_txt(path)
    raise ValueError(f"Unsupported input format: {input_format}")
