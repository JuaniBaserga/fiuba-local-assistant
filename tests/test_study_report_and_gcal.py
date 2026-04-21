from datetime import date, datetime

from fiuba_local.study.calendar_google import sync_sessions_to_google_calendar
from fiuba_local.study.report import build_report
from fiuba_local.study.types import StudySession


def _sample_sessions() -> list[StudySession]:
    return [
        StudySession(
            id="s1",
            materia="Mecanismos",
            start=datetime(2026, 4, 20, 19, 0),
            end=datetime(2026, 4, 20, 20, 30),
            duration_minutes=90,
            week_index=0,
            target_date=date(2026, 4, 24),
            target_event_type="parcial",
            target_title="P1",
        ),
        StudySession(
            id="s2",
            materia="Automatizacion",
            start=datetime(2026, 4, 21, 19, 0),
            end=datetime(2026, 4, 21, 20, 0),
            duration_minutes=60,
            week_index=0,
            target_date=date(2026, 4, 30),
            target_event_type="entrega",
            target_title="TP",
        ),
    ]


def test_build_report_generates_files(tmp_path):
    sessions = _sample_sessions()
    out = build_report(
        planned_sessions=sessions,
        completed_session_ids={"s1"},
        output_dir=tmp_path,
    )
    assert out.weekly_csv.exists()
    assert out.materia_csv.exists()
    assert out.planned_svg.exists()
    assert out.compare_svg.exists()

    weekly_text = out.weekly_csv.read_text(encoding="utf-8")
    assert "completion_rate_pct" in weekly_text
    assert "Mecanismos" in weekly_text

    svg_text = out.compare_svg.read_text(encoding="utf-8")
    assert "Planificado vs Completado" in svg_text


def test_sync_sessions_to_google_calendar_dry_run_does_not_require_google_libs(tmp_path):
    sessions = _sample_sessions()
    result = sync_sessions_to_google_calendar(
        sessions=sessions,
        calendar_id="primary",
        credentials_file=tmp_path / "creds.json",
        token_file=tmp_path / "token.json",
        timezone="America/Argentina/Buenos_Aires",
        dry_run=True,
        already_synced_ids={"s1"},
        force_resync=False,
        max_events=None,
    )
    assert result.attempted == 2
    assert result.created == 1
    assert result.skipped == 1
    assert result.errors == 0
    assert "s2" in result.synced_ids
