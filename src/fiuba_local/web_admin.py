from __future__ import annotations

from http import HTTPStatus
from pathlib import Path

from .search import stats as fts_stats
from .semantic import SentenceTransformerEmbedder, index_semantic_pilot, search_semantic, semantic_stats


class AdminHandlersMixin:
    """HTTP adapter for index administration and semantic search."""

    def _handle_admin_status(self) -> None:
        try:
            text_stats, text_error = fts_stats(self.config.db_path), None
        except Exception as exc:
            text_stats, text_error = {"documents": 0, "chunks": 0, "materias": 0}, str(exc)
        try:
            semantic, semantic_error = semantic_stats(self.config.semantic_db_path), None
        except Exception as exc:
            semantic = {"documents": 0, "fragments": 0, "embeddings": 0, "areas": 0}
            semantic_error = str(exc)
        self._json(
            {
                "root_path": str(self.config.root_path),
                "db_path": str(self.config.db_path),
                "semantic_db_path": str(self.config.semantic_db_path),
                "semantic_model": self.config.semantic_model,
                "fts": text_stats,
                "fts_error": text_error,
                "semantic": semantic,
                "semantic_error": semantic_error,
            }
        )

    def _semantic_embedder(self, allow_model_download: bool = False) -> SentenceTransformerEmbedder:
        return SentenceTransformerEmbedder(self.config.semantic_model, local_files_only=not allow_model_download)

    def _handle_admin_semantic_index(self) -> None:
        payload, error = self._read_json_body()
        if error:
            self._json({"error": error}, status=HTTPStatus.BAD_REQUEST)
            return
        assert payload is not None
        materia = str(payload.get("materia") or "Ind Extractivas").strip()
        try:
            limit_files = max(1, min(int(payload.get("limit_files") or 10), 50))
        except (TypeError, ValueError):
            self._json({"error": "limit_files debe ser entero"}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            stats = index_semantic_pilot(
                db_path=self.config.semantic_db_path,
                root=self.config.root_path,
                area=materia,
                embedder=self._semantic_embedder(bool(payload.get("allow_model_download", False))),
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
        materia = str(payload["materia"]).strip() if payload.get("materia") else None
        try:
            top_k = max(1, min(int(payload.get("top_k") or 10), 25))
        except (TypeError, ValueError):
            self._json({"error": "top_k debe ser entero"}, status=HTTPStatus.BAD_REQUEST)
            return
        if not query:
            self._json({"error": "query is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        try:
            hits = search_semantic(
                db_path=self.config.semantic_db_path,
                query=query,
                embedder=self._semantic_embedder(False),
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
