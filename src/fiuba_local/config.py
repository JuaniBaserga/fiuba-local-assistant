from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_path(name: str, fallback: Path) -> Path:
    value = os.getenv(name, "").strip()
    if not value:
        return fallback
    return Path(value).expanduser()


DEFAULT_FACULTAD_ROOT = _env_path("FIUBA_ROOT", Path.home() / "dev" / "Facultad")
DEFAULT_STATE_DIR = _env_path("FIUBA_STATE_DIR", Path.home() / ".fiuba_local")
DEFAULT_DB_PATH = _env_path("FIUBA_DB_PATH", DEFAULT_STATE_DIR / "index.db")
DEFAULT_SEMANTIC_DB_PATH = _env_path("FIUBA_SEMANTIC_DB_PATH", DEFAULT_STATE_DIR / "semantic.db")

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


@dataclass(frozen=True)
class ChunkConfig:
    max_chars: int = 1200
    overlap_chars: int = 200
