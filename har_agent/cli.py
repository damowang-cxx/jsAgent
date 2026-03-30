from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from har_agent.analysis.pipeline import analyze_har
from har_agent.config import ConfigLoadError, load_config
from har_agent.reporting.json_output import write_json_output
from har_agent.reporting.markdown_report import write_markdown_report

app = typer.Typer(help="Local-first HAR offline analysis CLI.", no_args_is_help=True)


@app.callback()
def main() -> None:
    """HAR Agent command group."""


@app.command("analyze")
def analyze(
    input: Path = typer.Option(..., "--input", exists=True, dir_okay=False, readable=True, help="Input HAR file."),
    config: Optional[str] = typer.Option(None, "--config", help="Optional YAML config."),
    goal: Optional[str] = typer.Option(None, "--goal", help="Natural-language analysis goal."),
    goal_file: Optional[str] = typer.Option(None, "--goal-file", help="Path to a text file containing the natural-language goal."),
    output_json: Optional[str] = typer.Option(None, "--output-json", help="Optional JSON output path."),
    output_report: Optional[str] = typer.Option(None, "--output-report", help="Optional Markdown output path."),
) -> None:
    try:
        resolved_goal = _resolve_goal_input(goal, goal_file)
        if config and resolved_goal:
            raise ConfigLoadError("--goal/--goal-file cannot be used together with --config")
        loaded_config = load_config(config)
        result = analyze_har(input, loaded_config, goal=resolved_goal)
    except (ConfigLoadError, RuntimeError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # pragma: no cover - CLI safety net
        typer.echo(f"Unexpected error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    json_path = Path(output_json) if output_json else Path("out") / "result.json"
    report_path = Path(output_report) if output_report else Path("out") / "report.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    write_json_output(result, json_path)
    write_markdown_report(result, report_path, loaded_config.report)
    typer.echo(
        "Analyzed "
        f"{result.summary.entry_count} entries, matched {result.summary.matched_request_count} requests, "
        f"resolved input mode {result.analysis_intent.input_mode} as {result.analysis_intent.analysis_kind} "
        f"with {result.analysis_intent.resolution_confidence} confidence, "
        f"produced {result.summary.cookie_lineage_count} cookie findings and {result.summary.field_analysis_count} field findings. "
        f"JSON: {json_path} Report: {report_path}"
    )


def _resolve_goal_input(goal: str | None, goal_file: str | None) -> str | None:
    if goal and goal_file:
        raise ConfigLoadError("--goal and --goal-file cannot be used together")
    if goal_file:
        goal_path = Path(goal_file)
        if not goal_path.exists():
            raise ConfigLoadError(f"Goal file not found: {goal_path}")
        goal_text = goal_path.read_text(encoding="utf-8").strip()
        if not goal_text:
            raise ConfigLoadError("Goal file is empty")
        return goal_text
    if goal:
        if not goal.strip():
            raise ConfigLoadError("Goal text is empty")
        return goal.strip()
    return None


if __name__ == "__main__":  # pragma: no cover
    app()
