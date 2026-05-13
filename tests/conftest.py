from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app.db.database import configure_database, init_database, session_scope


@pytest.fixture()
def db_session(tmp_path: Path):
    db_path = tmp_path / "test.db"
    configure_database(f"sqlite:///{db_path}")
    init_database(drop_existing=True)
    with session_scope() as session:
        yield session
