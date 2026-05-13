from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.analysis.reliability import cohens_kappa_binary, coder_comparison, disagreement_table
from app.analysis.thematic_engine import apply_rule_based_codes, import_annotations as import_annotations_file, start_analysis_run
from app.analysis.theme_review import review_candidate_themes
from app.codebook.loader import load_codebook
from app.db.database import init_database, session_scope
from app.db.models import CodebookVersion
from app.framework.braun_clarke import set_phase_status
from app.ingestion.loaders import ingest_file
from app.preprocessing.segmenters import preprocess_turns
from app.reports.exporters import export_report

app = typer.Typer(help="Configurable thematic analysis for conversations.")


@app.command("init-db")
def init_db(drop_existing: bool = typer.Option(False, "--drop-existing", help="Drop existing tables before creating the schema.")) -> None:
    init_database(drop_existing=drop_existing)
    typer.echo("Database initialized.")


@app.command("load-codebook")
def load_codebook_cmd(path: Path = typer.Option(..., "--path", exists=True, readable=True)) -> None:
    with session_scope() as session:
        codebook = load_codebook(session, path)
        typer.echo(f"Loaded codebook {codebook.name} version {codebook.version}.")


@app.command("ingest")
def ingest_cmd(path: Path = typer.Option(..., "--path", exists=True, readable=True), format: str = typer.Option(..., "--format")) -> None:  # noqa: A002
    with session_scope() as session:
        count = ingest_file(session, path, format)
        typer.echo(f"Ingested {count} turns.")


@app.command("preprocess")
def preprocess_cmd(strategy: str = typer.Option("turn", "--strategy"), chunk_size: int = typer.Option(80, "--chunk-size")) -> None:
    with session_scope() as session:
        count = preprocess_turns(session, strategy=strategy, chunk_size=chunk_size)
        typer.echo(f"Created {count} segments.")


@app.command("start-run")
def start_run_cmd(codebook_version: str = typer.Option(..., "--codebook-version"), run_name: str = typer.Option(..., "--run-name"), run_type: str = typer.Option("rule_based", "--run-type")) -> None:
    with session_scope() as session:
        run = start_analysis_run(session, codebook_version=codebook_version, run_name=run_name, run_type=run_type)
        typer.echo(f"Started analysis run {run.id}.")


@app.command("phase")
def phase_cmd(run_id: int = typer.Option(..., "--run-id"), phase: int = typer.Option(..., "--phase"), complete: bool = typer.Option(False, "--complete"), notes: Optional[str] = typer.Option(None, "--notes")) -> None:
    with session_scope() as session:
        record = set_phase_status(session, run_id=run_id, phase_number=phase, complete=complete, notes=notes)
        typer.echo(f"Phase {record.phase_number} is {record.status}.")


@app.command("analyze")
def analyze_cmd(run_id: int = typer.Option(..., "--run-id")) -> None:
    with session_scope() as session:
        count = apply_rule_based_codes(session, run_id=run_id)
        typer.echo(f"Created {count} rule-based annotations and candidate themes.")


@app.command("import-annotations")
def import_annotations_cmd(path: Path = typer.Option(..., "--path", exists=True, readable=True), run_id: int = typer.Option(..., "--run-id")) -> None:
    with session_scope() as session:
        count = import_annotations_file(session, run_id=run_id, path=path)
        typer.echo(f"Imported {count} annotations.")


@app.command("reliability")
def reliability_cmd(run_id: int = typer.Option(..., "--run-id")) -> None:
    with session_scope() as session:
        result = cohens_kappa_binary(session, run_id=run_id)
        comparison = coder_comparison(session, run_id=run_id)
        disagreements = disagreement_table(session, run_id=run_id)
        typer.echo(json.dumps({"kappa": result, "comparison": comparison, "disagreements": disagreements}, ensure_ascii=False, indent=2))


@app.command("review-themes")
def review_themes_cmd(run_id: int = typer.Option(..., "--run-id"), min_segments: int = typer.Option(1, "--min-segments")) -> None:
    with session_scope() as session:
        themes = review_candidate_themes(session, run_id=run_id, min_segments=min_segments)
        typer.echo(f"Reviewed {len(themes)} candidate themes.")


@app.command("export")
def export_cmd(run_id: int = typer.Option(..., "--run-id"), format: str = typer.Option(..., "--format"), out: Path = typer.Option(..., "--out")) -> None:  # noqa: A002
    with session_scope() as session:
        path = export_report(session, run_id=run_id, output_format=format, out_path=out)
        typer.echo(f"Exported report to {path}.")


if __name__ == "__main__":
    app()
