from __future__ import annotations

import argparse

from ..ocr_scan import scan_ocr_candidates
from ..webapp import run_server


def run_serve(args: argparse.Namespace) -> int:
    run_server(
        host=args.host,
        port=args.port,
        root_path=args.root.expanduser(),
        db_path=args.db.expanduser(),
        semantic_db_path=args.semantic_db.expanduser(),
        semantic_model=args.semantic_model,
        study_dates_path=args.study_dates.expanduser(),
        study_state_path=args.study_state.expanduser(),
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


def run_ocr_check(args: argparse.Namespace) -> int:
    root = args.root.expanduser()
    scope = root / args.materia if args.materia else root
    if not scope.exists() or not scope.is_dir():
        print(f"No existe la {'materia' if args.materia else 'raiz'}: {scope}")
        return 1
    if args.limit < 0:
        print("--limit no puede ser negativo.")
        return 1
    results = scan_ocr_candidates(scope, args.min_total_chars, args.min_chars_per_page)
    if args.only_needs_ocr:
        results = [result for result in results if result.needs_ocr]
    if args.limit > 0:
        results = results[: args.limit]
    print(f"OCR scan scope: {scope}")
    print(f"- PDFs evaluados: {len(results)}")
    print(f"- Candidatos OCR: {sum(1 for result in results if result.needs_ocr)}")
    print(f"- Umbrales: total_chars<{args.min_total_chars}, chars/pag<{args.min_chars_per_page}")
    if not results:
        print("Sin PDFs para mostrar con esos filtros.")
        return 0
    print("\nResultados:")
    for item in results:
        status = "OCR" if item.needs_ocr else "OK"
        pages = str(item.pages) if item.pages is not None else "?"
        average = f"{item.avg_chars_per_page:.1f}" if item.avg_chars_per_page is not None else "?"
        print(f"- [{status}] {item.path}")
        print(f"  pages={pages} chars={item.total_chars} avg_chars_per_page={average}")
        print(f"  razon={item.reason}")
        if item.warning:
            print(f"  warning={item.warning}")
        if item.needs_ocr:
            output = item.path.with_name(item.path.stem + ".ocr.pdf")
            print(f"  sugerencia: ocrmypdf --skip-text '{item.path}' '{output}'")
    return 0
