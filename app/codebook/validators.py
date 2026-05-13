from __future__ import annotations

import yaml
from pathlib import Path

from app.codebook.schema import CodebookFile


def load_and_validate_codebook(path: str | Path) -> CodebookFile:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Codebook YAML must contain a mapping at the root.")
    return CodebookFile.model_validate(data)
