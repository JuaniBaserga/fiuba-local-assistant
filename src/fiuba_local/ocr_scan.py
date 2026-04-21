from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path

from .extract import extract_text


@dataclass
class OCRScanResult:
    path: Path
    pages: int | None
    total_chars: int
    avg_chars_per_page: float | None
    warning: str | None
    needs_ocr: bool
    reason: str


def _iter_pdf_files(scope: Path) -> list[Path]:
    return sorted(path for path in scope.rglob("*.pdf") if path.is_file())


def _pdf_page_count(file_path: Path) -> int | None:
    PdfReader = None
    if importlib.util.find_spec("pypdf") is not None:
        try:
            from pypdf import PdfReader as _PdfReader  # type: ignore[import-not-found]

            PdfReader = _PdfReader
        except Exception:
            PdfReader = None
    if PdfReader is None and importlib.util.find_spec("PyPDF2") is not None:
        try:
            from PyPDF2 import PdfReader as _PdfReader  # type: ignore[import-not-found]

            PdfReader = _PdfReader
        except Exception:
            PdfReader = None
    if PdfReader is None:
        return None
    try:
        reader = PdfReader(str(file_path))
        return len(reader.pages)
    except Exception:
        return None


def _needs_ocr_reason(
    warning: str | None,
    total_chars: int,
    avg_chars_per_page: float | None,
    min_total_chars: int,
    min_chars_per_page: int,
) -> tuple[bool, str]:
    if warning:
        low = warning.lower()
        if "sin texto" in low or "no es texto util" in low:
            return True, "extractor reporta texto no util"
    if total_chars < min_total_chars:
        return True, f"muy poco texto extraido ({total_chars} chars)"
    if avg_chars_per_page is not None and avg_chars_per_page < min_chars_per_page:
        return True, f"muy poco texto por pagina ({avg_chars_per_page:.1f} chars/pag)"
    return False, "texto extraible aceptable"


def scan_ocr_candidates(
    scope: Path,
    min_total_chars: int = 120,
    min_chars_per_page: int = 60,
) -> list[OCRScanResult]:
    results: list[OCRScanResult] = []
    for pdf_path in _iter_pdf_files(scope):
        extraction = extract_text(pdf_path)
        text = extraction.text or ""
        total_chars = len(text.strip())
        pages = _pdf_page_count(pdf_path)
        avg_chars = (total_chars / pages) if pages and pages > 0 else None
        needs_ocr, reason = _needs_ocr_reason(
            warning=extraction.warning,
            total_chars=total_chars,
            avg_chars_per_page=avg_chars,
            min_total_chars=min_total_chars,
            min_chars_per_page=min_chars_per_page,
        )
        results.append(
            OCRScanResult(
                path=pdf_path,
                pages=pages,
                total_chars=total_chars,
                avg_chars_per_page=avg_chars,
                warning=extraction.warning,
                needs_ocr=needs_ocr,
                reason=reason,
            )
        )
    return results
