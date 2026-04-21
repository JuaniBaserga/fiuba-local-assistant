from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from .types import StudySession


@dataclass(frozen=True)
class ReportOutput:
    weekly_csv: Path
    materia_csv: Path
    planned_svg: Path
    compare_svg: Path


def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _minutes_to_hours(minutes: int) -> float:
    return round(minutes / 60.0, 2)


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff" />',
        f'<text x="24" y="32" font-family="Arial, sans-serif" font-size="20" fill="#111827">{title}</text>',
    ]


def _write_bar_chart_svg(path: Path, title: str, labels: list[str], values: list[float], color: str) -> None:
    width = 1100
    height = 480
    left = 80
    right = 40
    top = 60
    bottom = 120
    chart_w = width - left - right
    chart_h = height - top - bottom
    n = max(len(labels), 1)
    slot = chart_w / n
    bar_w = max(16.0, slot * 0.6)
    max_value = max(values) if values else 1.0
    scale = chart_h / max(max_value, 1.0)

    lines = _svg_header(width, height, title)
    lines.append(f'<line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" stroke="#9ca3af" />')
    lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#9ca3af" />')

    for i, (label, value) in enumerate(zip(labels, values)):
        x_center = left + (i * slot) + (slot / 2.0)
        bar_h = value * scale
        x = x_center - (bar_w / 2.0)
        y = top + chart_h - bar_h
        safe_label = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" fill="{color}" />')
        lines.append(
            f'<text x="{x_center:.2f}" y="{top + chart_h + 20}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="12" fill="#374151">{safe_label}</text>'
        )
        lines.append(
            f'<text x="{x_center:.2f}" y="{y - 6:.2f}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="12" fill="#111827">{value:.2f}h</text>'
        )

    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_grouped_bars_svg(
    path: Path,
    title: str,
    labels: list[str],
    planned_values: list[float],
    completed_values: list[float],
) -> None:
    width = 1120
    height = 500
    left = 80
    right = 40
    top = 60
    bottom = 130
    chart_w = width - left - right
    chart_h = height - top - bottom
    n = max(len(labels), 1)
    slot = chart_w / n
    group_w = max(18.0, slot * 0.7)
    bar_w = group_w / 2.2
    max_value = max(planned_values + completed_values) if (planned_values or completed_values) else 1.0
    scale = chart_h / max(max_value, 1.0)

    lines = _svg_header(width, height, title)
    lines.append(f'<line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" stroke="#9ca3af" />')
    lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#9ca3af" />')

    for i, label in enumerate(labels):
        x_center = left + (i * slot) + (slot / 2.0)
        group_left = x_center - (group_w / 2.0)

        p_val = planned_values[i]
        c_val = completed_values[i]

        p_h = p_val * scale
        c_h = c_val * scale
        p_y = top + chart_h - p_h
        c_y = top + chart_h - c_h

        px = group_left
        cx = group_left + bar_w + 6.0

        safe_label = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines.append(f'<rect x="{px:.2f}" y="{p_y:.2f}" width="{bar_w:.2f}" height="{p_h:.2f}" fill="#2563eb" />')
        lines.append(f'<rect x="{cx:.2f}" y="{c_y:.2f}" width="{bar_w:.2f}" height="{c_h:.2f}" fill="#059669" />')
        lines.append(
            f'<text x="{x_center:.2f}" y="{top + chart_h + 20}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="12" fill="#374151">{safe_label}</text>'
        )

    legend_y = height - 30
    lines.append('<rect x="80" y="{}" width="14" height="14" fill="#2563eb" />'.format(legend_y - 12))
    lines.append('<text x="100" y="{}" font-family="Arial, sans-serif" font-size="12" fill="#111827">Planificado</text>'.format(legend_y))
    lines.append('<rect x="220" y="{}" width="14" height="14" fill="#059669" />'.format(legend_y - 12))
    lines.append('<text x="240" y="{}" font-family="Arial, sans-serif" font-size="12" fill="#111827">Completado</text>'.format(legend_y))
    lines.append("</svg>")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_report(
    planned_sessions: list[StudySession],
    completed_session_ids: set[str],
    output_dir: Path,
) -> ReportOutput:
    output_dir = output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    planned_minutes_by_materia: dict[str, int] = {}
    completed_minutes_by_materia: dict[str, int] = {}
    weekly_rows: dict[tuple[str, str], dict[str, object]] = {}

    for session in planned_sessions:
        week = _week_start(session.start.date()).isoformat()
        key = (week, session.materia)
        if key not in weekly_rows:
            weekly_rows[key] = {
                "week_start": week,
                "materia": session.materia,
                "planned_minutes": 0,
                "completed_minutes": 0,
            }

        weekly_rows[key]["planned_minutes"] = int(weekly_rows[key]["planned_minutes"]) + session.duration_minutes
        planned_minutes_by_materia[session.materia] = planned_minutes_by_materia.get(session.materia, 0) + session.duration_minutes

        if session.id in completed_session_ids:
            weekly_rows[key]["completed_minutes"] = int(weekly_rows[key]["completed_minutes"]) + session.duration_minutes
            completed_minutes_by_materia[session.materia] = (
                completed_minutes_by_materia.get(session.materia, 0) + session.duration_minutes
            )

    weekly_output_rows: list[dict[str, object]] = []
    for _, row in sorted(weekly_rows.items(), key=lambda item: (item[0][0], item[0][1])):
        planned_minutes = int(row["planned_minutes"])
        completed_minutes = int(row["completed_minutes"])
        completion_rate = round((completed_minutes / planned_minutes) * 100.0, 2) if planned_minutes > 0 else 0.0
        weekly_output_rows.append(
            {
                "week_start": row["week_start"],
                "materia": row["materia"],
                "planned_hours": _minutes_to_hours(planned_minutes),
                "completed_hours": _minutes_to_hours(completed_minutes),
                "completion_rate_pct": completion_rate,
            }
        )

    materias = sorted(planned_minutes_by_materia.keys())
    materia_rows: list[dict[str, object]] = []
    planned_hours_values: list[float] = []
    completed_hours_values: list[float] = []
    for materia in materias:
        planned_m = planned_minutes_by_materia.get(materia, 0)
        completed_m = completed_minutes_by_materia.get(materia, 0)
        backlog_m = max(planned_m - completed_m, 0)
        completion_rate = round((completed_m / planned_m) * 100.0, 2) if planned_m > 0 else 0.0

        p_hours = _minutes_to_hours(planned_m)
        c_hours = _minutes_to_hours(completed_m)
        planned_hours_values.append(p_hours)
        completed_hours_values.append(c_hours)

        materia_rows.append(
            {
                "materia": materia,
                "planned_hours": p_hours,
                "completed_hours": c_hours,
                "backlog_hours": _minutes_to_hours(backlog_m),
                "completion_rate_pct": completion_rate,
            }
        )

    weekly_csv = output_dir / "study_report_weekly.csv"
    materia_csv = output_dir / "study_report_by_materia.csv"
    planned_svg = output_dir / "study_planned_by_materia.svg"
    compare_svg = output_dir / "study_plan_vs_completed.svg"

    _write_csv(
        weekly_csv,
        weekly_output_rows,
        fieldnames=["week_start", "materia", "planned_hours", "completed_hours", "completion_rate_pct"],
    )
    _write_csv(
        materia_csv,
        materia_rows,
        fieldnames=["materia", "planned_hours", "completed_hours", "backlog_hours", "completion_rate_pct"],
    )
    _write_bar_chart_svg(
        planned_svg,
        title="Horas Planificadas Por Materia",
        labels=materias,
        values=planned_hours_values,
        color="#2563eb",
    )
    _write_grouped_bars_svg(
        compare_svg,
        title="Planificado vs Completado",
        labels=materias,
        planned_values=planned_hours_values,
        completed_values=completed_hours_values,
    )

    return ReportOutput(
        weekly_csv=weekly_csv,
        materia_csv=materia_csv,
        planned_svg=planned_svg,
        compare_svg=compare_svg,
    )
