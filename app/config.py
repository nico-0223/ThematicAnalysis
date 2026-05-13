from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/thematic_analysis.db")
    app_env: str = os.getenv("APP_ENV", "development")
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    )
    project_root: Path = Path(__file__).resolve().parents[1]


def get_settings() -> Settings:
    return Settings()
