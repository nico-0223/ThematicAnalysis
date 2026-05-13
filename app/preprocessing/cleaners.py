from __future__ import annotations

import re


def conservative_clean(text: str, normalize_whitespace: bool = True, strip: bool = True) -> str:
    cleaned = text.strip() if strip else text
    if normalize_whitespace:
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned
