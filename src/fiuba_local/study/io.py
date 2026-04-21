from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from ..config import DEFAULT_STATE_DIR
from .types import StudyEvent


DEFAULT_STUDY_STATE_PATH = DEFAULT_STATE_DIR / "study_state.json"
DEFAULT_STUDY_DATES_PATH = DEFAULT_STATE_DIR / "study_dates.json"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, dict):
        raise ValueError(f"El archivo debe contener un objeto JSON: {path}")
    return raw


def build_default_dates_template(today: date) -> dict[str, Any]:
    sample_date = today + timedelta(days=21)
    return {
        "events": [
            {
                "materia": "Mecanismos",
                "event_type": "parcial",
                "title": "Parcial 1",
                "date": sample_date.isoformat(),
                "weight": 1.0,
                "difficulty": 3,
            }
        ]
    }


def build_default_state(today: date) -> dict[str, Any]:
    return {
        "version": 1,
        "created_at": today.isoformat(),
        "config": {
            "weekly_hours": 10.0,
            "weeks": 6,
            "session_minutes": 90,
            "max_daily_hours": 3.0,
            "day_start_hour": 19,
        },
        "planned_sessions": [],
        "completed_sessions": [],
    }


def save_template_files(
    dates_path: Path,
    state_path: Path,
    today: date,
    overwrite: bool = False,
) -> tuple[bool, bool]:
    wrote_dates = False
    wrote_state = False

    if overwrite or not dates_path.exists():
        _write_json(dates_path, build_default_dates_template(today))
        wrote_dates = True

    if overwrite or not state_path.exists():
        _write_json(state_path, build_default_state(today))
        wrote_state = True

    return wrote_dates, wrote_state


def load_state(path: Path) -> dict[str, Any]:
    return _read_json(path)


def save_state(path: Path, state: dict[str, Any]) -> None:
    _write_json(path, state)


def _parse_event(raw: dict[str, Any]) -> StudyEvent:
    materia = str(raw.get("materia", "")).strip()
    if not materia:
        raise ValueError("Cada evento requiere `materia`.")

    event_type = str(raw.get("event_type", "otro")).strip() or "otro"
    title = str(raw.get("title", "")).strip() or f"{event_type.title()} {materia}"

    raw_date = str(raw.get("date", "")).strip()
    if not raw_date:
        raise ValueError(f"Evento de {materia}: falta `date` (YYYY-MM-DD).")
    try:
        event_date = date.fromisoformat(raw_date)
    except ValueError as exc:
        raise ValueError(f"Evento de {materia}: fecha invalida `{raw_date}`.") from exc

    weight = float(raw.get("weight", 1.0))
    if weight <= 0:
        raise ValueError(f"Evento de {materia}: `weight` debe ser > 0.")

    difficulty = int(raw.get("difficulty", 3))
    if difficulty < 1 or difficulty > 5:
        raise ValueError(f"Evento de {materia}: `difficulty` debe estar entre 1 y 5.")

    return StudyEvent(
        materia=materia,
        event_type=event_type,
        title=title,
        date=event_date,
        weight=weight,
        difficulty=difficulty,
    )


def load_events(path: Path) -> list[StudyEvent]:
    payload = _read_json(path)
    raw_events = payload.get("events")
    if not isinstance(raw_events, list):
        raise ValueError("El archivo de fechas requiere una lista `events`.")
    events: list[StudyEvent] = []
    for idx, item in enumerate(raw_events, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Evento #{idx}: debe ser un objeto JSON.")
        events.append(_parse_event(item))
    return events
