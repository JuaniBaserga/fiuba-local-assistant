from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, datetime
from pathlib import Path

from ..study import (
    DEFAULT_STUDY_DATES_PATH,
    PlanRequest,
    StudyService,
    StudyValidationError,
    completed_ids,
    completed_records,
    load_state,
    planned_sessions,
    save_state,
    state_config,
    sync_sessions_to_google_calendar,
)
from ..study.types import StudySession


def _confirm(prompt: str) -> bool:
    if not sys.stdin.isatty():
        raise RuntimeError("`--confirm-with-user` requiere una terminal interactiva (TTY).")
    return input(prompt).strip().lower() in {"s", "si", "sí", "y", "yes"}


def run_study_init(args: argparse.Namespace) -> int:
    dates_path = args.dates_file.expanduser()
    state_path = args.state_file.expanduser()
    wrote_dates, wrote_state = StudyService(dates_path, state_path).initialize(args.overwrite, date.today())
    print(f"Template de fechas creado: {dates_path}" if wrote_dates else f"Fechas existentes, sin cambios: {dates_path}")
    print(f"Estado de estudio creado: {state_path}" if wrote_state else f"Estado existente, sin cambios: {state_path}")
    return 0


def _sessions_to_csv(path: Path, sessions: list[StudySession]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(sessions[0].to_dict().keys()))
        writer.writeheader()
        writer.writerows(session.to_dict() for session in sessions)


def run_study_plan(args: argparse.Namespace) -> int:
    dates_path = args.dates_file.expanduser()
    state_path = args.state_file.expanduser()
    service = StudyService(dates_path, state_path)
    try:
        events, state = service.load()
    except FileNotFoundError:
        if not dates_path.exists():
            print(f"No existe el archivo de fechas: {dates_path}")
            print("Ejecuta `fiuba-local study init` para crear templates.")
            return 1
        _, wrote_state = service.initialize(overwrite=False)
        events, state = service.load()
        if wrote_state:
            print(f"Estado inicial creado automaticamente: {state_path}")
    except StudyValidationError as exc:
        print(f"Estado de estudio invalido: {exc}")
        return 1
    if not events:
        print("No hay eventos en el archivo de fechas.")
        return 0

    try:
        request = PlanRequest.from_mapping(
            {
                "from_date": args.from_date,
                "weekly_hours": args.weekly_hours,
                "weeks": args.weeks,
                "session_minutes": args.session_minutes,
                "max_daily_hours": args.max_daily_hours,
                "day_start_hour": args.day_start_hour,
            },
            state_config(state),
        )
        sessions = service.build_plan(events, request)
    except StudyValidationError as exc:
        print(f"Error de planificacion: {exc}")
        return 1
    if not sessions:
        print("No hay eventos futuros para planificar.")
        return 0

    minutes_by_materia: dict[str, int] = {}
    for session in sessions:
        minutes_by_materia[session.materia] = minutes_by_materia.get(session.materia, 0) + session.duration_minutes
    print(f"Plan generado: {len(sessions)} sesiones")
    print(f"Desde: {sessions[0].start.date().isoformat()} hasta: {sessions[-1].end.date().isoformat()}")
    print("Horas por materia:")
    for materia, minutes in sorted(minutes_by_materia.items(), key=lambda item: item[1], reverse=True):
        print(f"- {materia}: {minutes / 60:.2f} h")
    print("Primeras sesiones (tema foco y razon):")
    for session in sessions[:10]:
        print(f"- {session.start:%Y-%m-%d %H:%M} | {session.materia} | {session.focus_topic}")
        print(f"  {session.focus_reason}")

    if args.confirm_with_user:
        try:
            confirmed = _confirm("Guardar este plan en study_state.json? [s/N]: ")
        except RuntimeError as exc:
            print(str(exc))
            return 1
        if not confirmed:
            print("Plan cancelado por el usuario. No se guardaron cambios.")
            return 0
    service.save_plan(state, request, sessions)
    print(f"Estado actualizado: {state_path}")
    if args.out_csv:
        output = args.out_csv.expanduser()
        _sessions_to_csv(output, sessions)
        print(f"CSV exportado: {output}")
    return 0


def run_study_export_ics(args: argparse.Namespace) -> int:
    state_path = args.state_file.expanduser()
    service = StudyService(DEFAULT_STUDY_DATES_PATH, state_path)
    try:
        sessions = service.sessions()
    except FileNotFoundError:
        print(f"No existe el archivo de estado: {state_path}")
        print("Ejecuta `fiuba-local study init` y luego `fiuba-local study plan`.")
        return 1
    except StudyValidationError as exc:
        print(f"Estado de estudio invalido: {exc}")
        return 1
    if not sessions:
        print("No hay sesiones planificadas en el estado. Ejecuta `study plan` primero.")
        return 0
    output = args.output.expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(service.export_ics(args.calendar_name), encoding="utf-8")
    print(f"Archivo ICS generado: {output}")
    print(f"Eventos exportados: {len(sessions)}")
    return 0


def _load_state_with_sessions(state_path: Path) -> tuple[dict, list[StudySession]] | None:
    try:
        state = load_state(state_path)
    except FileNotFoundError:
        print(f"No existe el archivo de estado: {state_path}")
        print("Ejecuta `fiuba-local study init` y luego `fiuba-local study plan`.")
        return None
    try:
        return state, planned_sessions(state)
    except (StudyValidationError, ValueError) as exc:
        print(f"Estado de estudio invalido: {exc}")
        return None


def run_study_log(args: argparse.Namespace) -> int:
    state_path = args.state_file.expanduser()
    loaded = _load_state_with_sessions(state_path)
    if loaded is None:
        return 1
    state, sessions = loaded
    if not sessions:
        print("No hay sesiones planificadas. Ejecuta `study plan` primero.")
        return 0
    session_by_id = {session.id: session for session in sessions}
    session = session_by_id.get(args.session_id)
    if session is None:
        print(f"Sesion no encontrada: {args.session_id}")
        print("Tip: revisa IDs en `study_plan.csv` o en `study_state.json`.")
        return 1
    completed = completed_records(state)
    if any(item.get("session_id") == args.session_id for item in completed):
        print(f"La sesion ya estaba marcada como completada: {args.session_id}")
        return 0
    completed.append({"session_id": args.session_id, "completed_at": datetime.now().isoformat(timespec="seconds")})
    state["completed_sessions"] = completed
    save_state(state_path, state)
    print(f"Sesion marcada como completada: {session.id}")
    print(f"- Materia: {session.materia}")
    print(f"- Inicio: {session.start.isoformat(timespec='minutes')}")
    return 0


def run_study_report(args: argparse.Namespace) -> int:
    state_path = args.state_file.expanduser()
    loaded = _load_state_with_sessions(state_path)
    if loaded is None:
        return 1
    state, sessions = loaded
    if not sessions:
        print("No hay sesiones planificadas. Ejecuta `study plan` primero.")
        return 0
    done_ids = completed_ids(state)
    report = StudyService(DEFAULT_STUDY_DATES_PATH, state_path).report(args.output_dir.expanduser())
    total_minutes = sum(session.duration_minutes for session in sessions)
    completed_minutes = sum(session.duration_minutes for session in sessions if session.id in done_ids)
    percentage = completed_minutes / total_minutes * 100.0 if total_minutes else 0.0
    print("Reporte generado")
    print(f"- Total planificado: {total_minutes / 60.0:.2f} h")
    print(f"- Total completado: {completed_minutes / 60.0:.2f} h ({percentage:.2f}%)")
    print(f"- CSV semanal: {report.weekly_csv}")
    print(f"- CSV por materia: {report.materia_csv}")
    print(f"- Grafico planificado: {report.planned_svg}")
    print(f"- Grafico comparativo: {report.compare_svg}")
    return 0


def run_study_sync_gcal(args: argparse.Namespace) -> int:
    state_path = args.state_file.expanduser()
    loaded = _load_state_with_sessions(state_path)
    if loaded is None:
        return 1
    state, sessions = loaded
    if not sessions:
        print("No hay sesiones planificadas. Ejecuta `study plan` primero.")
        return 0
    gcal = state.get("gcal", {})
    gcal = gcal if isinstance(gcal, dict) else {}
    synced_ids = {item for item in gcal.get("synced_session_ids", []) if isinstance(item, str)}
    if args.confirm_with_user and not args.dry_run:
        selected = len(sessions) if args.max_events is None else min(len(sessions), args.max_events)
        print(f"Se intentaran sincronizar hasta {selected} sesiones en calendario '{args.calendar_id}'.")
        try:
            if not _confirm("Continuar con sync real a Google Calendar? [s/N]: "):
                print("Sincronizacion cancelada por el usuario.")
                return 0
        except RuntimeError as exc:
            print(str(exc))
            return 1
    try:
        result = sync_sessions_to_google_calendar(
            sessions=sessions,
            calendar_id=args.calendar_id,
            credentials_file=args.credentials_file.expanduser(),
            token_file=args.token_file.expanduser(),
            timezone=args.timezone,
            dry_run=args.dry_run,
            already_synced_ids=synced_ids,
            force_resync=args.force_resync,
            max_events=args.max_events,
        )
    except RuntimeError as exc:
        print(f"Error dependencias Google Calendar: {exc}")
        return 1
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    if not args.dry_run:
        state["gcal"] = {
            "calendar_id": args.calendar_id,
            "synced_session_ids": sorted(result.synced_ids),
            "last_sync_at": datetime.now().isoformat(timespec="seconds"),
            "timezone": args.timezone,
        }
        save_state(state_path, state)
    mode = "DRY-RUN" if args.dry_run else "SYNC"
    print(f"Google Calendar {mode} finalizado")
    print(f"- Intentados: {result.attempted}")
    print(f"- Creados: {result.created}")
    print(f"- Omitidos: {result.skipped}")
    print(f"- Errores: {result.errors}")
    print("No se creo ningun evento (modo simulacion)." if args.dry_run else f"Estado actualizado: {state_path}")
    return 0
