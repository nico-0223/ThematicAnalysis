from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def now_utc() -> datetime:
    return datetime.now(UTC)


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    title: Mapped[str | None] = mapped_column(String(500))
    source: Mapped[str | None] = mapped_column(String(255))
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=now_utc)
    speakers: Mapped[list[Speaker]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    turns: Mapped[list[Turn]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Speaker(Base):
    __tablename__ = "speakers"
    __table_args__ = (UniqueConstraint("conversation_id", "speaker_label", name="uq_speaker_conversation_label"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    speaker_label: Mapped[str] = mapped_column(String(255))
    role: Mapped[str | None] = mapped_column(String(255))
    metadata_json: Mapped[str | None] = mapped_column(Text)
    conversation: Mapped[Conversation] = relationship(back_populates="speakers")
    turns: Mapped[list[Turn]] = relationship(back_populates="speaker")


class Turn(Base):
    __tablename__ = "turns"
    __table_args__ = (UniqueConstraint("conversation_id", "turn_index", name="uq_turn_conversation_index"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    speaker_id: Mapped[int | None] = mapped_column(ForeignKey("speakers.id", ondelete="SET NULL"), index=True)
    turn_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[str | None] = mapped_column(String(255))
    metadata_json: Mapped[str | None] = mapped_column(Text)
    conversation: Mapped[Conversation] = relationship(back_populates="turns")
    speaker: Mapped[Speaker | None] = relationship(back_populates="turns")
    segments: Mapped[list[Segment]] = relationship(back_populates="turn", cascade="all, delete-orphan")


class Segment(Base):
    __tablename__ = "segments"
    __table_args__ = (UniqueConstraint("turn_id", "segment_index", "segmentation_strategy", name="uq_segment_turn_strategy"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    turn_id: Mapped[int] = mapped_column(ForeignKey("turns.id", ondelete="CASCADE"), index=True)
    segment_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    segmentation_strategy: Mapped[str] = mapped_column(String(255))
    original_text: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[str | None] = mapped_column(Text)
    turn: Mapped[Turn] = relationship(back_populates="segments")
    annotations: Mapped[list[Annotation]] = relationship(back_populates="segment", cascade="all, delete-orphan")


class CodebookVersion(Base):
    __tablename__ = "codebook_versions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    theoretical_framework: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=now_utc)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    themes: Mapped[list[Theme]] = relationship(back_populates="codebook_version", cascade="all, delete-orphan")
    features: Mapped[list[CodingFeature]] = relationship(back_populates="codebook_version", cascade="all, delete-orphan")
    framework_settings: Mapped[list[FrameworkSettings]] = relationship(back_populates="codebook_version", cascade="all, delete-orphan")


class FrameworkSettings(Base):
    __tablename__ = "framework_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codebook_version_id: Mapped[int] = mapped_column(ForeignKey("codebook_versions.id", ondelete="CASCADE"), index=True)
    primary_framework: Mapped[str] = mapped_column(Text)
    supporting_frameworks_json: Mapped[str | None] = mapped_column(Text)
    analysis_orientation: Mapped[str | None] = mapped_column(String(255))
    coding_orientation: Mapped[str | None] = mapped_column(String(255))
    theme_orientation: Mapped[str | None] = mapped_column(String(255))
    epistemological_position: Mapped[str | None] = mapped_column(String(255))
    semantic_or_latent: Mapped[str | None] = mapped_column(String(255))
    inductive_or_deductive: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    codebook_version: Mapped[CodebookVersion] = relationship(back_populates="framework_settings")


class MethodologicalPhase(Base):
    __tablename__ = "methodological_phases"
    __table_args__ = (UniqueConstraint("analysis_run_id", "phase_number", name="uq_run_phase"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    phase_number: Mapped[int] = mapped_column(Integer)
    phase_name: Mapped[str] = mapped_column(String(255))
    framework_reference: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="not_started")
    started_at: Mapped[datetime | None] = mapped_column(default=None)
    completed_at: Mapped[datetime | None] = mapped_column(default=None)
    notes: Mapped[str | None] = mapped_column(Text)
    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="phases")


class Theme(Base):
    __tablename__ = "themes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codebook_version_id: Mapped[int] = mapped_column(ForeignKey("codebook_versions.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    analytical_definition: Mapped[str | None] = mapped_column(Text)
    inclusion_criteria: Mapped[str | None] = mapped_column(Text)
    exclusion_criteria: Mapped[str | None] = mapped_column(Text)
    examples_json: Mapped[str | None] = mapped_column(Text)
    counterexamples_json: Mapped[str | None] = mapped_column(Text)
    parent_theme_id: Mapped[int | None] = mapped_column(ForeignKey("themes.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(50), default="active")
    codebook_version: Mapped[CodebookVersion] = relationship(back_populates="themes")
    codes: Mapped[list[Code]] = relationship(back_populates="theme", cascade="all, delete-orphan")


class CandidateTheme(Base):
    __tablename__ = "candidate_themes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    supporting_codes_json: Mapped[str | None] = mapped_column(Text)
    supporting_segments_json: Mapped[str | None] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String(50), default="candidate")
    rationale: Mapped[str | None] = mapped_column(Text)
    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="candidate_themes")


class Code(Base):
    __tablename__ = "codes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    analytical_definition: Mapped[str | None] = mapped_column(Text)
    inclusion_criteria: Mapped[str | None] = mapped_column(Text)
    exclusion_criteria: Mapped[str | None] = mapped_column(Text)
    indicators_json: Mapped[str | None] = mapped_column(Text)
    examples_json: Mapped[str | None] = mapped_column(Text)
    counterexamples_json: Mapped[str | None] = mapped_column(Text)
    theme: Mapped[Theme] = relationship(back_populates="codes")
    annotations: Mapped[list[Annotation]] = relationship(back_populates="code")


class CodingFeature(Base):
    __tablename__ = "coding_features"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codebook_version_id: Mapped[int] = mapped_column(ForeignKey("codebook_versions.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    feature_type: Mapped[str] = mapped_column(String(100))
    allowed_values_json: Mapped[str | None] = mapped_column(Text)
    extraction_hint: Mapped[str | None] = mapped_column(Text)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    codebook_version: Mapped[CodebookVersion] = relationship(back_populates="features")


class Coder(Base):
    __tablename__ = "coders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    metadata_json: Mapped[str | None] = mapped_column(Text)


class Annotation(Base):
    __tablename__ = "annotations"
    __table_args__ = (UniqueConstraint("segment_id", "code_id", "coder_id", "analysis_run_id", name="uq_annotation"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id", ondelete="CASCADE"), index=True)
    code_id: Mapped[int] = mapped_column(ForeignKey("codes.id", ondelete="CASCADE"), index=True)
    coder_id: Mapped[int] = mapped_column(ForeignKey("coders.id", ondelete="CASCADE"), index=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    confidence: Mapped[float | None] = mapped_column(Float)
    rationale: Mapped[str | None] = mapped_column(Text)
    evidence_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=now_utc)
    segment: Mapped[Segment] = relationship(back_populates="annotations")
    code: Mapped[Code] = relationship(back_populates="annotations")
    coder: Mapped[Coder] = relationship()
    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="annotations")
    decisions: Mapped[list[CodingDecision]] = relationship(back_populates="annotation", cascade="all, delete-orphan")


class CodingDecision(Base):
    __tablename__ = "coding_decisions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    annotation_id: Mapped[int] = mapped_column(ForeignKey("annotations.id", ondelete="CASCADE"), index=True)
    decision_type: Mapped[str] = mapped_column(String(255))
    decision_note: Mapped[str | None] = mapped_column(Text)
    framework_phase: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=now_utc)
    annotation: Mapped[Annotation] = relationship(back_populates="decisions")


class Memo(Base):
    __tablename__ = "memos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int | None] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    segment_id: Mapped[int | None] = mapped_column(ForeignKey("segments.id", ondelete="CASCADE"), index=True)
    coder_id: Mapped[int | None] = mapped_column(ForeignKey("coders.id", ondelete="SET NULL"), index=True)
    memo_type: Mapped[str] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text)
    related_phase: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=now_utc)


class ReflexiveJournalEntry(Base):
    __tablename__ = "reflexive_journal_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_run_id: Mapped[int | None] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    coder_id: Mapped[int | None] = mapped_column(ForeignKey("coders.id", ondelete="SET NULL"), index=True)
    text: Mapped[str] = mapped_column(Text)
    related_phase: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=now_utc)


class AuditTrailEntry(Base):
    __tablename__ = "audit_trail_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_run_id: Mapped[int | None] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    phase_number: Mapped[int | None] = mapped_column(Integer)
    action_type: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    before_state_json: Mapped[str | None] = mapped_column(Text)
    after_state_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=now_utc)


class AdjudicationRecord(Base):
    __tablename__ = "adjudication_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id", ondelete="CASCADE"), index=True)
    code_id: Mapped[int | None] = mapped_column(ForeignKey("codes.id", ondelete="SET NULL"))
    decision: Mapped[str] = mapped_column(String(255))
    rationale: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=now_utc)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codebook_version_id: Mapped[int] = mapped_column(ForeignKey("codebook_versions.id", ondelete="CASCADE"), index=True)
    run_name: Mapped[str] = mapped_column(String(255))
    run_type: Mapped[str] = mapped_column(String(255), default="rule_based")
    config_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=now_utc)
    phases: Mapped[list[MethodologicalPhase]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")
    annotations: Mapped[list[Annotation]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")
    candidate_themes: Mapped[list[CandidateTheme]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")


class ExportRecord(Base):
    __tablename__ = "exports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    export_format: Mapped[str] = mapped_column(String(50))
    path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=now_utc)
