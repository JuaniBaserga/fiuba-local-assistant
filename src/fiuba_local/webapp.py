from __future__ import annotations

import argparse
import json
import os
import sqlite3
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .config import DEFAULT_DB_PATH, DEFAULT_FACULTAD_ROOT, DEFAULT_SEMANTIC_DB_PATH
from .cloud_llm import (
    CloudLLMError,
    generate_gemini_answer,
    generate_openai_answer,
)
from .envfile import load_env_file
from .indexer import index_materia
from .ollama_client import OllamaError, generate_answer
from .search import rank_hits, search_chunks
from .semantic import (
    DEFAULT_EMBEDDING_MODEL,
    SentenceTransformerEmbedder,
    index_semantic_pilot,
    search_semantic,
    semantic_stats,
)
from .search import stats as fts_stats


STATIC_DIR = Path(__file__).parent / "static"


@dataclass(frozen=True)
class AppConfig:
    root_path: Path
    db_path: Path
    semantic_db_path: Path
    semantic_model: str
    ollama_host: str
    openai_api_key: str
    gemini_api_key: str
    openai_base_url: str
    gemini_base_url: str
    default_ollama_model: str
    default_openai_model: str
    default_gemini_model: str
    timeout_sec: int
    top_k: int


def _positive_int(value: str) -> int:
    n = int(value)
    if n <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return n


def _build_context(hits) -> str:
    blocks: list[str] = []
    for i, hit in enumerate(hits, start=1):
        src = f"{Path(hit.path).name} (chunk {hit.chunk_idx})"
        blocks.append(f"[S{i}] {src}\n{hit.text}")
    return "\n\n".join(blocks)


def _resolve_api_key(primary: str, env_names: list[str]) -> str:
    if primary.strip():
        return primary.strip()
    for env_name in env_names:
        value = os.getenv(env_name, "").strip()
        if value:
            return value
    return ""


def _resolve_model(engine: str, requested_model: str, config: AppConfig) -> str:
    model = requested_model.strip()
    if engine == "gemini":
        # If UI sends an Ollama/OpenAI model by mistake, use Gemini default.
        if not model or ":" in model or model.startswith("gpt-"):
            return config.default_gemini_model
        return model
    if engine == "openai":
        if not model or ":" in model or model.startswith("gemini-"):
            return config.default_openai_model
        return model
    if engine == "ollama":
        if not model:
            return config.default_ollama_model
        return model
    return model


def _list_indexed_materias(db_path: Path) -> list[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT DISTINCT materia FROM documents ORDER BY materia COLLATE NOCASE ASC"
        ).fetchall()
        return [str(row[0]) for row in rows if row and row[0]]
    finally:
        conn.close()


def _list_fs_materias(root_path: Path) -> list[str]:
    if not root_path.exists() or not root_path.is_dir():
        return []
    items = [
        path.name
        for path in root_path.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ]
    return sorted(items, key=lambda s: s.casefold())


class StudyHandler(BaseHTTPRequestHandler):
    config: AppConfig

    def _json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _text_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "file not found")
            return
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        # Keep terminal output concise while serving requests.
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._text_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if path == "/admin":
            self._text_file(STATIC_DIR / "admin.html", "text/html; charset=utf-8")
            return
        if path == "/assets/style.css":
            self._text_file(STATIC_DIR / "style.css", "text/css; charset=utf-8")
            return
        if path == "/assets/app.js":
            self._text_file(STATIC_DIR / "app.js", "application/javascript; charset=utf-8")
            return
        if path == "/assets/admin.js":
            self._text_file(STATIC_DIR / "admin.js", "application/javascript; charset=utf-8")
            return
        if path == "/api/health":
            self._json({"status": "ok"})
            return
        if path == "/api/admin/status":
            self._handle_admin_status()
            return
        if path == "/api/materias":
            available = _list_fs_materias(self.config.root_path)
            indexed = _list_indexed_materias(self.config.db_path)
            indexed_set = {m.casefold() for m in indexed}
            items = [
                {"name": materia, "indexed": materia.casefold() in indexed_set}
                for materia in available
            ]
            self._json(
                {
                    "materias": available,
                    "indexed_materias": indexed,
                    "items": items,
                }
            )
            return

        self.send_error(HTTPStatus.NOT_FOUND, "not found")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/index":
            self._handle_index()
            return
        if parsed.path == "/api/admin/semantic-index":
            self._handle_admin_semantic_index()
            return
        if parsed.path == "/api/admin/semantic-search":
            self._handle_admin_semantic_search()
            return
        if parsed.path != "/api/answer":
            self.send_error(HTTPStatus.NOT_FOUND, "not found")
            return

        raw_size = self.headers.get("Content-Length", "0")
        try:
            content_length = int(raw_size)
        except ValueError:
            self._json({"error": "invalid content-length"}, status=HTTPStatus.BAD_REQUEST)
            return
        if content_length <= 0 or content_length > 2_000_000:
            self._json({"error": "invalid request body size"}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            self._json({"error": "invalid json body"}, status=HTTPStatus.BAD_REQUEST)
            return

        question = str(payload.get("question", "")).strip()
        materia_raw = payload.get("materia")
        materia = str(materia_raw).strip() if materia_raw else None
        engine = str(payload.get("engine", "gemini")).strip().lower()
        requested_model = str(payload.get("model", "")).strip()
        timeout_sec = int(payload.get("timeout_sec", self.config.timeout_sec))
        top_k = int(payload.get("top_k", self.config.top_k))
        if not question:
            self._json({"error": "question is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        top_k = max(1, min(top_k, 15))
        model = _resolve_model(engine, requested_model, self.config)

        hits = search_chunks(
            db_path=self.config.db_path,
            query=question,
            materia=materia,
            limit=top_k,
        )
        hits = rank_hits(question, hits)
        if not hits:
            self._json(
                {"error": "no relevant context found. index the materia or adjust the query"},
                status=HTTPStatus.NOT_FOUND,
            )
            return

        sources = [
            {
                "id": f"S{i}",
                "file": str(Path(hit.path).name),
                "path": hit.path,
                "chunk": hit.chunk_idx,
                "score": hit.score,
                "excerpt": hit.text[:600],
            }
            for i, hit in enumerate(hits, start=1)
        ]

        context_block = _build_context(hits)
        try:
            if engine == "ollama":
                llm = generate_answer(
                    host=self.config.ollama_host,
                    model=model,
                    user_question=question,
                    context_block=context_block,
                    timeout_sec=timeout_sec,
                )
            elif engine == "openai":
                llm = generate_openai_answer(
                    api_key=self.config.openai_api_key,
                    model=model,
                    user_question=question,
                    context_block=context_block,
                    timeout_sec=timeout_sec,
                    base_url=self.config.openai_base_url,
                )
            elif engine == "gemini":
                llm = generate_gemini_answer(
                    api_key=self.config.gemini_api_key,
                    model=model,
                    user_question=question,
                    context_block=context_block,
                    timeout_sec=timeout_sec,
                    base_url=self.config.gemini_base_url,
                )
            else:
                self._json({"error": f"engine not supported: {engine}"}, status=HTTPStatus.BAD_REQUEST)
                return
        except (OllamaError, CloudLLMError) as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.SERVICE_UNAVAILABLE)
            return

        self._json(
            {
                "engine": engine,
                "answer": llm.content,
                "model": llm.model,
                "materia": materia,
                "sources": sources,
            }
        )

    def _handle_index(self) -> None:
        raw_size = self.headers.get("Content-Length", "0")
        try:
            content_length = int(raw_size)
        except ValueError:
            self._json({"error": "invalid content-length"}, status=HTTPStatus.BAD_REQUEST)
            return
        if content_length <= 0 or content_length > 500_000:
            self._json({"error": "invalid request body size"}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            self._json({"error": "invalid json body"}, status=HTTPStatus.BAD_REQUEST)
            return

        materia_raw = payload.get("materia")
        materia = str(materia_raw).strip() if materia_raw else ""

        materias: list[str]
        if materia:
            materias = [materia]
        else:
            materias = _list_fs_materias(self.config.root_path)
            if not materias:
                self._json({"error": "no materias found in root path"}, status=HTTPStatus.NOT_FOUND)
                return

        summaries: list[dict] = []
        for name in materias:
            try:
                stats = index_materia(
                    db_path=self.config.db_path,
                    facultad_root=self.config.root_path,
                    materia=name,
                )
            except FileNotFoundError:
                summaries.append(
                    {
                        "materia": name,
                        "ok": False,
                        "error": "materia not found",
                    }
                )
                continue
            except Exception as exc:
                summaries.append(
                    {
                        "materia": name,
                        "ok": False,
                        "error": str(exc),
                    }
                )
                continue

            summaries.append(
                {
                    "materia": name,
                    "ok": True,
                    "stats": {
                        "scanned": stats.scanned,
                        "updated": stats.updated,
                        "skipped_unchanged": stats.skipped_unchanged,
                        "skipped_unsupported": stats.skipped_unsupported,
                        "skipped_empty": stats.skipped_empty,
                        "warnings": stats.warnings,
                    },
                }
            )

        self._json({"results": summaries})

    def _handle_admin_status(self) -> None:
        try:
            text_stats = fts_stats(self.config.db_path)
            text_error = None
        except Exception as exc:
            text_stats = {"documents": 0, "chunks": 0, "materias": 0}
            text_error = str(exc)

        try:
            sem_stats = semantic_stats(self.config.semantic_db_path)
            semantic_error = None
        except Exception as exc:
            sem_stats = {"documents": 0, "fragments": 0, "embeddings": 0, "areas": 0}
            semantic_error = str(exc)

        self._json(
            {
                "root_path": str(self.config.root_path),
                "db_path": str(self.config.db_path),
                "semantic_db_path": str(self.config.semantic_db_path),
                "semantic_model": self.config.semantic_model,
                "fts": text_stats,
                "fts_error": text_error,
                "semantic": sem_stats,
                "semantic_error": semantic_error,
            }
        )

    def _read_json_body(self, max_size: int = 500_000) -> tuple[dict | None, str | None]:
        raw_size = self.headers.get("Content-Length", "0")
        try:
            content_length = int(raw_size)
        except ValueError:
            return None, "invalid content-length"
        if content_length <= 0 or content_length > max_size:
            return None, "invalid request body size"
        try:
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return None, "invalid json body"
        if not isinstance(payload, dict):
            return None, "json body must be an object"
        return payload, None

    def _semantic_embedder(self, allow_model_download: bool = False) -> SentenceTransformerEmbedder:
        return SentenceTransformerEmbedder(
            self.config.semantic_model,
            local_files_only=not allow_model_download,
        )

    def _handle_admin_semantic_index(self) -> None:
        payload, error = self._read_json_body()
        if error:
            self._json({"error": error}, status=HTTPStatus.BAD_REQUEST)
            return
        assert payload is not None
        materia = str(payload.get("materia") or "Ind Extractivas").strip()
        limit_files = int(payload.get("limit_files") or 10)
        limit_files = max(1, min(limit_files, 50))
        allow_download = bool(payload.get("allow_model_download", False))

        try:
            embedder = self._semantic_embedder(allow_download)
            stats = index_semantic_pilot(
                db_path=self.config.semantic_db_path,
                root=self.config.root_path,
                area=materia,
                embedder=embedder,
                limit_files=limit_files,
            )
        except Exception as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.SERVICE_UNAVAILABLE)
            return

        self._json(
            {
                "materia": materia,
                "stats": {
                    "scanned": stats.scanned,
                    "updated": stats.updated,
                    "skipped_unchanged": stats.skipped_unchanged,
                    "fragments": stats.fragments,
                    "embeddings_created": stats.embeddings_created,
                    "embeddings_reused": stats.embeddings_reused,
                    "warnings": stats.warnings,
                },
            }
        )

    def _handle_admin_semantic_search(self) -> None:
        payload, error = self._read_json_body()
        if error:
            self._json({"error": error}, status=HTTPStatus.BAD_REQUEST)
            return
        assert payload is not None
        query = str(payload.get("query") or "").strip()
        materia_raw = payload.get("materia")
        materia = str(materia_raw).strip() if materia_raw else None
        top_k = int(payload.get("top_k") or 10)
        top_k = max(1, min(top_k, 25))
        if not query:
            self._json({"error": "query is required"}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            embedder = self._semantic_embedder(False)
            hits = search_semantic(
                db_path=self.config.semantic_db_path,
                query=query,
                embedder=embedder,
                area=materia,
                limit=top_k,
            )
        except Exception as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.SERVICE_UNAVAILABLE)
            return

        self._json(
            {
                "query": query,
                "results": [
                    {
                        "score": hit.score,
                        "file": Path(hit.path).name,
                        "path": hit.path,
                        "title": hit.title,
                        "document_type": hit.document_type,
                        "page_start": hit.page_start,
                        "page_end": hit.page_end,
                        "chunk_index": hit.chunk_index,
                        "excerpt": hit.text[:700],
                    }
                    for hit in hits
                ],
            }
        )


def run_server(
    host: str,
    port: int,
    root_path: Path,
    db_path: Path,
    semantic_db_path: Path,
    semantic_model: str,
    ollama_host: str,
    openai_api_key: str,
    gemini_api_key: str,
    openai_base_url: str,
    gemini_base_url: str,
    model: str,
    timeout_sec: int,
    top_k: int,
) -> None:
    resolved_openai_key = _resolve_api_key(openai_api_key, ["OPENAI_API_KEY"])
    resolved_gemini_key = _resolve_api_key(
        gemini_api_key,
        ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY"],
    )
    config = AppConfig(
        root_path=root_path.expanduser(),
        db_path=db_path.expanduser(),
        semantic_db_path=semantic_db_path.expanduser(),
        semantic_model=semantic_model,
        ollama_host=ollama_host,
        openai_api_key=resolved_openai_key,
        gemini_api_key=resolved_gemini_key,
        openai_base_url=openai_base_url,
        gemini_base_url=gemini_base_url,
        default_ollama_model=model,
        default_openai_model="gpt-4.1-mini",
        default_gemini_model="gemini-2.5-flash",
        timeout_sec=timeout_sec,
        top_k=top_k,
    )
    handler_cls = type("ConfiguredStudyHandler", (StudyHandler,), {"config": config})
    server = ThreadingHTTPServer((host, port), handler_cls)
    print(f"Serving UI on http://{host}:{port}")
    print(f"Root: {config.root_path}")
    print(f"DB: {config.db_path}")
    print(f"Semantic DB: {config.semantic_db_path}")
    print(f"Semantic model: {config.semantic_model}")
    print(f"Ollama model (default): {config.default_ollama_model}")
    print(f"OpenAI model (default): {config.default_openai_model}")
    print(f"Gemini model (default): {config.default_gemini_model}")
    print(f"OpenAI key loaded: {'yes' if bool(config.openai_api_key) else 'no'}")
    print(f"Gemini key loaded: {'yes' if bool(config.gemini_api_key) else 'no'}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fiuba-local-web",
        description="Local web app for FIUBA study assistant",
    )
    parser.add_argument("--host", default="127.0.0.1", help="server host")
    parser.add_argument("--port", type=_positive_int, default=8787, help="server port")
    parser.add_argument("--root", type=Path, default=DEFAULT_FACULTAD_ROOT, help="facultad root path")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="sqlite db path")
    parser.add_argument("--semantic-db", type=Path, default=DEFAULT_SEMANTIC_DB_PATH, help="semantic sqlite db path")
    parser.add_argument("--semantic-model", default=DEFAULT_EMBEDDING_MODEL, help="semantic embedding model")
    parser.add_argument("--ollama-host", default="http://127.0.0.1:11434", help="ollama host")
    parser.add_argument("--openai-api-key", default=os.getenv("OPENAI_API_KEY", ""), help="OpenAI API key")
    parser.add_argument("--gemini-api-key", default=os.getenv("GEMINI_API_KEY", ""), help="Gemini API key")
    parser.add_argument("--openai-base-url", default="https://api.openai.com/v1", help="OpenAI base URL")
    parser.add_argument(
        "--gemini-base-url",
        default="https://generativelanguage.googleapis.com/v1beta",
        help="Gemini base URL",
    )
    parser.add_argument("--model", default="qwen2.5:3b-instruct", help="default model")
    parser.add_argument("--timeout-sec", type=_positive_int, default=300, help="ollama timeout")
    parser.add_argument("--top-k", type=_positive_int, default=6, help="default retrieval top-k")
    return parser


def main() -> int:
    load_env_file(Path.cwd() / ".env")
    args = build_parser().parse_args()
    run_server(
        host=args.host,
        port=args.port,
        root_path=args.root,
        db_path=args.db,
        semantic_db_path=args.semantic_db,
        semantic_model=args.semantic_model,
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


if __name__ == "__main__":
    raise SystemExit(main())
