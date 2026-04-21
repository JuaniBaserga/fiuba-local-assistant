from __future__ import annotations

import importlib.util
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExtractionResult:
    text: str
    method: str
    warning: str | None = None


def _extract_pdf_with_pypdf(file_path: Path) -> ExtractionResult | None:
    provider = None
    PdfReader = None
    if importlib.util.find_spec("pypdf") is not None:
        try:
            from pypdf import PdfReader as _PdfReader  # type: ignore[import-not-found]

            PdfReader = _PdfReader
            provider = "pypdf"
        except Exception:
            PdfReader = None
    if PdfReader is None and importlib.util.find_spec("PyPDF2") is not None:
        try:
            from PyPDF2 import PdfReader as _PdfReader  # type: ignore[import-not-found]

            PdfReader = _PdfReader
            provider = "PyPDF2"
        except Exception:
            PdfReader = None
    if PdfReader is None:
        return None

    try:
        reader = PdfReader(str(file_path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        text = "\n".join(pages).strip()
        if text:
            return ExtractionResult(text=text, method=provider or "pdf-reader")
        return ExtractionResult(
            text="",
            method=provider or "pdf-reader",
            warning="PDF sin texto extraible (posible escaneado).",
        )
    except Exception as exc:
        return ExtractionResult(
            text="",
            method=provider or "pdf-reader",
            warning=f"Error extrayendo PDF con lector local: {exc}",
        )


def _extract_pdf_with_textutil(file_path: Path) -> ExtractionResult | None:
    # Fallback de macOS. En muchos PDFs devuelve contenido binario en vez de texto.
    cmd = ["textutil", "-convert", "txt", "-stdout", str(file_path)]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return None
    if out.returncode != 0:
        return None
    text = (out.stdout or "").strip()
    if not text:
        return ExtractionResult(text="", method="textutil", warning="PDF sin salida de texto.")
    if text.startswith("%PDF-"):
        return ExtractionResult(
            text="",
            method="textutil",
            warning="textutil devolvio contenido PDF crudo; no es texto util.",
        )
    return ExtractionResult(text=text, method="textutil")


def extract_text(file_path: Path) -> ExtractionResult:
    suffix = file_path.suffix.lower()
    if suffix in {".md", ".txt"}:
        raw = file_path.read_text(encoding="utf-8", errors="ignore")
        return ExtractionResult(text=raw, method="plain")

    if suffix == ".pdf":
        pypdf_result = _extract_pdf_with_pypdf(file_path)
        if pypdf_result is not None:
            return pypdf_result
        textutil_result = _extract_pdf_with_textutil(file_path)
        if textutil_result is not None:
            return textutil_result
        return ExtractionResult(
            text="",
            method="none",
            warning="No hay extractor PDF disponible. Instala pypdf para habilitarlo.",
        )

    return ExtractionResult(
        text="",
        method="none",
        warning=f"Extension no soportada: {file_path.suffix}",
    )
