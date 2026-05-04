from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class StudyEvent:
    materia: str
    event_type: str
    title: str
    date: date
    weight: float = 1.0
    difficulty: int = 3
    topics: tuple[str, ...] = ()


@dataclass(frozen=True)
class StudySession:
    id: str
    materia: str
    start: datetime
    end: datetime
    duration_minutes: int
    week_index: int
    target_date: date
    target_event_type: str
    target_title: str
    focus_topic: str = ""
    focus_reason: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "materia": self.materia,
            "start": self.start.isoformat(timespec="minutes"),
            "end": self.end.isoformat(timespec="minutes"),
            "duration_minutes": self.duration_minutes,
            "week_index": self.week_index,
            "target_date": self.target_date.isoformat(),
            "target_event_type": self.target_event_type,
            "target_title": self.target_title,
            "focus_topic": self.focus_topic,
            "focus_reason": self.focus_reason,
        }

    @staticmethod
    def from_dict(raw: dict[str, object]) -> "StudySession":
        return StudySession(
            id=str(raw["id"]),
            materia=str(raw["materia"]),
            start=datetime.fromisoformat(str(raw["start"])),
            end=datetime.fromisoformat(str(raw["end"])),
            duration_minutes=int(raw["duration_minutes"]),
            week_index=int(raw["week_index"]),
            target_date=date.fromisoformat(str(raw["target_date"])),
            target_event_type=str(raw["target_event_type"]),
            target_title=str(raw["target_title"]),
            focus_topic=str(raw.get("focus_topic", "Repaso general")),
            focus_reason=str(raw.get("focus_reason", "Sesion asignada por prioridad y cercania de fecha objetivo.")),
        )
