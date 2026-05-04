from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass
class CloudLLMResponse:
    content: str
    model: str


class CloudLLMError(RuntimeError):
    pass


def _system_prompt() -> str:
    return (
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


def generate_openai_answer(
    api_key: str,
    model: str,
    user_question: str,
    context_block: str,
    timeout_sec: int = 120,
    base_url: str = "https://api.openai.com/v1",
) -> CloudLLMResponse:
    if not api_key:
        raise CloudLLMError("OPENAI_API_KEY no configurada.")
    url = base_url.rstrip("/") + "/chat/completions"
    user_prompt = (
        f"Pregunta:\n{user_question}\n\n"
        f"Contexto recuperado:\n{context_block}\n\n"
        "Responde siguiendo el formato."
    )
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise CloudLLMError(f"OpenAI HTTP {exc.code}: {detail[:400]}") from exc
    except urllib.error.URLError as exc:
        raise CloudLLMError(f"No se pudo conectar a OpenAI: {exc}") from exc

    try:
        parsed = json.loads(raw)
        choice = parsed["choices"][0]["message"]["content"]
        if isinstance(choice, str):
            content = choice
        else:
            content = str(choice)
        model_used = parsed.get("model", model)
    except Exception as exc:
        raise CloudLLMError(f"Respuesta invalida de OpenAI: {raw[:400]}") from exc

    return CloudLLMResponse(content=content.strip(), model=model_used)


def generate_gemini_answer(
    api_key: str,
    model: str,
    user_question: str,
    context_block: str,
    timeout_sec: int = 120,
    base_url: str = "https://generativelanguage.googleapis.com/v1beta",
) -> CloudLLMResponse:
    if not api_key:
        raise CloudLLMError(
            "Gemini API key no configurada. Usa GEMINI_API_KEY (o GOOGLE_API_KEY)."
        )
    encoded_key = urllib.parse.quote(api_key, safe="")
    url = f"{base_url.rstrip('/')}/models/{model}:generateContent?key={encoded_key}"
    user_prompt = (
        f"Pregunta:\n{user_question}\n\n"
        f"Contexto recuperado:\n{context_block}\n\n"
        "Responde siguiendo el formato."
    )
    payload = {
        "systemInstruction": {"parts": [{"text": _system_prompt()}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": 0.1},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise CloudLLMError(f"Gemini HTTP {exc.code}: {detail[:400]}") from exc
    except urllib.error.URLError as exc:
        raise CloudLLMError(f"No se pudo conectar a Gemini: {exc}") from exc

    try:
        parsed = json.loads(raw)
        candidates = parsed.get("candidates", [])
        first = candidates[0]
        parts = first.get("content", {}).get("parts", [])
        content = "".join(part.get("text", "") for part in parts).strip()
        if not content:
            raise ValueError("empty content")
    except Exception as exc:
        raise CloudLLMError(f"Respuesta invalida de Gemini: {raw[:400]}") from exc

    return CloudLLMResponse(content=content, model=model)
