from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .config import ChunkConfig, SUPPORTED_EXTENSIONS
from .db import connect
from .extract import extract_text
from .textops import chunk_text, guess_materia


@dataclass
class IndexStats:
    scanned: int = 0
    updated: int = 0
    skipped_unchanged: int = 0
    skipped_unsupported: int = 0
    skipped_empty: int = 0
    warnings: int = 0


def _iter_files(materia_path: Path) -> Iterable[Path]:
    for path in materia_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_existing_doc(conn, path: str):
    return conn.execute(
        "SELECT id, sha256 FROM documents WHERE path = ?",
        (path,),
    ).fetchone()


def index_materia(
    db_path: Path,
    facultad_root: Path,
    materia: str,
    chunk_config: ChunkConfig | None = None,
) -> IndexStats:
    chunk_config = chunk_config or ChunkConfig()
    materia_path = facultad_root / materia
    if not materia_path.exists() or not materia_path.is_dir():
        raise FileNotFoundError(f"No existe la materia en: {materia_path}")

    stats = IndexStats()
    conn = connect(db_path)
    try:
        for file_path in _iter_files(materia_path):
            stats.scanned += 1
            ext = file_path.suffix.lower()
            file_bytes = file_path.read_bytes()
            file_hash = _sha256_bytes(file_bytes)
            row = _load_existing_doc(conn, str(file_path))
            if row and row["sha256"] == file_hash:
                stats.skipped_unchanged += 1
                continue

            extraction = extract_text(file_path)
            if extraction.warning:
                stats.warnings += 1
            chunks = chunk_text(extraction.text, chunk_config)
            if not chunks:
                if ext == ".pdf":
                    stats.skipped_unsupported += 1
                else:
                    stats.skipped_empty += 1
                continue

            materia_name = guess_materia(file_path, facultad_root)
            if row:
                doc_id = row["id"]
                conn.execute(
                    """
                    UPDATE documents
                    SET materia = ?, file_ext = ?, mtime = ?, file_size = ?, sha256 = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        materia_name,
                        ext,
                        file_path.stat().st_mtime,
                        len(file_bytes),
                        file_hash,
                        doc_id,
                    ),
                )
                conn.execute("DELETE FROM chunks_fts WHERE rowid IN (SELECT id FROM chunks WHERE doc_id = ?)", (doc_id,))
                conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
            else:
                cur = conn.execute(
                    """
                    INSERT INTO documents(path, materia, file_ext, mtime, file_size, sha256)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(file_path),
                        materia_name,
                        ext,
                        file_path.stat().st_mtime,
                        len(file_bytes),
                        file_hash,
                    ),
                )
                doc_id = int(cur.lastrowid)

            for chunk in chunks:
                cur = conn.execute(
                    "INSERT INTO chunks(doc_id, chunk_idx, text) VALUES (?, ?, ?)",
                    (doc_id, chunk.index, chunk.text),
                )
                chunk_rowid = int(cur.lastrowid)
                conn.execute(
                    "INSERT INTO chunks_fts(rowid, text) VALUES (?, ?)",
                    (chunk_rowid, chunk.text),
                )
            stats.updated += 1

        conn.commit()
        return stats
    finally:
        conn.close()
