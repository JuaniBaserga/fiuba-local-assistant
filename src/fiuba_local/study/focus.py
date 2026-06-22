from __future__ import annotations

from .types import StudyEvent


def planning_phase(event_type: str, days_left: int) -> str:
    event_kind = event_type.strip().lower()
    if event_kind == "entrega":
        if days_left <= 4:
            return "cierre"
        if days_left <= 14:
            return "desarrollo"
        return "arranque"
    if days_left <= 7:
        return "cierre"
    if days_left <= 21:
        return "consolidacion"
    return "fundamentos"


def _default_focus_topic(event_type: str, phase: str) -> str:
    if event_type.strip().lower() == "entrega":
        if phase == "arranque":
            return "descomponer enunciado y definir plan de trabajo"
        if phase == "desarrollo":
            return "resolver bloque principal del trabajo practico"
        return "cierre, validacion y checklist de entrega"
    if phase == "fundamentos":
        return "fundamentos y mapa de conceptos"
    if phase == "consolidacion":
        return "ejercicios tipo parcial con correccion guiada"
    return "simulacro y repaso activo de errores"


def focus_topic(event: StudyEvent, sequence_for_materia: int, phase: str) -> str:
    if event.topics:
        topic = event.topics[sequence_for_materia % len(event.topics)]
        return f"Repaso activo: {topic}" if phase == "cierre" else topic
    return _default_focus_topic(event.event_type, phase)


def focus_reason(event: StudyEvent, days_left: int, phase: str, topic: str) -> str:
    reasons = {
        "fundamentos": "fase de base conceptual",
        "consolidacion": "fase de consolidacion con practica",
        "arranque": "fase de arranque para no acumular deuda",
        "desarrollo": "fase de desarrollo de contenido principal",
    }
    phase_reason = reasons.get(phase, "fase de cierre previa al objetivo")
    day_label = "dia" if days_left == 1 else "dias"
    return (
        f"Faltan {days_left} {day_label} para {event.event_type} '{event.title}'; "
        f"{phase_reason}, foco en: {topic}."
    )
