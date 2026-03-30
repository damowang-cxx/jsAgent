from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from har_agent.config import ReportConfig
from har_agent.models.report import AnalysisResult


def render_markdown_report(result: AnalysisResult, report_config: ReportConfig) -> str:
    template_dir = Path(__file__).parent / "templates"
    environment = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = environment.get_template("report.md.j2")
    return template.render(
        result=result,
        include_timeline=report_config.include_timeline,
        include_raw_examples=report_config.include_raw_examples,
    )


def write_markdown_report(result: AnalysisResult, path: str | Path, report_config: ReportConfig) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_report(result, report_config), encoding="utf-8")
