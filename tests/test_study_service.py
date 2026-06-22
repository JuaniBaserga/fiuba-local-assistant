from __future__ import annotations

import json
from datetime import date

import pytest

from fiuba_local.study import (
    PlanRequest,
    StudyService,
    StudyValidationError,
    completed_ids,
    planned_sessions,
)


def test_plan_request_uses_defaults_and_validates():
    request = PlanRequest.from_mapping(
        {"weekly_hours": "8"},
        {"weeks": 2, "session_minutes": 60, "max_daily_hours": 2, "day_start_hour": 18},
        today=date(2026, 6, 22),
    )
    assert request.from_date == date(2026, 6, 22)
    assert request.weekly_hours == 8.0
    assert request.weeks == 2

    with pytest.raises(StudyValidationError, match="Parametros de plan invalidos"):
        PlanRequest.from_mapping({"weeks": 0})


def test_service_plan_persists_typed_sessions(tmp_path):
    service = StudyService(tmp_path / "dates.json", tmp_path / "state.json")
    service.initialize(today=date(2026, 6, 1))
    request = PlanRequest.from_mapping(
        {
            "from_date": "2026-06-01",
            "weekly_hours": 2,
            "weeks": 1,
            "session_minutes": 60,
            "max_daily_hours": 2,
            "day_start_hour": 18,
        }
    )
    sessions = service.plan(request)

    assert sessions
    assert service.sessions() == sessions
    state = json.loads(service.state_path.read_text(encoding="utf-8"))
    assert planned_sessions(state) == sessions
    assert completed_ids(state) == set()


def test_service_rejects_invalid_persisted_sessions(tmp_path):
    service = StudyService(tmp_path / "dates.json", tmp_path / "state.json")
    service.initialize(today=date(2026, 6, 1))
    state = json.loads(service.state_path.read_text(encoding="utf-8"))
    state["planned_sessions"] = [{"id": "missing-fields"}]
    service.state_path.write_text(json.dumps(state), encoding="utf-8")

    with pytest.raises(StudyValidationError, match="Sesion invalida"):
        service.sessions()


def test_state_writes_are_atomic_and_leave_no_temp_files(tmp_path):
    service = StudyService(tmp_path / "dates.json", tmp_path / "state.json")
    service.initialize(today=date(2026, 6, 1))
    state = json.loads(service.state_path.read_text(encoding="utf-8"))
    state["config"]["weeks"] = 3

    from fiuba_local.study import save_state

    save_state(service.state_path, state)
    assert json.loads(service.state_path.read_text(encoding="utf-8"))["config"]["weeks"] == 3
    assert list(tmp_path.glob("*.tmp")) == []
