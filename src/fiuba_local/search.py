from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .db import connect


TOKEN_RE = re.compile(r"[A-Za-z0-9_áéíóúüñÁÉÍÓÚÜÑ]{2,}")


@dataclass
class SearchHit:
    score: float
    path: str
    chunk_idx: int
    text: str


def rank_hits(query: str, hits: list[SearchHit]) -> list[SearchHit]:
    query_tokens = {tok.lower() for tok in TOKEN_RE.findall(query)}
    if not query_tokens:
        return hits

    def score(hit: SearchHit) -> tuple[float, float]:
        hit_tokens = {tok.lower() for tok in TOKEN_RE.findall(hit.text)}
        overlap = len(query_tokens & hit_tokens)
        # bm25 en FTS5 suele ser menor (mas negativo = mejor). Invertimos signo.
        bm25_component = -hit.score
        return (float(overlap), float(bm25_component))

    return sorted(hits, key=score, reverse=True)


def _to_fts_query(query: str) -> str:
    tokens = TOKEN_RE.findall(query)
    if not tokens:
        return query
    return " OR ".join(f"{tok}*" for tok in tokens[:12])


def search_chunks(
    db_path: Path,
    query: str,
    materia: str | None = None,
    limit: int = 5,
) -> list[SearchHit]:
    conn = connect(db_path)
    try:
        fts_query = _to_fts_query(query)
        sql = """
        SELECT
          bm25(chunks_fts) AS score,
          d.path AS path,
          c.chunk_idx AS chunk_idx,
          c.text AS text
        FROM chunks_fts
        JOIN chunks c ON c.id = chunks_fts.rowid
        JOIN documents d ON d.id = c.doc_id
        WHERE chunks_fts MATCH ?
        """
        params: list[object] = [fts_query]
        if materia:
            sql += " AND d.materia = ?"
            params.append(materia)
        sql += " ORDER BY score LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        return [
            SearchHit(
                score=float(row["score"]),
                path=str(row["path"]),
                chunk_idx=int(row["chunk_idx"]),
                text=str(row["text"]),
            )
            for row in rows
        ]
    finally:
        conn.close()


def stats(db_path: Path) -> dict[str, int]:
    conn = connect(db_path)
    try:
        docs = conn.execute("SELECT COUNT(*) AS n FROM documents").fetchone()["n"]
        chunks = conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()["n"]
        materias = conn.execute("SELECT COUNT(DISTINCT materia) AS n FROM documents").fetchone()["n"]
        return {"documents": int(docs), "chunks": int(chunks), "materias": int(materias)}
    finally:
        conn.close()
