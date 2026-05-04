# Status Snapshot

## Last update
- Date: `2026-05-04`
- Scope: `fiuba-local-assistant` (respuesta con fuentes + localhost UI)

## Current state
- Product focus: responder preguntas con fuentes usando apuntes locales.
- Local retrieval stack works: SQLite + FTS5 + incremental index.
- Localhost UI is simplified to one main workflow: `Preguntar`.
- Multi-engine answering is available:
1. `Gemini API`
2. `OpenAI API`
3. `Ollama`
- Materias come from filesystem and show indexed status.

## What works today
1. Indexar una materia desde CLI o UI.
2. Preguntar desde UI con lista de fuentes y extractos.
3. Usar `.env` para API keys.
4. Refrescar materias y ver `indexada` / `sin indexar`.
5. Detectar candidatos OCR desde CLI con `ocr-check` si hace falta diagnostico tecnico.

## Current gaps
1. Source citations are file/chunk level, not page-level.
2. Ranking is basic and needs evaluation with real questions.
3. OCR is CLI-only diagnostic, not a productized UI flow.
4. `study` planner/calendar exists as experimental/future surface, not current product focus.

## Top 3 next steps
1. Build/evaluate a real question set per materia.
2. Improve retrieval/rerank and no-context behavior.
3. Add page-aware citations in extraction/index.

## Future PRDs
Out-of-focus or later-stage ideas live in:

- `docs/PRD_FUTURE.md`

Includes:
1. OCR assisted flow.
2. Debate mode.
3. Summary mode.
4. Study planner/calendar.
5. Google Calendar sync.
6. Google Drive ingestion.
7. Advanced admin UI.

## Retake commands
```bash
cd /Users/juanibaserga/dev/fiuba-local-assistant
.venv/bin/python -m fiuba_local.cli \
  --root /Users/juanibaserga/dev/Facultad \
  --db /Users/juanibaserga/dev/.fiuba_local/index.db \
  serve --host 127.0.0.1 --port 8787
```

Open:
```text
http://127.0.0.1:8787
```

Quick checks:
```bash
.venv/bin/python -m fiuba_local.cli \
  --root /Users/juanibaserga/dev/Facultad \
  --db /Users/juanibaserga/dev/.fiuba_local/index.db \
  stats
```

## Related docs
- `docs/PRD.md`
- `docs/PRD_FUTURE.md`
- `docs/EVAL_SET.md`
