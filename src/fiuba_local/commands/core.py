from __future__ import annotations

import argparse
from pathlib import Path

from ..indexer import index_materia
from ..ollama_client import OllamaError, generate_answer
from ..search import rank_hits, search_chunks, stats as get_stats


def run_index(args: argparse.Namespace) -> int:
    stats = index_materia(args.db.expanduser(), args.root.expanduser(), args.materia)
    print("Indexacion finalizada")
    print(f"- Archivos escaneados: {stats.scanned}")
    print(f"- Archivos actualizados: {stats.updated}")
    print(f"- Sin cambios: {stats.skipped_unchanged}")
    print(f"- Omitidos sin texto util: {stats.skipped_unsupported + stats.skipped_empty}")
    print(f"- Advertencias de extraccion: {stats.warnings}")
    return 0


def run_ask(args: argparse.Namespace) -> int:
    hits = search_chunks(args.db.expanduser(), args.query, args.materia, args.top_k)
    if not hits:
        print("Sin resultados. Proba otra consulta o indexa la materia primero.")
        return 0
    print(f"Resultados para: {args.query!r}")
    if args.materia:
        print(f"Filtro materia: {args.materia}")
    for index, hit in enumerate(hits, start=1):
        preview = hit.text.replace("\n", " ")
        preview = preview[:260] + "..." if len(preview) > 260 else preview
        print(f"\n[{index}] {Path(hit.path).name} (chunk {hit.chunk_idx}, score={hit.score:.3f})")
        print(f"Fuente: {hit.path}")
        print(preview)
    return 0


def run_answer(args: argparse.Namespace) -> int:
    hits = rank_hits(args.query, search_chunks(args.db.expanduser(), args.query, args.materia, args.top_k))
    if not hits:
        print("Sin resultados en el indice. Ejecuta `index` primero o ajusta la consulta.")
        return 0
    context = "\n\n".join(
        f"[S{index}] {Path(hit.path).name} (chunk {hit.chunk_idx})\n{hit.text}"
        for index, hit in enumerate(hits, start=1)
    )
    try:
        result = generate_answer(args.ollama_host, args.model, args.query, context, args.timeout_sec)
    except OllamaError as exc:
        print(f"Error Ollama: {exc}")
        print("Tip: instala y arranca Ollama, luego descarga un modelo.")
        print("  brew install ollama\n  ollama serve\n  ollama pull qwen2.5:7b-instruct")
        return 1
    print(f"Modelo: {result.model}")
    if args.materia:
        print(f"Materia: {args.materia}")
    print(f"\n{result.content}\n\nFuentes recuperadas:")
    for index, hit in enumerate(hits, start=1):
        print(f"[S{index}] {hit.path} (chunk {hit.chunk_idx})")
    return 0


def run_stats(args: argparse.Namespace) -> int:
    stats = get_stats(args.db.expanduser())
    print("Estado del indice")
    print(f"- Materias: {stats['materias']}")
    print(f"- Documentos: {stats['documents']}")
    print(f"- Chunks: {stats['chunks']}")
    return 0
