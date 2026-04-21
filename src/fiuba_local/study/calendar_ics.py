from __future__ import annotations

from datetime import datetime

from .types import StudySession


def _fmt_dt(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%S")


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def render_ics(
    sessions: list[StudySession],
    calendar_name: str = "FIUBA Study Plan",
    prod_id: str = "-//fiuba-local-assistant//study//ES",
) -> str:
    now_stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines: list[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{_escape(prod_id)}",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{_escape(calendar_name)}",
    ]

    for session in sorted(sessions, key=lambda s: (s.start, s.id)):
        summary = f"Estudio - {session.materia}"
        description = (
            f"Objetivo: {session.target_event_type} ({session.target_title})\\n"
            f"Fecha objetivo: {session.target_date.isoformat()}\\n"
            f"Duracion: {session.duration_minutes} minutos"
        )
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{_escape(session.id)}@fiuba-local",
                f"DTSTAMP:{now_stamp}",
                f"DTSTART:{_fmt_dt(session.start)}",
                f"DTEND:{_fmt_dt(session.end)}",
                f"SUMMARY:{_escape(summary)}",
                f"DESCRIPTION:{_escape(description)}",
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
