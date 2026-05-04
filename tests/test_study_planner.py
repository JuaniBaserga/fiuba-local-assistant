from datetime import date, datetime

from fiuba_local.study.calendar_ics import render_ics
from fiuba_local.study.planner import PlanOptions, build_study_plan
from fiuba_local.study.types import StudyEvent, StudySession


def test_build_study_plan_prioritizes_nearer_events():
    start = date(2026, 4, 20)
    events = [
        StudyEvent(
            materia="Mecanismos",
            event_type="parcial",
            title="Parcial Meca",
            date=date(2026, 4, 24),
            weight=1.0,
            difficulty=3,
        ),
        StudyEvent(
            materia="Automatizacion",
            event_type="parcial",
            title="Parcial Auto",
            date=date(2026, 5, 20),
            weight=1.0,
            difficulty=3,
        ),
    ]
    options = PlanOptions(
        from_date=start,
        weekly_hours=6.0,
        weeks=1,
        session_minutes=60,
        max_daily_hours=4.0,
        day_start_hour=19,
    )

    sessions = build_study_plan(events, options)
    assert sessions

    minutes_by_materia: dict[str, int] = {}
    for session in sessions:
        minutes_by_materia[session.materia] = minutes_by_materia.get(session.materia, 0) + session.duration_minutes

    assert minutes_by_materia["Mecanismos"] > minutes_by_materia["Automatizacion"]
    assert sum(minutes_by_materia.values()) == 360


def test_build_study_plan_respects_daily_limit_when_feasible():
    start = date(2026, 4, 20)
    events = [
        StudyEvent(
            materia="Mecanismos",
            event_type="parcial",
            title="Parcial Meca",
            date=date(2026, 5, 10),
            weight=1.0,
            difficulty=4,
        ),
        StudyEvent(
            materia="Ind Extractivas",
            event_type="entrega",
            title="TP",
            date=date(2026, 5, 12),
            weight=1.0,
            difficulty=3,
        ),
    ]
    options = PlanOptions(
        from_date=start,
        weekly_hours=10.0,
        weeks=1,
        session_minutes=60,
        max_daily_hours=2.0,
        day_start_hour=18,
    )
    sessions = build_study_plan(events, options)

    by_day: dict[date, int] = {}
    for session in sessions:
        day = session.start.date()
        by_day[day] = by_day.get(day, 0) + session.duration_minutes

    assert all(minutes <= 120 for minutes in by_day.values())


def test_build_study_plan_assigns_focus_topic_and_reason():
    start = date(2026, 4, 20)
    events = [
        StudyEvent(
            materia="Mecanismos",
            event_type="parcial",
            title="Parcial Meca",
            date=date(2026, 4, 28),
            weight=1.0,
            difficulty=4,
            topics=("Cinematica", "Dinamica", "Rozamiento"),
        )
    ]
    options = PlanOptions(
        from_date=start,
        weekly_hours=4.0,
        weeks=1,
        session_minutes=60,
        max_daily_hours=3.0,
        day_start_hour=18,
    )

    sessions = build_study_plan(events, options)
    assert sessions
    assert all(session.focus_topic.strip() for session in sessions)
    assert all(session.focus_reason.strip() for session in sessions)
    assert any("Cinematica" in session.focus_topic or "Dinamica" in session.focus_topic for session in sessions)


def test_render_ics_contains_events():
    session = StudySession(
        id="2026-04-20-mecanismos-1",
        materia="Mecanismos",
        start=datetime(2026, 4, 20, 19, 0),
        end=datetime(2026, 4, 20, 20, 30),
        duration_minutes=90,
        week_index=0,
        target_date=date(2026, 4, 24),
        target_event_type="parcial",
        target_title="Parcial Meca",
        focus_topic="Repaso activo: Cinematica",
        focus_reason="Faltan 4 dias para parcial 'Parcial Meca'; fase de cierre previa al objetivo.",
    )
    payload = render_ics([session], calendar_name="Plan FIUBA")

    assert "BEGIN:VCALENDAR" in payload
    assert "SUMMARY:Estudio - Mecanismos" in payload
    assert "Tema foco: Repaso activo: Cinematica" in payload
    assert "X-WR-CALNAME:Plan FIUBA" in payload
