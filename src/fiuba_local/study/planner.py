from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from math import floor

from .types import StudyEvent, StudySession


@dataclass(frozen=True)
class PlanOptions:
    from_date: date
    weekly_hours: float
    weeks: int
    session_minutes: int = 90
    max_daily_hours: float = 3.0
    day_start_hour: int = 19


def _event_score(event: StudyEvent, as_of: date) -> float:
    days_left = max((event.date - as_of).days, 1)
    urgency = 1.0 / days_left
    difficulty_factor = 0.6 + (0.2 * event.difficulty)
    return event.weight * difficulty_factor * urgency


def _allocate_minutes(score_by_materia: dict[str, float], total_minutes: int) -> dict[str, int]:
    if not score_by_materia or total_minutes <= 0:
        return {}

    total_score = sum(score_by_materia.values())
    if total_score <= 0:
        return {}

    raw_alloc: dict[str, float] = {
        materia: (score / total_score) * total_minutes
        for materia, score in score_by_materia.items()
    }
    allocated = {materia: floor(minutes) for materia, minutes in raw_alloc.items()}
    consumed = sum(allocated.values())
    remainder = total_minutes - consumed

    frac_order = sorted(
        raw_alloc.keys(),
        key=lambda materia: (raw_alloc[materia] - allocated[materia], score_by_materia[materia], materia),
        reverse=True,
    )
    idx = 0
    while remainder > 0 and frac_order:
        materia = frac_order[idx % len(frac_order)]
        allocated[materia] += 1
        remainder -= 1
        idx += 1
    return allocated


def _next_event_per_materia(events: list[StudyEvent], as_of: date) -> dict[str, StudyEvent]:
    out: dict[str, StudyEvent] = {}
    for event in sorted(events, key=lambda e: e.date):
        if event.date < as_of:
            continue
        if event.materia not in out:
            out[event.materia] = event
    return out


def _pick_day(day_load: list[int], session_minutes: int, max_daily_minutes: int) -> int:
    candidates = [
        day_idx
        for day_idx, current in enumerate(day_load)
        if current + session_minutes <= max_daily_minutes
    ]
    if candidates:
        return min(candidates, key=lambda idx: (day_load[idx], idx))
    return min(range(len(day_load)), key=lambda idx: (day_load[idx], idx))


def _planning_phase(event_type: str, days_left: int) -> str:
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
    event_kind = event_type.strip().lower()
    if event_kind == "entrega":
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


def _focus_topic(event: StudyEvent, sequence_for_materia: int, phase: str) -> str:
    if event.topics:
        topic = event.topics[sequence_for_materia % len(event.topics)]
        if phase == "cierre":
            return f"Repaso activo: {topic}"
        return topic
    return _default_focus_topic(event.event_type, phase)


def _focus_reason(event: StudyEvent, days_left: int, phase: str, focus_topic: str) -> str:
    day_label = "dia" if days_left == 1 else "dias"
    if phase == "fundamentos":
        phase_reason = "fase de base conceptual"
    elif phase == "consolidacion":
        phase_reason = "fase de consolidacion con practica"
    elif phase == "arranque":
        phase_reason = "fase de arranque para no acumular deuda"
    elif phase == "desarrollo":
        phase_reason = "fase de desarrollo de contenido principal"
    else:
        phase_reason = "fase de cierre previa al objetivo"
    return (
        f"Faltan {days_left} {day_label} para {event.event_type} '{event.title}'; "
        f"{phase_reason}, foco en: {focus_topic}."
    )


def build_study_plan(events: list[StudyEvent], options: PlanOptions) -> list[StudySession]:
    if options.weeks <= 0:
        raise ValueError("`weeks` debe ser > 0.")
    if options.weekly_hours <= 0:
        raise ValueError("`weekly_hours` debe ser > 0.")
    if options.session_minutes <= 0:
        raise ValueError("`session_minutes` debe ser > 0.")
    if options.max_daily_hours <= 0:
        raise ValueError("`max_daily_hours` debe ser > 0.")
    if options.day_start_hour < 0 or options.day_start_hour > 23:
        raise ValueError("`day_start_hour` debe estar entre 0 y 23.")

    upcoming = [event for event in events if event.date >= options.from_date]
    if not upcoming:
        return []

    total_weekly_minutes = int(round(options.weekly_hours * 60))
    max_daily_minutes = int(round(options.max_daily_hours * 60))
    sessions: list[StudySession] = []
    sessions_by_materia: dict[str, int] = {}
    sequence = 1

    for week_idx in range(options.weeks):
        week_start = options.from_date + timedelta(days=7 * week_idx)
        week_end = week_start + timedelta(days=6)
        relevant = [event for event in upcoming if event.date >= week_start]
        if not relevant:
            break

        score_by_materia: dict[str, float] = {}
        for event in relevant:
            score_by_materia[event.materia] = score_by_materia.get(event.materia, 0.0) + _event_score(event, week_start)

        minutes_by_materia = _allocate_minutes(score_by_materia, total_weekly_minutes)
        next_event = _next_event_per_materia(relevant, week_start)

        day_load = [0] * 7
        for materia in sorted(minutes_by_materia.keys(), key=lambda m: (minutes_by_materia[m], m), reverse=True):
            remaining = minutes_by_materia[materia]
            if remaining <= 0:
                continue
            target = next_event[materia]

            while remaining > 0:
                duration = min(options.session_minutes, remaining)
                day_idx = _pick_day(day_load, duration, max_daily_minutes)
                session_date = week_start + timedelta(days=day_idx)
                if session_date > week_end:
                    break
                start_minutes = (options.day_start_hour * 60) + day_load[day_idx]
                start_dt = datetime.combine(session_date, time.min) + timedelta(minutes=start_minutes)
                end_dt = start_dt + timedelta(minutes=duration)
                days_left = max((target.date - session_date).days, 0)
                phase = _planning_phase(target.event_type, days_left)
                materia_seq = sessions_by_materia.get(materia, 0)
                focus_topic = _focus_topic(target, materia_seq, phase)
                focus_reason = _focus_reason(target, days_left, phase, focus_topic)

                session_id = f"{session_date.isoformat()}-{materia.lower().replace(' ', '-')}-{sequence}"
                sequence += 1
                sessions.append(
                    StudySession(
                        id=session_id,
                        materia=materia,
                        start=start_dt,
                        end=end_dt,
                        duration_minutes=duration,
                        week_index=week_idx,
                        target_date=target.date,
                        target_event_type=target.event_type,
                        target_title=target.title,
                        focus_topic=focus_topic,
                        focus_reason=focus_reason,
                    )
                )
                sessions_by_materia[materia] = materia_seq + 1
                day_load[day_idx] += duration
                remaining -= duration

    return sorted(sessions, key=lambda s: (s.start, s.materia, s.id))
