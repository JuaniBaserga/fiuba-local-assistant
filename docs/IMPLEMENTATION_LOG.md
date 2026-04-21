# Implementation Log

## 2026-04-18

### Core architecture
1. Consolidated chat-first direction in PRD/PLAN.
2. Kept local index/retrieval as infrastructure layer.

### Localhost app
1. Added web server module with API endpoints and static UI.
2. Added `serve` command to launch UI in localhost.
3. Added multi-engine support in UI:
- Codex prompt mode
- OpenAI API
- Gemini API
- Ollama local

### API keys and env
1. Added `.env` loader without extra dependencies.
2. Added `.env.example` and `.gitignore` for secret hygiene.
3. Added fallback for Gemini key aliases (`GEMINI_API_KEY`, `GOOGLE_API_KEY`).

### OCR workflow
1. Added OCR candidate scanner module (`ocr_scan.py`).
2. Added CLI command `ocr-check`.
3. Added UI tab `OCR Check` and backend endpoint `/api/ocr/check`.
4. Added suggested `ocrmypdf` command per candidate file.

### Materia visibility
1. Changed `/api/materias` to return:
- available materias from filesystem
- indexed materias from DB
- per-item indexed status
2. Updated UI to show:
- detected count
- indexed count
- materia list with status

### Current limitations
1. Source attribution still file/chunk based (page-level pending).
2. OCR execution is not one-click yet (detection + suggestion only).
3. Debate flow is available in protocol/docs but not fully productized in UI.
