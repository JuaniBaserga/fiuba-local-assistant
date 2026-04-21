from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY,
  path TEXT UNIQUE NOT NULL,
  materia TEXT NOT NULL,
  file_ext TEXT NOT NULL,
  mtime REAL NOT NULL,
  file_size INTEGER NOT NULL,
  sha256 TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chunks (
  id INTEGER PRIMARY KEY,
  doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_idx INTEGER NOT NULL,
  text TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_chunks_doc_chunk_idx
ON chunks(doc_id, chunk_idx);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
USING fts5(text, content='chunks', content_rowid='id');

CREATE INDEX IF NOT EXISTS idx_documents_materia ON documents(materia);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA)
    return conn
