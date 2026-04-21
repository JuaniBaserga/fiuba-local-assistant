# Status Snapshot

## Last update
- Date: `2026-04-18`
- Scope: `fiuba-local-assistant` (chat-first + localhost UI)

## Current state
- Product direction is stable (`chat-first`).
- Local retrieval stack works (SQLite + FTS5 + incremental index).
- Localhost UI is running with tabs:
1. `Preguntar`
2. `OCR Check`
- Multi-engine answering is available:
1. `Codex prompt mode`
2. `OpenAI API`
3. `Gemini API`
4. `Ollama`
- Materias now come from filesystem and show indexed status.

## What works today
1. Index one materia from CLI.
2. Ask questions from UI with source list.
3. Use `.env` for API keys.
4. Detect OCR candidates from CLI and UI.
5. Refresh visible materia list and see `indexada` / `sin indexar`.

## Current gaps
1. Source citations are file/chunk level, not page-level.
2. OCR is detection + suggested command, not one-click execution.
3. Debate workflow exists in docs/protocol but is not fully UI-productized.
4. UI index action exists; bulk indexing policy and progress UX can improve.

## Top 3 next steps
1. Add page-aware citations in extraction/index.
2. Add one-click OCR execution flow (`ocrmypdf` integration) with safe confirmation.
3. Add dedicated `Debatir` tab and strict output template.

## Risks / blockers
1. PDF extraction quality varies by source type.
2. OCR tools may require local install and can be slow on large files.
3. API cost/latency depends on selected model provider.

## Retake commands
```bash
cd /Users/juanibaserga/dev/fiuba-local-assistant
PYTHONPATH=src python3 -m fiuba_local.cli serve --host 127.0.0.1 --port 8787
```

Open:
```text
http://127.0.0.1:8787
```

Quick checks:
```bash
PYTHONPATH=src python3 -m fiuba_local.cli stats
PYTHONPATH=src python3 -m fiuba_local.cli ocr-check --materia "Ind Extractivas" --only-needs-ocr
```

## Related docs
- `docs/PRD.md`
- `docs/PLAN.md`
- `docs/IMPLEMENTATION_LOG.md`
- `docs/SPRINT_A_CHECKLIST.md`
