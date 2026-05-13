from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.codebook.schema import CodebookFile
from app.codebook.validators import load_and_validate_codebook
from app.db.models import Code, CodebookVersion, CodingFeature, FrameworkSettings, Theme
from app.framework.audit_trail import record_audit_event


def _dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def load_codebook(session: Session, path: str | Path) -> CodebookVersion:
    config = load_and_validate_codebook(path)
    return persist_codebook(session, config, source_path=str(path))


def persist_codebook(session: Session, config: CodebookFile, source_path: str | None = None) -> CodebookVersion:
    existing = session.scalar(select(CodebookVersion).where(CodebookVersion.version == config.codebook.version))
    if existing:
        existing.is_active = False
        session.flush()
    codebook = CodebookVersion(
        name=config.codebook.name,
        version=config.codebook.version,
        description=config.codebook.description,
        theoretical_framework=_dump(config.codebook.theoretical_framework.model_dump()),
        is_active=True,
    )
    session.add(codebook)
    session.flush()

    settings = FrameworkSettings(
        codebook_version_id=codebook.id,
        primary_framework=config.codebook.theoretical_framework.primary,
        supporting_frameworks_json=_dump(config.codebook.theoretical_framework.supporting),
        analysis_orientation=config.framework_settings.analysis_orientation,
        coding_orientation=config.framework_settings.coding_orientation,
        theme_orientation=config.framework_settings.theme_orientation,
        epistemological_position=config.framework_settings.epistemological_position,
        semantic_or_latent=config.framework_settings.semantic_or_latent,
        inductive_or_deductive=config.framework_settings.inductive_or_deductive,
        description=config.framework_settings.description,
    )
    session.add(settings)

    for feature in config.features:
        session.add(
            CodingFeature(
                codebook_version_id=codebook.id,
                name=feature.name,
                description=feature.description,
                feature_type=feature.type,
                allowed_values_json=_dump(feature.allowed_values),
                extraction_hint=feature.extraction_hint,
                is_required=feature.required,
            )
        )

    for theme_cfg in config.themes:
        theme = Theme(
            codebook_version_id=codebook.id,
            name=theme_cfg.name,
            description=theme_cfg.description,
            analytical_definition=theme_cfg.analytical_definition,
            inclusion_criteria=_dump(theme_cfg.inclusion_criteria),
            exclusion_criteria=_dump(theme_cfg.exclusion_criteria),
            examples_json=_dump(theme_cfg.examples),
            counterexamples_json=_dump(theme_cfg.counterexamples),
            status=theme_cfg.status,
        )
        session.add(theme)
        session.flush()
        for code_cfg in theme_cfg.codes:
            indicators = list(dict.fromkeys([*theme_cfg.indicators, *code_cfg.indicators]))
            session.add(
                Code(
                    theme_id=theme.id,
                    name=code_cfg.name,
                    description=code_cfg.description,
                    analytical_definition=code_cfg.analytical_definition,
                    inclusion_criteria=_dump(code_cfg.inclusion_criteria),
                    exclusion_criteria=_dump(code_cfg.exclusion_criteria),
                    indicators_json=_dump(indicators),
                    examples_json=_dump(code_cfg.examples),
                    counterexamples_json=_dump(code_cfg.counterexamples),
                )
            )
    session.flush()
    record_audit_event(
        session,
        analysis_run_id=None,
        phase_number=None,
        action_type="load_codebook",
        description=f"Loaded codebook version {codebook.version}.",
        after_state={"codebook_id": codebook.id, "path": source_path},
    )
    return codebook
