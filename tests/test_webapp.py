from __future__ import annotations

import json
from datetime import date
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from fiuba_local import webapp
from fiuba_local.study.io import save_template_files


def _config(tmp_path: Path) -> webapp.AppConfig:
    return webapp.AppConfig(
        root_path=tmp_path,
        db_path=tmp_path / "index.db",
        semantic_db_path=tmp_path / "semantic.db",
        semantic_model="test-model",
        study_dates_path=tmp_path / "dates.json",
        study_state_path=tmp_path / "state.json",
        ollama_host="http://127.0.0.1:11434",
        openai_api_key="",
        gemini_api_key="",
        openai_base_url="https://api.openai.com/v1",
        gemini_base_url="https://generativelanguage.googleapis.com/v1beta",
        default_ollama_model="test",
        default_openai_model="test",
        default_gemini_model="test",
        timeout_sec=10,
        top_k=3,
    )


def _handler(tmp_path: Path, payload: object = None) -> webapp.StudyHandler:
    handler = object.__new__(webapp.StudyHandler)
    handler.config = _config(tmp_path)
    body = json.dumps(payload)
    handler.headers = {"Content-Length": str(len(body.encode("utf-8")))}
    handler.rfile = BytesIO(body.encode("utf-8"))
    handler._responses = []

    def capture(response_payload, status=webapp.HTTPStatus.OK):
        handler._responses.append((int(status), response_payload))

    handler._json = capture
    return handler


def test_study_plan_invalid_date_returns_400(tmp_path):
    handler = _handler(tmp_path, {"from_date": "no-es-fecha"})
    save_template_files(handler.config.study_dates_path, handler.config.study_state_path, date.today())
    handler._handle_study_plan()
    status, payload = handler._responses[-1]

    assert status == 400
    assert "invalidos" in payload["error"]


def test_study_status_rejects_malformed_session(tmp_path):
    handler = _handler(tmp_path)
    save_template_files(handler.config.study_dates_path, handler.config.study_state_path, date.today())
    state = json.loads(handler.config.study_state_path.read_text(encoding="utf-8"))
    state["planned_sessions"] = [{"id": "incompleta"}]
    handler.config.study_state_path.write_text(json.dumps(state), encoding="utf-8")
    handler._handle_study_status()
    status, payload = handler._responses[-1]

    assert status == 400
    assert "Sesion invalida" in payload["error"]


def test_load_demo_validates_and_copies_dates(tmp_path):
    demo = tmp_path / "demo.json"
    demo.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "materia": "Mecanismos",
                        "event_type": "parcial",
                        "title": "P1",
                        "date": "2026-07-01",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    handler = _handler(target_dir, {"path": str(demo)})
    handler._handle_study_load_demo()
    status, payload = handler._responses[-1]

    assert status == 200
    assert payload["dates_path"] == str(handler.config.study_dates_path)
    assert json.loads(handler.config.study_dates_path.read_text(encoding="utf-8"))["events"][0]["title"] == "P1"


def test_webapp_entrypoint_passes_study_paths():
    with patch.object(webapp, "run_server") as run:
        with patch("sys.argv", ["fiuba-local-web"]):
            assert webapp.main() == 0

    kwargs = run.call_args.kwargs
    assert kwargs["study_dates_path"] == webapp.DEFAULT_STUDY_DATES_PATH
    assert kwargs["study_state_path"] == webapp.DEFAULT_STUDY_STATE_PATH


def test_answer_rejects_non_object_json(tmp_path):
    handler = _handler(tmp_path, ["not", "an", "object"])
    handler._handle_answer()

    status, payload = handler._responses[-1]
    assert status == 400
    assert payload["error"] == "json body must be an object"
