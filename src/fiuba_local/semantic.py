from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .config import ChunkConfig
from .extract import extract_text
from .textops import chunk_text, guess_materia, normalize_text


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

SEMANTIC_SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY,
  path TEXT UNIQUE NOT NULL,
  collection TEXT NOT NULL,
  area TEXT NOT NULL,
  document_type TEXT NOT NULL,
  title TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fragments (
  id INTEGER PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  page_start INTEGER NOT NULL,
  page_end INTEGER NOT NULL,
  text TEXT NOT NULL,
  text_hash TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_fragments_doc_chunk_idx
ON fragments(document_id, chunk_index);

CREATE INDEX IF NOT EXISTS idx_fragments_text_hash
ON fragments(text_hash);

CREATE TABLE IF NOT EXISTS embeddings (
  fragment_id INTEGER NOT NULL REFERENCES fragments(id) ON DELETE CASCADE,
  model_id TEXT NOT NULL,
  dimensions INTEGER NOT NULL,
  vector_json TEXT NOT NULL,
  text_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(fragment_id, model_id)
);

CREATE INDEX IF NOT EXISTS idx_embeddings_model
ON embeddings(model_id);
"""


class Embedder(Protocol):
    model_id: str

    def encode(self, texts: list[str]) -> list[list[float]]:
        ...


@dataclass
class SemanticIndexStats:
    scanned: int = 0
    updated: int = 0
    skipped_unchanged: int = 0
    fragments: int = 0
    embeddings_created: int = 0
    embeddings_reused: int = 0
    warnings: int = 0


@dataclass
class SemanticHit:
    score: float
    path: str
    title: str
    document_type: str
    page_start: int
    page_end: int
    chunk_index: int
    text: str


class SentenceTransformerEmbedder:
    def __init__(self, model_id: str, *, local_files_only: bool = True) -> None:
        if importlib.util.find_spec("sentence_transformers") is None:
            raise RuntimeError(
                "Falta sentence-transformers. Instala el extra semantico: "
                "`pip install -e '.[semantic]'`."
            )

        from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]

        kwargs = {}
        try:
            params = inspect.signature(SentenceTransformer).parameters
            if "local_files_only" in params:
                kwargs["local_files_only"] = local_files_only
        except (TypeError, ValueError):
            pass

        try:
            self._model = SentenceTransformer(model_id, **kwargs)
        except Exception as exc:
            if local_files_only:
                raise RuntimeError(
                    f"No pude cargar el modelo local/cacheado {model_id!r}. "
                    "Descargalo previamente o usa `--allow-model-download`."
                ) from exc
            raise
        self.model_id = model_id

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [[float(value) for value in vector] for vector in vectors]


def connect_semantic(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SEMANTIC_SCHEMA)
    return conn


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _iter_pilot_files(root: Path, area: str, limit: int = 10) -> list[Path]:
    area_path = root / area
    if not area_path.exists() or not area_path.is_dir():
        raise FileNotFoundError(f"No existe la materia en: {area_path}")
    files = sorted(
        path
        for path in area_path.rglob("*")
        if path.is_file() and path.suffix.lower() in {".pdf", ".txt", ".md"}
    )
    return files[:limit] if limit > 0 else files


def infer_document_type(path: Path) -> str:
    lower = " ".join(part.lower() for part in path.parts)
    name = path.name.lower()
    if "parcial" in lower or "final" in lower or "pregunta" in lower:
        return "exam"
    if "practica" in lower or "práctica" in lower or "guia" in lower or "guía" in lower:
        return "practice"
    if "resumen" in lower or "apunte" in name:
        return "summary"
    return "theory"


def _extract_pdf_pages(file_path: Path) -> tuple[list[str], str | None]:
    if importlib.util.find_spec("pypdf") is None:
        extraction = extract_text(file_path)
        return ([extraction.text] if extraction.text.strip() else []), extraction.warning

    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]

        reader = PdfReader(str(file_path))
        pages = [normalize_text(page.extract_text() or "") for page in reader.pages]
        return pages, None
    except Exception as exc:
        extraction = extract_text(file_path)
        warning = f"Error extrayendo PDF por pagina: {exc}"
        if extraction.warning:
            warning = f"{warning}; fallback: {extraction.warning}"
        return ([extraction.text] if extraction.text.strip() else []), warning


def _fragments_for_file(file_path: Path, chunk_config: ChunkConfig) -> list[tuple[int, int, int, str, str]]:
    if file_path.suffix.lower() == ".pdf":
        pages, _ = _extract_pdf_pages(file_path)
    else:
        pages = [extract_text(file_path).text]

    fragments: list[tuple[int, int, int, str, str]] = []
    chunk_index = 0
    for page_number, page_text in enumerate(pages, start=1):
        for chunk in chunk_text(page_text, chunk_config):
            text_hash = _sha256_text(chunk.text)
            fragments.append((chunk_index, page_number, page_number, chunk.text, text_hash))
            chunk_index += 1
    return fragments


def _load_reusable_embeddings(conn: sqlite3.Connection, model_id: str) -> dict[str, tuple[int, str]]:
    rows = conn.execute(
        "SELECT text_hash, dimensions, vector_json FROM embeddings WHERE model_id = ?",
        (model_id,),
    ).fetchall()
    return {str(row["text_hash"]): (int(row["dimensions"]), str(row["vector_json"])) for row in rows}


def index_semantic_pilot(
    *,
    db_path: Path,
    root: Path,
    area: str,
    embedder: Embedder,
    limit_files: int = 10,
    chunk_config: ChunkConfig | None = None,
) -> SemanticIndexStats:
    chunk_config = chunk_config or ChunkConfig(max_chars=900, overlap_chars=120)
    stats = SemanticIndexStats()
    conn = connect_semantic(db_path)
    reusable = _load_reusable_embeddings(conn, embedder.model_id)
    try:
        for file_path in _iter_pilot_files(root, area, limit_files):
            stats.scanned += 1
            file_bytes = file_path.read_bytes()
            file_hash = _sha256_bytes(file_bytes)
            row = conn.execute("SELECT id, sha256 FROM documents WHERE path = ?", (str(file_path),)).fetchone()
            if row and row["sha256"] == file_hash:
                stats.skipped_unchanged += 1
                continue

            _pages, warning = _extract_pdf_pages(file_path) if file_path.suffix.lower() == ".pdf" else ([], None)
            if warning:
                stats.warnings += 1
            fragments = _fragments_for_file(file_path, chunk_config)
            if not fragments:
                stats.warnings += 1
                continue

            if row:
                doc_id = int(row["id"])
                conn.execute(
                    """
                    UPDATE documents
                    SET collection = ?, area = ?, document_type = ?, title = ?, sha256 = ?,
                        metadata_json = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        "facultad",
                        guess_materia(file_path, root),
                        infer_document_type(file_path),
                        file_path.stem,
                        file_hash,
                        json.dumps({"suffix": file_path.suffix.lower()}, ensure_ascii=False),
                        doc_id,
                    ),
                )
                conn.execute("DELETE FROM fragments WHERE document_id = ?", (doc_id,))
            else:
                cur = conn.execute(
                    """
                    INSERT INTO documents(collection, area, document_type, title, path, sha256, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "facultad",
                        guess_materia(file_path, root),
                        infer_document_type(file_path),
                        file_path.stem,
                        str(file_path),
                        file_hash,
                        json.dumps({"suffix": file_path.suffix.lower()}, ensure_ascii=False),
                    ),
                )
                doc_id = int(cur.lastrowid)

            pending: list[tuple[int, str, str]] = []
            for chunk_index, page_start, page_end, text, text_hash in fragments:
                cur = conn.execute(
                    """
                    INSERT INTO fragments(document_id, chunk_index, page_start, page_end, text, text_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (doc_id, chunk_index, page_start, page_end, text, text_hash),
                )
                fragment_id = int(cur.lastrowid)
                reused = reusable.get(text_hash)
                if reused:
                    dimensions, vector_json = reused
                    conn.execute(
                        """
                        INSERT INTO embeddings(fragment_id, model_id, dimensions, vector_json, text_hash)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (fragment_id, embedder.model_id, dimensions, vector_json, text_hash),
                    )
                    stats.embeddings_reused += 1
                else:
                    pending.append((fragment_id, text, text_hash))
                stats.fragments += 1

            if pending:
                vectors = embedder.encode([item[1] for item in pending])
                for (fragment_id, _text, text_hash), vector in zip(pending, vectors):
                    vector_json = json.dumps(vector, separators=(",", ":"))
                    conn.execute(
                        """
                        INSERT INTO embeddings(fragment_id, model_id, dimensions, vector_json, text_hash)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (fragment_id, embedder.model_id, len(vector), vector_json, text_hash),
                    )
                    reusable[text_hash] = (len(vector), vector_json)
                    stats.embeddings_created += 1

            stats.updated += 1

        conn.commit()
        return stats
    finally:
        conn.close()


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def search_semantic(
    *,
    db_path: Path,
    query: str,
    embedder: Embedder,
    area: str | None = None,
    limit: int = 10,
) -> list[SemanticHit]:
    query_vector = embedder.encode([query])[0]
    conn = connect_semantic(db_path)
    try:
        sql = """
        SELECT
          e.vector_json AS vector_json,
          d.path AS path,
          d.title AS title,
          d.document_type AS document_type,
          f.page_start AS page_start,
          f.page_end AS page_end,
          f.chunk_index AS chunk_index,
          f.text AS text
        FROM embeddings e
        JOIN fragments f ON f.id = e.fragment_id
        JOIN documents d ON d.id = f.document_id
        WHERE e.model_id = ?
        """
        params: list[object] = [embedder.model_id]
        if area:
            sql += " AND d.area = ?"
            params.append(area)

        hits: list[SemanticHit] = []
        for row in conn.execute(sql, params).fetchall():
            vector = [float(value) for value in json.loads(str(row["vector_json"]))]
            hits.append(
                SemanticHit(
                    score=_cosine(query_vector, vector),
                    path=str(row["path"]),
                    title=str(row["title"]),
                    document_type=str(row["document_type"]),
                    page_start=int(row["page_start"]),
                    page_end=int(row["page_end"]),
                    chunk_index=int(row["chunk_index"]),
                    text=str(row["text"]),
                )
            )
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]
    finally:
        conn.close()


def semantic_stats(db_path: Path) -> dict[str, int]:
    conn = connect_semantic(db_path)
    try:
        docs = conn.execute("SELECT COUNT(*) AS n FROM documents").fetchone()["n"]
        fragments = conn.execute("SELECT COUNT(*) AS n FROM fragments").fetchone()["n"]
        embeddings = conn.execute("SELECT COUNT(*) AS n FROM embeddings").fetchone()["n"]
        areas = conn.execute("SELECT COUNT(DISTINCT area) AS n FROM documents").fetchone()["n"]
        return {
            "documents": int(docs),
            "fragments": int(fragments),
            "embeddings": int(embeddings),
            "areas": int(areas),
        }
    finally:
        conn.close()
