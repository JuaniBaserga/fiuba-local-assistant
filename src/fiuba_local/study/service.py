from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from .calendar_ics import render_ics
from .io import load_events, load_state, save_dates, save_state, save_template_files
from .planner import PlanOptions, build_study_plan
from .report import ReportOutput, build_report
from .types import StudyEvent, StudySession


class StudyError(Exception):
    """Base error for study-domain operations."""


class StudyValidationError(StudyError):
    """Raised when study input or persisted state is invalid."""


@dataclass(frozen=True)
class PlanRequest:
    from_date: date
    weekly_hours: float
    weeks: int
    session_minutes: int
    max_daily_hours: float
    day_start_hour: int

    @classmethod
    def from_mapping(
        cls,
        payload: Mapping[str, object],
        defaults: Mapping[str, object] | None = None,
        today: date | None = None,
    ) -> "PlanRequest":
        defaults = defaults or {}

        def value(name: str, fallback: object) -> object:
            candidate = payload.get(name)
            if candidate is None or candidate == "":
                candidate = defaults.get(name, fallback)
            return candidate

        try:
            raw_date = value("from_date", (today or date.today()).isoformat())
            from_date = raw_date if isinstance(raw_date, date) else date.fromisoformat(str(raw_date))
            request = cls(
                from_date=from_date,
                weekly_hours=float(value("weekly_hours", 10.0)),
                weeks=int(value("weeks", 6)),
                session_minutes=int(value("session_minutes", 90)),
                max_daily_hours=float(value("max_daily_hours", 3.0)),
                day_start_hour=int(value("day_start_hour", 19)),
            )
            request.to_options()
            return request
        except (TypeError, ValueError) as exc:
            raise StudyValidationError(f"Parametros de plan invalidos: {exc}") from exc

    def to_options(self) -> PlanOptions:
        options = PlanOptions(
            from_date=self.from_date,
            weekly_hours=self.weekly_hours,
            weeks=self.weeks,
            session_minutes=self.session_minutes,
            max_daily_hours=self.max_daily_hours,
            day_start_hour=self.day_start_hour,
        )
        # Validation lives in the planner today; keep one source of truth.
        build_study_plan([], options)
        return options

    def config(self) -> dict[str, object]:
        return {
            "weekly_hours": self.weekly_hours,
            "weeks": self.weeks,
            "session_minutes": self.session_minutes,
            "max_daily_hours": self.max_daily_hours,
            "day_start_hour": self.day_start_hour,
        }


def state_config(state: Mapping[str, object]) -> dict[str, object]:
    config = state.get("config")
    return dict(config) if isinstance(config, dict) else {}


def planned_sessions(state: Mapping[str, object]) -> list[StudySession]:
    raw_sessions = state.get("planned_sessions", [])
    if not isinstance(raw_sessions, list):
        raise StudyValidationError("`planned_sessions` debe ser una lista.")
    sessions: list[StudySession] = []
    try:
        for index, raw in enumerate(raw_sessions, start=1):
            if not isinstance(raw, dict):
                raise StudyValidationError(f"Sesion invalida en posicion {index}.")
            sessions.append(StudySession.from_dict(raw))
    except (KeyError, TypeError, ValueError) as exc:
        raise StudyValidationError(f"Sesion invalida: {exc}") from exc
    return sessions


def completed_records(state: Mapping[str, object]) -> list[dict[str, object]]:
    raw = state.get("completed_sessions", [])
    return [dict(item) for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []


def completed_ids(state: Mapping[str, object]) -> set[str]:
    return {
        session_id
        for item in completed_records(state)
        if (session_id := item.get("session_id")) and isinstance(session_id, str)
    }


@dataclass(frozen=True)
class StudyService:
    dates_path: Path
    state_path: Path

    def initialize(self, overwrite: bool = False, today: date | None = None) -> tuple[bool, bool]:
        return save_template_files(self.dates_path, self.state_path, today or date.today(), overwrite)

    def load(self) -> tuple[list[StudyEvent], dict[str, Any]]:
        try:
            return load_events(self.dates_path), load_state(self.state_path)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise StudyValidationError(str(exc)) from exc

    def plan(self, request: PlanRequest) -> list[StudySession]:
        events, state = self.load()
        sessions = self.build_plan(events, request)
        self.save_plan(state, request, sessions)
        return sessions

    def build_plan(self, events: list[StudyEvent], request: PlanRequest) -> list[StudySession]:
        try:
            return build_study_plan(events, request.to_options())
        except ValueError as exc:
            raise StudyValidationError(str(exc)) from exc

    def save_plan(
        self,
        state: dict[str, Any],
        request: PlanRequest,
        sessions: list[StudySession],
    ) -> None:
        state["config"] = request.config()
        state["planned_sessions"] = [session.to_dict() for session in sessions]
        save_state(self.state_path, state)

    def sessions(self) -> list[StudySession]:
        try:
            return planned_sessions(load_state(self.state_path))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise StudyValidationError(str(exc)) from exc

    def export_ics(self, calendar_name: str = "FIUBA Study Plan") -> str:
        return render_ics(self.sessions(), calendar_name=calendar_name)

    def report(self, output_dir: Path | None = None) -> ReportOutput:
        try:
            state = load_state(self.state_path)
            sessions = planned_sessions(state)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise StudyValidationError(str(exc)) from exc
        return build_report(sessions, completed_ids(state), output_dir or self.state_path.parent / "reports")

    def load_demo(self, source: Path) -> None:
        if not source.is_file():
            raise FileNotFoundError(f"No existe el archivo: {source}")
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("el JSON debe contener un objeto")
            load_events(source)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise StudyValidationError(f"Demo invalida: {exc}") from exc
        save_dates(self.dates_path, payload)
        if not self.state_path.exists():
            self.initialize(overwrite=False)
