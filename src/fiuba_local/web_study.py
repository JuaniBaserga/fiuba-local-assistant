from __future__ import annotations

from http import HTTPStatus
from pathlib import Path

from .study import (
    PlanRequest,
    StudyService,
    StudyValidationError,
    completed_ids,
    planned_sessions,
    state_config,
)


class StudyHandlersMixin:
    """HTTP adapter for study-domain operations."""

    def _study_state_payload(self) -> dict:
        return {
            "dates_path": str(self.config.study_dates_path),
            "state_path": str(self.config.study_state_path),
        }

    def _study_service(self) -> StudyService:
        return StudyService(self.config.study_dates_path, self.config.study_state_path)

    def _handle_study_status(self) -> None:
        try:
            events, state = self._study_service().load()
            sessions = planned_sessions(state)
        except FileNotFoundError:
            self._json(
                {
                    **self._study_state_payload(),
                    "ready": False,
                    "events_count": 0,
                    "planned_sessions_count": 0,
                    "completed_sessions_count": 0,
                    "events": [],
                    "planned_sessions": [],
                }
            )
            return
        except StudyValidationError as exc:
            self._json({"error": f"Estado de estudio invalido: {exc}"}, status=HTTPStatus.BAD_REQUEST)
            return

        done_ids = completed_ids(state)
        upcoming_events = [
            {
                "materia": event.materia,
                "event_type": event.event_type,
                "title": event.title,
                "date": event.date.isoformat(),
                "weight": event.weight,
                "difficulty": event.difficulty,
                "topics": list(event.topics),
            }
            for event in sorted(events, key=lambda event: event.date)
        ]
        planned_payload = [
            {
                **session.to_dict(),
                "completed": session.id in done_ids,
            }
            for session in sorted(sessions, key=lambda session: (session.start, session.materia, session.id))
        ]
        self._json(
            {
                **self._study_state_payload(),
                "ready": True,
                "events_count": len(upcoming_events),
                "planned_sessions_count": len(planned_payload),
                "completed_sessions_count": len(done_ids),
                "events": upcoming_events,
                "planned_sessions": planned_payload,
                "config": state_config(state),
            }
        )

    def _handle_study_init(self) -> None:
        payload, error = self._read_json_body()
        if error:
            self._json({"error": error}, status=HTTPStatus.BAD_REQUEST)
            return
        assert payload is not None
        wrote_dates, wrote_state = self._study_service().initialize(overwrite=bool(payload.get("overwrite", False)))
        self._json({"ok": True, "wrote_dates": wrote_dates, "wrote_state": wrote_state})

    def _handle_study_plan(self) -> None:
        payload, error = self._read_json_body()
        if error:
            self._json({"error": error}, status=HTTPStatus.BAD_REQUEST)
            return
        assert payload is not None
        try:
            service = self._study_service()
            _, state = service.load()
            request = PlanRequest.from_mapping(payload, state_config(state))
            sessions = service.plan(request)
        except FileNotFoundError as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.NOT_FOUND)
            return
        except StudyValidationError as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._json({"ok": True, "sessions": len(sessions)})

    def _handle_study_export_ics(self) -> None:
        try:
            ics_payload = self._study_service().export_ics()
        except FileNotFoundError as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.NOT_FOUND)
            return
        except StudyValidationError as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._json({"ok": True, "ics": ics_payload})

    def _handle_study_report(self) -> None:
        try:
            report = self._study_service().report()
        except FileNotFoundError as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.NOT_FOUND)
            return
        except StudyValidationError as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._json(
            {
                "ok": True,
                "weekly_csv": str(report.weekly_csv),
                "materia_csv": str(report.materia_csv),
                "planned_svg": str(report.planned_svg),
                "compare_svg": str(report.compare_svg),
            }
        )

    def _handle_study_load_demo(self) -> None:
        payload, error = self._read_json_body()
        if error:
            self._json({"error": error}, status=HTTPStatus.BAD_REQUEST)
            return
        assert payload is not None
        source = Path(str(payload.get("path", ""))).expanduser()
        try:
            self._study_service().load_demo(source)
        except FileNotFoundError as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.NOT_FOUND)
            return
        except StudyValidationError as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self._json({"ok": True, "source_path": str(source), "dates_path": str(self.config.study_dates_path)})
