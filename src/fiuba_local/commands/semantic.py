from __future__ import annotations

import argparse
from pathlib import Path

from ..semantic import SentenceTransformerEmbedder, index_semantic_pilot, search_semantic, semantic_stats


def _embedder(args: argparse.Namespace) -> SentenceTransformerEmbedder:
    return SentenceTransformerEmbedder(
        args.model,
        local_files_only=not bool(getattr(args, "allow_model_download", False)),
    )


def run_semantic_index(args: argparse.Namespace) -> int:
    try:
        stats = index_semantic_pilot(
            db_path=args.semantic_db.expanduser(),
            root=args.root.expanduser(),
            area=args.materia,
            embedder=_embedder(args),
            limit_files=args.limit_files,
        )
    except RuntimeError as exc:
        print(f"Error semantico: {exc}")
        return 1
    print("Indexacion semantica finalizada")
    print(f"- DB experimental: {args.semantic_db.expanduser()}")
    print(f"- Modelo: {args.model}")
    print(f"- Archivos escaneados: {stats.scanned}")
    print(f"- Archivos actualizados: {stats.updated}")
    print(f"- Sin cambios: {stats.skipped_unchanged}")
    print(f"- Fragmentos nuevos/reindexados: {stats.fragments}")
    print(f"- Embeddings creados: {stats.embeddings_created}")
    print(f"- Embeddings reutilizados: {stats.embeddings_reused}")
    print(f"- Advertencias: {stats.warnings}")
    return 0


def run_semantic_search(args: argparse.Namespace) -> int:
    try:
        hits = search_semantic(
            db_path=args.semantic_db.expanduser(),
            query=args.query,
            embedder=_embedder(args),
            area=args.materia,
            limit=args.top_k,
        )
    except RuntimeError as exc:
        print(f"Error semantico: {exc}")
        return 1
    if not hits:
        print("Sin resultados semanticos. Ejecuta `semantic index` primero.")
        return 0
    print(f"Vecinos semanticos para: {args.query!r}")
    if args.materia:
        print(f"Filtro materia: {args.materia}")
    for index, hit in enumerate(hits, start=1):
        preview = hit.text.replace("\n", " ")
        preview = preview[:260] + "..." if len(preview) > 260 else preview
        pages = str(hit.page_start) if hit.page_start == hit.page_end else f"{hit.page_start}-{hit.page_end}"
        print(f"\n[{index}] {Path(hit.path).name} p.{pages} ({hit.document_type}, score={hit.score:.3f})")
        print(f"Fuente: {hit.path}")
        print(preview)
    return 0


def run_semantic_stats(args: argparse.Namespace) -> int:
    stats = semantic_stats(args.semantic_db.expanduser())
    print("Estado del indice semantico experimental")
    print(f"- Areas: {stats['areas']}")
    print(f"- Documentos: {stats['documents']}")
    print(f"- Fragmentos: {stats['fragments']}")
    print(f"- Embeddings: {stats['embeddings']}")
    return 0
