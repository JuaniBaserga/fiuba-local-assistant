from __future__ import annotations

import argparse
import csv
import os
from datetime import date, datetime
from pathlib import Path

from .config import DEFAULT_DB_PATH, DEFAULT_FACULTAD_ROOT
from .envfile import load_env_file
from .indexer import index_materia
from .ocr_scan import scan_ocr_candidates
from .ollama_client import OllamaError, generate_answer
from .search import rank_hits, search_chunks, stats as get_stats
from .study import (
    DEFAULT_STUDY_DATES_PATH,
    DEFAULT_STUDY_STATE_PATH,
    PlanOptions,
    ReportOutput,
    StudySession,
    build_report,
    build_study_plan,
    load_events,
    load_state,
    render_ics,
    save_state,
    save_template_files,
    sync_sessions_to_google_calendar,
)
from .webapp import run_server


def _positive_int(value: str) -> int:
    n = int(value)
    if n <= 0:
        raise argparse.ArgumentTypeError("Debe ser un entero positivo.")
    return n


def _positive_float(value: str) -> float:
    n = float(value)
    if n <= 0:
        raise argparse.ArgumentTypeError("Debe ser un numero positivo.")
    return n


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fiuba-local",
        description="Asistente FIUBA local - Fase 1 (indexado + busqueda).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_FACULTAD_ROOT,
        help=f"Raiz de carpetas de materias (default: {DEFAULT_FACULTAD_ROOT})",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Ruta del indice sqlite (default: {DEFAULT_DB_PATH})",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_index = sub.add_parser("index", help="Indexa una materia.")
    p_index.add_argument("--materia", required=True, help="Nombre exacto de la carpeta de materia.")

    p_ask = sub.add_parser("ask", help="Busca fragmentos relevantes.")
    p_ask.add_argument("query", help="Pregunta o consulta.")
    p_ask.add_argument("--materia", help="Filtra por materia.")
    p_ask.add_argument("--top-k", type=_positive_int, default=5, help="Cantidad de resultados.")

    p_answer = sub.add_parser("answer", help="Responde usando Ollama + contexto recuperado.")
    p_answer.add_argument("query", help="Pregunta o consulta.")
    p_answer.add_argument("--materia", help="Filtra por materia.")
    p_answer.add_argument("--top-k", type=_positive_int, default=6, help="Cantidad de fragmentos a recuperar.")
    p_answer.add_argument("--model", default="qwen2.5:7b-instruct", help="Modelo local en Ollama.")
    p_answer.add_argument("--timeout-sec", type=_positive_int, default=300, help="Timeout de consulta a Ollama.")
    p_answer.add_argument(
        "--ollama-host",
        default="http://127.0.0.1:11434",
        help="Endpoint de Ollama local.",
    )

    p_serve = sub.add_parser("serve", help="Levanta una UI web local en localhost.")
    p_serve.add_argument("--host", default="127.0.0.1", help="Host del servidor web.")
    p_serve.add_argument("--port", type=_positive_int, default=8787, help="Puerto del servidor web.")
    p_serve.add_argument("--model", default="qwen2.5:3b-instruct", help="Modelo por defecto de Ollama.")
    p_serve.add_argument("--top-k", type=_positive_int, default=6, help="Top-k por defecto.")
    p_serve.add_argument("--timeout-sec", type=_positive_int, default=300, help="Timeout de consulta a Ollama.")
    p_serve.add_argument(
        "--openai-api-key",
        default=os.getenv("OPENAI_API_KEY", ""),
        help="API key de OpenAI (opcional).",
    )
    p_serve.add_argument(
        "--gemini-api-key",
        default=os.getenv("GEMINI_API_KEY", ""),
        help="API key de Gemini (opcional).",
    )
    p_serve.add_argument(
        "--openai-base-url",
        default="https://api.openai.com/v1",
        help="Base URL de OpenAI.",
    )
    p_serve.add_argument(
        "--gemini-base-url",
        default="https://generativelanguage.googleapis.com/v1beta",
        help="Base URL de Gemini.",
    )
    p_serve.add_argument(
        "--ollama-host",
        default="http://127.0.0.1:11434",
        help="Endpoint de Ollama local.",
    )

    p_study = sub.add_parser("study", help="Planificacion de estudio y calendario.")
    study_sub = p_study.add_subparsers(dest="study_cmd", required=True)

    p_study_init = study_sub.add_parser("init", help="Crea templates de fechas y estado.")
    p_study_init.add_argument(
        "--dates-file",
        type=Path,
        default=DEFAULT_STUDY_DATES_PATH,
        help="Archivo JSON con fechas academicas.",
    )
    p_study_init.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH,
        help="Archivo JSON de estado de estudio.",
    )
    p_study_init.add_argument("--overwrite", action="store_true", help="Sobrescribe archivos existentes.")

    p_study_plan = study_sub.add_parser("plan", help="Genera sesiones de estudio.")
    p_study_plan.add_argument(
        "--dates-file",
        type=Path,
        default=DEFAULT_STUDY_DATES_PATH,
        help="Archivo JSON con fechas academicas.",
    )
    p_study_plan.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH,
        help="Archivo JSON de estado de estudio.",
    )
    p_study_plan.add_argument("--from-date", type=date.fromisoformat, help="Fecha inicial (YYYY-MM-DD).")
    p_study_plan.add_argument("--weekly-hours", type=_positive_float, help="Horas disponibles por semana.")
    p_study_plan.add_argument("--weeks", type=_positive_int, help="Cantidad de semanas a planificar.")
    p_study_plan.add_argument("--session-minutes", type=_positive_int, help="Duracion de sesion.")
    p_study_plan.add_argument("--max-daily-hours", type=_positive_float, help="Maximo de horas por dia.")
    p_study_plan.add_argument("--day-start-hour", type=int, help="Hora de inicio sugerida (0-23).")
    p_study_plan.add_argument("--out-csv", type=Path, help="Exporta sesiones a CSV.")

    p_study_ics = study_sub.add_parser("export-ics", help="Exporta sesiones a calendario ICS.")
    p_study_ics.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH,
        help="Archivo JSON de estado de estudio.",
    )
    p_study_ics.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH.parent / "study_plan.ics",
        help="Ruta del archivo ICS de salida.",
    )
    p_study_ics.add_argument("--calendar-name", default="FIUBA Study Plan", help="Nombre del calendario.")

    p_study_log = study_sub.add_parser("log", help="Marca una sesion como completada.")
    p_study_log.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH,
        help="Archivo JSON de estado de estudio.",
    )
    p_study_log.add_argument("--session-id", required=True, help="ID de la sesion a marcar como completada.")

    p_study_report = study_sub.add_parser("report", help="Genera reporte de planificado vs completado.")
    p_study_report.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH,
        help="Archivo JSON de estado de estudio.",
    )
    p_study_report.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH.parent / "reports",
        help="Directorio de salida para CSV y graficos.",
    )

    p_study_sync = study_sub.add_parser("sync-gcal", help="Sincroniza sesiones con Google Calendar.")
    p_study_sync.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH,
        help="Archivo JSON de estado de estudio.",
    )
    p_study_sync.add_argument("--calendar-id", default="primary", help="Calendar ID destino (default: primary).")
    p_study_sync.add_argument(
        "--credentials-file",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH.parent / "gcal_credentials.json",
        help="Client secrets OAuth descargado desde Google Cloud.",
    )
    p_study_sync.add_argument(
        "--token-file",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH.parent / "gcal_token.json",
        help="Token OAuth local cacheado.",
    )
    p_study_sync.add_argument(
        "--timezone",
        default="America/Argentina/Buenos_Aires",
        help="Zona horaria para crear eventos.",
    )
    p_study_sync.add_argument("--max-events", type=_positive_int, help="Limite de eventos a sincronizar.")
    p_study_sync.add_argument("--dry-run", action="store_true", help="No crea eventos, solo simula.")
    p_study_sync.add_argument("--force-resync", action="store_true", help="Ignora cache local de sesiones sincronizadas.")

    p_ocr = sub.add_parser("ocr-check", help="Detecta PDFs candidatos a OCR.")
    p_ocr.add_argument("--materia", help="Materia a escanear. Si se omite, escanea toda la raiz.")
    p_ocr.add_argument(
        "--min-total-chars",
        type=_positive_int,
        default=120,
        help="Umbral minimo de caracteres totales extraidos.",
    )
    p_ocr.add_argument(
        "--min-chars-per-page",
        type=_positive_int,
        default=60,
        help="Umbral minimo de caracteres promedio por pagina.",
    )
    p_ocr.add_argument("--only-needs-ocr", action="store_true", help="Mostrar solo candidatos a OCR.")
    p_ocr.add_argument("--limit", type=int, default=0, help="Limite de filas mostradas (0 = sin limite).")

    sub.add_parser("stats", help="Muestra estado del indice.")
    return parser


def run_index(args: argparse.Namespace) -> int:
    stats = index_materia(
        db_path=args.db.expanduser(),
        facultad_root=args.root.expanduser(),
        materia=args.materia,
    )
    print("Indexacion finalizada")
    print(f"- Archivos escaneados: {stats.scanned}")
    print(f"- Archivos actualizados: {stats.updated}")
    print(f"- Sin cambios: {stats.skipped_unchanged}")
    print(f"- Omitidos sin texto util: {stats.skipped_unsupported + stats.skipped_empty}")
    print(f"- Advertencias de extraccion: {stats.warnings}")
    return 0


def run_ask(args: argparse.Namespace) -> int:
    hits = search_chunks(
        db_path=args.db.expanduser(),
        query=args.query,
        materia=args.materia,
        limit=args.top_k,
    )
    if not hits:
        print("Sin resultados. Proba otra consulta o indexa la materia primero.")
        return 0

    print(f"Resultados para: {args.query!r}")
    if args.materia:
        print(f"Filtro materia: {args.materia}")
    for i, hit in enumerate(hits, start=1):
        preview = hit.text.replace("\n", " ")
        if len(preview) > 260:
            preview = preview[:260] + "..."
        print(f"\n[{i}] {Path(hit.path).name} (chunk {hit.chunk_idx}, score={hit.score:.3f})")
        print(f"Fuente: {hit.path}")
        print(preview)
    return 0


def _build_context(hits) -> str:
    blocks: list[str] = []
    for i, hit in enumerate(hits, start=1):
        src = f"{Path(hit.path).name} (chunk {hit.chunk_idx})"
        blocks.append(f"[S{i}] {src}\n{hit.text}")
    return "\n\n".join(blocks)


def run_answer(args: argparse.Namespace) -> int:
    hits = search_chunks(
        db_path=args.db.expanduser(),
        query=args.query,
        materia=args.materia,
        limit=args.top_k,
    )
    hits = rank_hits(args.query, hits)
    if not hits:
        print("Sin resultados en el indice. Ejecuta `index` primero o ajusta la consulta.")
        return 0

    context = _build_context(hits)
    try:
        llm = generate_answer(
            host=args.ollama_host,
            model=args.model,
            user_question=args.query,
            context_block=context,
            timeout_sec=args.timeout_sec,
        )
    except OllamaError as exc:
        print(f"Error Ollama: {exc}")
        print("Tip: instala y arranca Ollama, luego descarga un modelo.")
        print("  brew install ollama")
        print("  ollama serve")
        print("  ollama pull qwen2.5:7b-instruct")
        return 1

    print(f"Modelo: {llm.model}")
    if args.materia:
        print(f"Materia: {args.materia}")
    print()
    print(llm.content)
    print("\nFuentes recuperadas:")
    for i, hit in enumerate(hits, start=1):
        print(f"[S{i}] {hit.path} (chunk {hit.chunk_idx})")
    return 0


def run_stats(args: argparse.Namespace) -> int:
    s = get_stats(args.db.expanduser())
    print("Estado del indice")
    print(f"- Materias: {s['materias']}")
    print(f"- Documentos: {s['documents']}")
    print(f"- Chunks: {s['chunks']}")
    return 0


def run_serve(args: argparse.Namespace) -> int:
    run_server(
        host=args.host,
        port=args.port,
        root_path=args.root.expanduser(),
        db_path=args.db.expanduser(),
        ollama_host=args.ollama_host,
        openai_api_key=args.openai_api_key,
        gemini_api_key=args.gemini_api_key,
        openai_base_url=args.openai_base_url,
        gemini_base_url=args.gemini_base_url,
        model=args.model,
        timeout_sec=args.timeout_sec,
        top_k=args.top_k,
    )
    return 0


def _state_config(state: dict) -> dict:
    cfg = state.get("config")
    if isinstance(cfg, dict):
        return cfg
    return {}


def run_study_init(args: argparse.Namespace) -> int:
    today = date.today()
    dates_path = args.dates_file.expanduser()
    state_path = args.state_file.expanduser()
    wrote_dates, wrote_state = save_template_files(
        dates_path=dates_path,
        state_path=state_path,
        today=today,
        overwrite=args.overwrite,
    )
    if wrote_dates:
        print(f"Template de fechas creado: {dates_path}")
    else:
        print(f"Fechas existentes, sin cambios: {dates_path}")
    if wrote_state:
        print(f"Estado de estudio creado: {state_path}")
    else:
        print(f"Estado existente, sin cambios: {state_path}")
    return 0


def _sessions_to_csv(path: Path, sessions: list[StudySession]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "id",
                "materia",
                "start",
                "end",
                "duration_minutes",
                "week_index",
                "target_date",
                "target_event_type",
                "target_title",
            ],
        )
        writer.writeheader()
        for session in sessions:
            writer.writerow(session.to_dict())


def run_study_plan(args: argparse.Namespace) -> int:
    dates_path = args.dates_file.expanduser()
    state_path = args.state_file.expanduser()
    try:
        events = load_events(dates_path)
    except FileNotFoundError:
        print(f"No existe el archivo de fechas: {dates_path}")
        print("Ejecuta `fiuba-local study init` para crear templates.")
        return 1
    if not events:
        print("No hay eventos en el archivo de fechas.")
        return 0

    try:
        state = load_state(state_path)
    except FileNotFoundError:
        _, wrote_state = save_template_files(
            dates_path=dates_path,
            state_path=state_path,
            today=date.today(),
            overwrite=False,
        )
        state = load_state(state_path)
        if wrote_state:
            print(f"Estado inicial creado automaticamente: {state_path}")

    cfg = _state_config(state)
    from_date = args.from_date or date.today()
    weekly_hours = args.weekly_hours if args.weekly_hours is not None else float(cfg.get("weekly_hours", 10.0))
    weeks = args.weeks if args.weeks is not None else int(cfg.get("weeks", 6))
    session_minutes = args.session_minutes if args.session_minutes is not None else int(cfg.get("session_minutes", 90))
    max_daily_hours = (
        args.max_daily_hours if args.max_daily_hours is not None else float(cfg.get("max_daily_hours", 3.0))
    )
    day_start_hour = args.day_start_hour if args.day_start_hour is not None else int(cfg.get("day_start_hour", 19))
    if day_start_hour < 0 or day_start_hour > 23:
        raise ValueError("`--day-start-hour` debe estar entre 0 y 23.")

    plan_options = PlanOptions(
        from_date=from_date,
        weekly_hours=weekly_hours,
        weeks=weeks,
        session_minutes=session_minutes,
        max_daily_hours=max_daily_hours,
        day_start_hour=day_start_hour,
    )
    sessions = build_study_plan(events, plan_options)
    if not sessions:
        print("No hay eventos futuros para planificar.")
        return 0

    minutes_by_materia: dict[str, int] = {}
    for session in sessions:
        minutes_by_materia[session.materia] = minutes_by_materia.get(session.materia, 0) + session.duration_minutes

    state["config"] = {
        "weekly_hours": weekly_hours,
        "weeks": weeks,
        "session_minutes": session_minutes,
        "max_daily_hours": max_daily_hours,
        "day_start_hour": day_start_hour,
    }
    state["planned_sessions"] = [session.to_dict() for session in sessions]
    save_state(state_path, state)

    print(f"Plan generado: {len(sessions)} sesiones")
    print(f"Desde: {sessions[0].start.date().isoformat()} hasta: {sessions[-1].end.date().isoformat()}")
    print("Horas por materia:")
    for materia, minutes in sorted(minutes_by_materia.items(), key=lambda kv: kv[1], reverse=True):
        print(f"- {materia}: {minutes / 60:.2f} h")
    print(f"Estado actualizado: {state_path}")

    if args.out_csv:
        out_csv = args.out_csv.expanduser()
        _sessions_to_csv(out_csv, sessions)
        print(f"CSV exportado: {out_csv}")
    return 0


def run_study_export_ics(args: argparse.Namespace) -> int:
    state_path = args.state_file.expanduser()
    try:
        state = load_state(state_path)
    except FileNotFoundError:
        print(f"No existe el archivo de estado: {state_path}")
        print("Ejecuta `fiuba-local study init` y luego `fiuba-local study plan`.")
        return 1
    raw_sessions = state.get("planned_sessions", [])
    if not isinstance(raw_sessions, list) or not raw_sessions:
        print("No hay sesiones planificadas en el estado. Ejecuta `study plan` primero.")
        return 0

    sessions: list[StudySession] = []
    for idx, raw in enumerate(raw_sessions, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"Sesion invalida en posicion {idx}.")
        sessions.append(StudySession.from_dict(raw))

    ics_payload = render_ics(sessions, calendar_name=args.calendar_name)
    output = args.output.expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(ics_payload, encoding="utf-8")
    print(f"Archivo ICS generado: {output}")
    print(f"Eventos exportados: {len(sessions)}")
    return 0


def _load_planned_sessions_from_state(state: dict) -> list[StudySession]:
    raw_sessions = state.get("planned_sessions", [])
    if not isinstance(raw_sessions, list):
        raise ValueError("`planned_sessions` debe ser una lista.")
    sessions: list[StudySession] = []
    for idx, raw in enumerate(raw_sessions, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"Sesion invalida en posicion {idx}.")
        sessions.append(StudySession.from_dict(raw))
    return sessions


def _completed_records(state: dict) -> list[dict]:
    raw = state.get("completed_sessions", [])
    if isinstance(raw, list):
        out: list[dict] = []
        for item in raw:
            if isinstance(item, dict):
                out.append(item)
        return out
    return []


def _completed_ids(state: dict) -> set[str]:
    ids: set[str] = set()
    for item in _completed_records(state):
        sid = item.get("session_id")
        if isinstance(sid, str) and sid:
            ids.add(sid)
    return ids


def run_study_log(args: argparse.Namespace) -> int:
    state_path = args.state_file.expanduser()
    try:
        state = load_state(state_path)
    except FileNotFoundError:
        print(f"No existe el archivo de estado: {state_path}")
        print("Ejecuta `fiuba-local study init` y luego `fiuba-local study plan`.")
        return 1

    sessions = _load_planned_sessions_from_state(state)
    if not sessions:
        print("No hay sesiones planificadas. Ejecuta `study plan` primero.")
        return 0

    session_by_id = {session.id: session for session in sessions}
    if args.session_id not in session_by_id:
        print(f"Sesion no encontrada: {args.session_id}")
        print("Tip: revisa IDs en `study_plan.csv` o en `study_state.json`.")
        return 1

    completed = _completed_records(state)
    for item in completed:
        if item.get("session_id") == args.session_id:
            print(f"La sesion ya estaba marcada como completada: {args.session_id}")
            return 0

    completed.append(
        {
            "session_id": args.session_id,
            "completed_at": datetime.now().isoformat(timespec="seconds"),
        }
    )
    state["completed_sessions"] = completed
    save_state(state_path, state)

    session = session_by_id[args.session_id]
    print(f"Sesion marcada como completada: {session.id}")
    print(f"- Materia: {session.materia}")
    print(f"- Inicio: {session.start.isoformat(timespec='minutes')}")
    return 0


def run_study_report(args: argparse.Namespace) -> int:
    state_path = args.state_file.expanduser()
    try:
        state = load_state(state_path)
    except FileNotFoundError:
        print(f"No existe el archivo de estado: {state_path}")
        print("Ejecuta `fiuba-local study init` y luego `fiuba-local study plan`.")
        return 1

    sessions = _load_planned_sessions_from_state(state)
    if not sessions:
        print("No hay sesiones planificadas. Ejecuta `study plan` primero.")
        return 0

    completed_ids = _completed_ids(state)
    report: ReportOutput = build_report(
        planned_sessions=sessions,
        completed_session_ids=completed_ids,
        output_dir=args.output_dir.expanduser(),
    )
    total_minutes = sum(s.duration_minutes for s in sessions)
    completed_minutes = sum(s.duration_minutes for s in sessions if s.id in completed_ids)
    pct = (completed_minutes / total_minutes * 100.0) if total_minutes > 0 else 0.0

    print("Reporte generado")
    print(f"- Total planificado: {total_minutes / 60.0:.2f} h")
    print(f"- Total completado: {completed_minutes / 60.0:.2f} h ({pct:.2f}%)")
    print(f"- CSV semanal: {report.weekly_csv}")
    print(f"- CSV por materia: {report.materia_csv}")
    print(f"- Grafico planificado: {report.planned_svg}")
    print(f"- Grafico comparativo: {report.compare_svg}")
    return 0


def run_study_sync_gcal(args: argparse.Namespace) -> int:
    state_path = args.state_file.expanduser()
    try:
        state = load_state(state_path)
    except FileNotFoundError:
        print(f"No existe el archivo de estado: {state_path}")
        print("Ejecuta `fiuba-local study init` y luego `fiuba-local study plan`.")
        return 1

    sessions = _load_planned_sessions_from_state(state)
    if not sessions:
        print("No hay sesiones planificadas. Ejecuta `study plan` primero.")
        return 0

    gcal_block = state.get("gcal", {})
    if not isinstance(gcal_block, dict):
        gcal_block = {}
    raw_synced = gcal_block.get("synced_session_ids", [])
    synced_ids = {sid for sid in raw_synced if isinstance(sid, str)}

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
    if args.dry_run:
        print("No se creo ningun evento (modo simulacion).")
    else:
        print(f"Estado actualizado: {state_path}")
    return 0


def run_ocr_check(args: argparse.Namespace) -> int:
    root = args.root.expanduser()
    if args.materia:
        scope = root / args.materia
        if not scope.exists() or not scope.is_dir():
            print(f"No existe la materia en: {scope}")
            return 1
    else:
        scope = root
        if not scope.exists() or not scope.is_dir():
            print(f"No existe la raiz: {scope}")
            return 1

    if args.limit < 0:
        print("--limit no puede ser negativo.")
        return 1

    results = scan_ocr_candidates(
        scope=scope,
        min_total_chars=args.min_total_chars,
        min_chars_per_page=args.min_chars_per_page,
    )
    if args.only_needs_ocr:
        results = [r for r in results if r.needs_ocr]
    if args.limit > 0:
        results = results[: args.limit]

    total = len(results)
    flagged = sum(1 for r in results if r.needs_ocr)
    print(f"OCR scan scope: {scope}")
    print(f"- PDFs evaluados: {total}")
    print(f"- Candidatos OCR: {flagged}")
    print(f"- Umbrales: total_chars<{args.min_total_chars}, chars/pag<{args.min_chars_per_page}")

    if total == 0:
        print("Sin PDFs para mostrar con esos filtros.")
        return 0

    print("\nResultados:")
    for item in results:
        status = "OCR" if item.needs_ocr else "OK"
        pages = str(item.pages) if item.pages is not None else "?"
        avg = f"{item.avg_chars_per_page:.1f}" if item.avg_chars_per_page is not None else "?"
        print(f"- [{status}] {item.path}")
        print(f"  pages={pages} chars={item.total_chars} avg_chars_per_page={avg}")
        print(f"  razon={item.reason}")
        if item.warning:
            print(f"  warning={item.warning}")
        if item.needs_ocr:
            out_path = item.path.with_name(item.path.stem + ".ocr.pdf")
            print(f"  sugerencia: ocrmypdf --skip-text '{item.path}' '{out_path}'")
    return 0


def main() -> int:
    load_env_file(Path.cwd() / ".env")
    parser = build_parser()
    args = parser.parse_args()
    if args.cmd == "index":
        return run_index(args)
    if args.cmd == "ask":
        return run_ask(args)
    if args.cmd == "answer":
        return run_answer(args)
    if args.cmd == "serve":
        return run_serve(args)
    if args.cmd == "study":
        if args.study_cmd == "init":
            return run_study_init(args)
        if args.study_cmd == "plan":
            return run_study_plan(args)
        if args.study_cmd == "export-ics":
            return run_study_export_ics(args)
        if args.study_cmd == "log":
            return run_study_log(args)
        if args.study_cmd == "report":
            return run_study_report(args)
        if args.study_cmd == "sync-gcal":
            return run_study_sync_gcal(args)
        raise ValueError(f"Subcomando desconocido: {args.study_cmd}")
    if args.cmd == "ocr-check":
        return run_ocr_check(args)
    if args.cmd == "stats":
        return run_stats(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
