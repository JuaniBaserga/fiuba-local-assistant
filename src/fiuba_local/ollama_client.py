from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class OllamaResponse:
    content: str
    model: str


class OllamaError(RuntimeError):
    pass


def generate_answer(
    host: str,
    model: str,
    user_question: str,
    context_block: str,
    timeout_sec: int = 300,
) -> OllamaResponse:
    url = host.rstrip("/") + "/api/chat"
    system_prompt = (
        "Sos un tutor de FIUBA para estudiar con apuntes locales. "
        "Responde en espanol claro, tecnico y orientado a resolver parciales. "
        "Usa SOLO el contexto provisto; no completes con memoria externa. "
        "Si el contexto no alcanza, decilo al principio y responde solo lo sustentado. "
        "Cita afirmaciones importantes con [S1], [S2], etc. "
        "Formato obligatorio:\n"
        "1) Respuesta corta: 2 a 4 lineas directas.\n"
        "2) Desarrollo: explicacion ordenada, con formulas o pasos si aplican.\n"
        "3) Como usarlo en un ejercicio/parcial: procedimiento o checklist.\n"
        "4) Fuentes usadas: lista breve de etiquetas citadas.\n"
        "5) Confianza: alta/media/baja y motivo."
    )
    user_prompt = (
        f"Pregunta:\n{user_question}\n\n"
        f"Contexto recuperado:\n{context_block}\n\n"
        "Responde siguiendo el formato."
    )

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {"temperature": 0.1},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise OllamaError(
            f"No se pudo conectar a Ollama en {url}. "
            "Asegurate de ejecutar `ollama serve`."
        ) from exc
    except TimeoutError as exc:
        raise OllamaError("Timeout consultando Ollama.") from exc

    try:
        parsed = json.loads(raw)
        content = parsed["message"]["content"]
        model_used = parsed.get("model", model)
    except Exception as exc:
        raise OllamaError(f"Respuesta invalida de Ollama: {raw[:300]}") from exc

    return OllamaResponse(content=content.strip(), model=model_used)
