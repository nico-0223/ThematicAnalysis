from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class TheoreticalFrameworkConfig(BaseModel):
    primary: str
    supporting: list[str] = Field(default_factory=list)


class CodebookMeta(BaseModel):
    name: str
    version: str
    description: str | None = None
    theoretical_framework: TheoreticalFrameworkConfig


class FrameworkSettingsConfig(BaseModel):
    analysis_orientation: str | None = None
    coding_orientation: str | None = None
    theme_orientation: str | None = None
    epistemological_position: str | None = None
    semantic_or_latent: str | None = None
    inductive_or_deductive: str | None = None
    require_audit_trail: bool = True
    require_memos: bool = True
    require_phase_completion: bool = True
    description: str | None = None


class FeatureConfig(BaseModel):
    name: str
    description: str | None = None
    type: str = Field(alias="type")
    allowed_values: list[str] = Field(default_factory=list)
    required: bool = False
    extraction_hint: str | None = None


class CodeConfig(BaseModel):
    name: str
    description: str | None = None
    analytical_definition: str | None = None
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)
    indicators: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    counterexamples: list[str] = Field(default_factory=list)


class ThemeConfig(BaseModel):
    name: str
    description: str | None = None
    analytical_definition: str | None = None
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)
    indicators: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    counterexamples: list[str] = Field(default_factory=list)
    status: str = "active"
    codes: list[CodeConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_codes(self) -> "ThemeConfig":
        if not self.codes:
            raise ValueError(f"Theme '{self.name}' must contain at least one code")
        return self


class MemoPromptsConfig(BaseModel):
    familiarisation: list[str] = Field(default_factory=list)
    coding: list[str] = Field(default_factory=list)
    theme_review: list[str] = Field(default_factory=list)


class CodebookFile(BaseModel):
    codebook: CodebookMeta
    framework_settings: FrameworkSettingsConfig
    features: list[FeatureConfig] = Field(default_factory=list)
    themes: list[ThemeConfig]
    memo_prompts: MemoPromptsConfig = Field(default_factory=MemoPromptsConfig)

    @field_validator("themes")
    @classmethod
    def require_themes(cls, value: list[ThemeConfig]) -> list[ThemeConfig]:
        if not value:
            raise ValueError("At least one theme is required. Themes remain editable after loading.")
        return value
