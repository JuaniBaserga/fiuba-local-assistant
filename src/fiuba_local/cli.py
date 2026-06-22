from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path

from .config import DEFAULT_DB_PATH, DEFAULT_FACULTAD_ROOT, DEFAULT_SEMANTIC_DB_PATH
from .commands import core as core_commands
from .commands import runtime as runtime_commands
from .commands import semantic as semantic_commands
from .commands import study as study_commands
from .envfile import load_env_file
from .semantic import DEFAULT_EMBEDDING_MODEL
from .study import DEFAULT_STUDY_DATES_PATH, DEFAULT_STUDY_STATE_PATH


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
        "--semantic-db",
        type=Path,
        default=DEFAULT_SEMANTIC_DB_PATH,
        help=f"Ruta del indice semantico experimental (default: {DEFAULT_SEMANTIC_DB_PATH})",
    )
    p_serve.add_argument(
        "--semantic-model",
        default=DEFAULT_EMBEDDING_MODEL,
        help="Modelo local de embeddings para /admin.",
    )
    p_serve.add_argument(
        "--study-dates",
        type=Path,
        default=DEFAULT_STUDY_DATES_PATH,
        help=f"Ruta del archivo de fechas de estudio (default: {DEFAULT_STUDY_DATES_PATH})",
    )
    p_serve.add_argument(
        "--study-state",
        type=Path,
        default=DEFAULT_STUDY_STATE_PATH,
        help=f"Ruta del archivo de estado de estudio (default: {DEFAULT_STUDY_STATE_PATH})",
    )
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
    p_study_plan.add_argument(
        "--confirm-with-user",
        action="store_true",
        help="Pide confirmacion interactiva antes de guardar el plan.",
    )

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
    p_study_sync.add_argument(
        "--confirm-with-user",
        action="store_true",
        help="Pide confirmacion interactiva antes de sincronizar (modo real).",
    )

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

    p_semantic = sub.add_parser("semantic", help="Indice experimental de busqueda semantica.")
    semantic_sub = p_semantic.add_subparsers(dest="semantic_cmd", required=True)

    p_semantic_index = semantic_sub.add_parser("index", help="Indexa el corpus piloto semantico.")
    p_semantic_index.add_argument("--materia", default="Ind Extractivas", help="Materia/carpeta piloto.")
    p_semantic_index.add_argument(
        "--semantic-db",
        type=Path,
        default=DEFAULT_SEMANTIC_DB_PATH,
        help=f"Ruta del indice semantico experimental (default: {DEFAULT_SEMANTIC_DB_PATH})",
    )
    p_semantic_index.add_argument(
        "--model",
        default=DEFAULT_EMBEDDING_MODEL,
        help="Modelo local de embeddings compatible con sentence-transformers.",
    )
    p_semantic_index.add_argument("--limit-files", type=_positive_int, default=10, help="Cantidad maxima de PDFs piloto.")
    p_semantic_index.add_argument(
        "--allow-model-download",
        action="store_true",
        help="Permite que sentence-transformers descargue el modelo si no esta cacheado.",
    )

    p_semantic_search = semantic_sub.add_parser("search", help="Busca vecinos semanticos en el indice experimental.")
    p_semantic_search.add_argument("query", help="Consulta semantica.")
    p_semantic_search.add_argument("--materia", help="Filtra por materia/area.")
    p_semantic_search.add_argument("--top-k", type=_positive_int, default=10, help="Cantidad de vecinos.")
    p_semantic_search.add_argument(
        "--semantic-db",
        type=Path,
        default=DEFAULT_SEMANTIC_DB_PATH,
        help=f"Ruta del indice semantico experimental (default: {DEFAULT_SEMANTIC_DB_PATH})",
    )
    p_semantic_search.add_argument(
        "--model",
        default=DEFAULT_EMBEDDING_MODEL,
        help="Modelo local de embeddings compatible con sentence-transformers.",
    )
    p_semantic_search.add_argument(
        "--allow-model-download",
        action="store_true",
        help="Permite que sentence-transformers descargue el modelo si no esta cacheado.",
    )

    p_semantic_stats = semantic_sub.add_parser("stats", help="Muestra estado del indice semantico.")
    p_semantic_stats.add_argument(
        "--semantic-db",
        type=Path,
        default=DEFAULT_SEMANTIC_DB_PATH,
        help=f"Ruta del indice semantico experimental (default: {DEFAULT_SEMANTIC_DB_PATH})",
    )

    sub.add_parser("stats", help="Muestra estado del indice.")
    return parser


def main() -> int:
    load_env_file(Path.cwd() / ".env")
    parser = build_parser()
    args = parser.parse_args()
    if args.cmd == "index":
        return core_commands.run_index(args)
    if args.cmd == "ask":
        return core_commands.run_ask(args)
    if args.cmd == "answer":
        return core_commands.run_answer(args)
    if args.cmd == "serve":
        return runtime_commands.run_serve(args)
    if args.cmd == "study":
        if args.study_cmd == "init":
            return study_commands.run_study_init(args)
        if args.study_cmd == "plan":
            return study_commands.run_study_plan(args)
        if args.study_cmd == "export-ics":
            return study_commands.run_study_export_ics(args)
        if args.study_cmd == "log":
            return study_commands.run_study_log(args)
        if args.study_cmd == "report":
            return study_commands.run_study_report(args)
        if args.study_cmd == "sync-gcal":
            return study_commands.run_study_sync_gcal(args)
        raise ValueError(f"Subcomando desconocido: {args.study_cmd}")
    if args.cmd == "ocr-check":
        return runtime_commands.run_ocr_check(args)
    if args.cmd == "semantic":
        if args.semantic_cmd == "index":
            return semantic_commands.run_semantic_index(args)
        if args.semantic_cmd == "search":
            return semantic_commands.run_semantic_search(args)
        if args.semantic_cmd == "stats":
            return semantic_commands.run_semantic_stats(args)
        raise ValueError(f"Subcomando desconocido: {args.semantic_cmd}")
    if args.cmd == "stats":
        return core_commands.run_stats(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
