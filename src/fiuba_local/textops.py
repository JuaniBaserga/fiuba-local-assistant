from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .config import ChunkConfig


WHITESPACE_RE = re.compile(r"\s+")


@dataclass
class Chunk:
    index: int
    text: str


def normalize_text(raw: str) -> str:
    text = raw.replace("\x00", " ")
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def chunk_text(raw: str, config: ChunkConfig) -> list[Chunk]:
    text = normalize_text(raw)
    if not text:
        return []
    if len(text) <= config.max_chars:
        return [Chunk(index=0, text=text)]

    chunks: list[Chunk] = []
    start = 0
    idx = 0
    n = len(text)
    while start < n:
        end = min(start + config.max_chars, n)
        if end < n:
            pivot = text.rfind(" ", start, end)
            if pivot > start + 200:
                end = pivot
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(Chunk(index=idx, text=chunk))
            idx += 1
        if end >= n:
            break
        start = max(end - config.overlap_chars, start + 1)
    return chunks


def guess_materia(file_path: Path, facultad_root: Path) -> str:
    rel = file_path.relative_to(facultad_root)
    return rel.parts[0] if rel.parts else "desconocida"
