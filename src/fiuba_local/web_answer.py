from __future__ import annotations

import json
from http import HTTPStatus
from pathlib import Path

from .cloud_llm import CloudLLMError, generate_gemini_answer, generate_openai_answer
from .ollama_client import OllamaError, generate_answer
from .search import rank_hits, search_chunks


def _build_context(hits) -> str:
    return "\n\n".join(
        f"[S{index}] {Path(hit.path).name} (chunk {hit.chunk_idx})\n{hit.text}"
        for index, hit in enumerate(hits, start=1)
    )


def _resolve_model(engine: str, requested: str, config) -> str:
    model = requested.strip()
    if engine == "gemini" and (not model or ":" in model or model.startswith("gpt-")):
        return config.default_gemini_model
    if engine == "openai" and (not model or ":" in model or model.startswith("gemini-")):
        return config.default_openai_model
    if engine == "ollama" and not model:
        return config.default_ollama_model
    return model


class AnswerHandlersMixin:
    """HTTP adapter for retrieval-augmented answers."""

    def _handle_answer(self) -> None:
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
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except Exception:
            self._json({"error": "invalid json body"}, status=HTTPStatus.BAD_REQUEST)
            return
        if not isinstance(payload, dict):
            self._json({"error": "json body must be an object"}, status=HTTPStatus.BAD_REQUEST)
            return

        question = str(payload.get("question", "")).strip()
        materia = str(payload["materia"]).strip() if payload.get("materia") else None
        engine = str(payload.get("engine", "gemini")).strip().lower()
        try:
            timeout_sec = int(payload.get("timeout_sec", self.config.timeout_sec))
            top_k = max(1, min(int(payload.get("top_k", self.config.top_k)), 15))
        except (TypeError, ValueError):
            self._json({"error": "timeout_sec y top_k deben ser enteros"}, status=HTTPStatus.BAD_REQUEST)
            return
        if timeout_sec <= 0:
            self._json({"error": "timeout_sec debe ser > 0"}, status=HTTPStatus.BAD_REQUEST)
            return
        if not question:
            self._json({"error": "question is required"}, status=HTTPStatus.BAD_REQUEST)
            return

        model = _resolve_model(engine, str(payload.get("model", "")), self.config)
        hits = rank_hits(
            question,
            search_chunks(self.config.db_path, question, materia=materia, limit=top_k),
        )
        if not hits:
            self._json(
                {"error": "no relevant context found. index the materia or adjust the query"},
                status=HTTPStatus.NOT_FOUND,
            )
            return
        context = _build_context(hits)
        try:
            if engine == "ollama":
                result = generate_answer(self.config.ollama_host, model, question, context, timeout_sec)
            elif engine == "openai":
                result = generate_openai_answer(
                    self.config.openai_api_key, model, question, context, timeout_sec, self.config.openai_base_url
                )
            elif engine == "gemini":
                result = generate_gemini_answer(
                    self.config.gemini_api_key, model, question, context, timeout_sec, self.config.gemini_base_url
                )
            else:
                self._json({"error": f"engine not supported: {engine}"}, status=HTTPStatus.BAD_REQUEST)
                return
        except (OllamaError, CloudLLMError) as exc:
            self._json({"error": str(exc)}, status=HTTPStatus.SERVICE_UNAVAILABLE)
            return
        sources = [
            {
                "id": f"S{index}",
                "file": Path(hit.path).name,
                "path": hit.path,
                "chunk": hit.chunk_idx,
                "score": hit.score,
                "excerpt": hit.text[:600],
            }
            for index, hit in enumerate(hits, start=1)
        ]
        self._json(
            {
                "engine": engine,
                "answer": result.content,
                "model": result.model,
                "materia": materia,
                "sources": sources,
            }
        )
