from pathlib import Path

import pytest
from sqlalchemy import select

from app.codebook.loader import load_codebook
from app.codebook.validators import load_and_validate_codebook
from app.db.models import CodebookVersion, CodingFeature, Theme


def test_loading_valid_codebook(db_session):
    codebook = load_codebook(db_session, "app/codebook/examples/codebook.example.yml")
    assert codebook.version == "0.1.0"
    assert db_session.scalar(select(Theme).where(Theme.codebook_version_id == codebook.id)) is not None
    assert db_session.scalar(select(CodingFeature).where(CodingFeature.codebook_version_id == codebook.id)) is not None


def test_rejecting_invalid_codebook(tmp_path: Path):
    invalid = tmp_path / "invalid.yml"
    invalid.write_text("codebook: {}\nthemes: []\n", encoding="utf-8")
    with pytest.raises(Exception):
        load_and_validate_codebook(invalid)
