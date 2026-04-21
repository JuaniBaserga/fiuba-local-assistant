from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .types import StudySession


@dataclass(frozen=True)
class GoogleSyncResult:
    attempted: int
    created: int
    skipped: int
    errors: int
    synced_ids: set[str]


def _event_id_for_session(session_id: str) -> str:
    # Google Calendar event ID allows lowercase letters, digits, '-' and '_'.
    # Keep deterministic to avoid duplicates across reruns.
    digest = hashlib.sha1(session_id.encode("utf-8")).hexdigest()[:24]
    return f"fiuba-{digest}"


def _load_google_service(credentials_file: Path, token_file: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Faltan dependencias para Google Calendar. "
            "Instala: google-api-python-client google-auth-oauthlib"
        ) from exc

    scopes = ["https://www.googleapis.com/auth/calendar.events"]
    creds = None

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_file.exists():
                raise FileNotFoundError(f"No existe credentials file: {credentials_file}")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), scopes)
            creds = flow.run_local_server(port=0)
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(creds.to_json(), encoding="utf-8")

    return build("calendar", "v3", credentials=creds)


def sync_sessions_to_google_calendar(
    *,
    sessions: list[StudySession],
    calendar_id: str,
    credentials_file: Path,
    token_file: Path,
    timezone: str,
    dry_run: bool,
    already_synced_ids: set[str],
    force_resync: bool = False,
    max_events: int | None = None,
) -> GoogleSyncResult:
    selected = sorted(sessions, key=lambda s: (s.start, s.id))
    if max_events is not None:
        selected = selected[:max_events]

    if dry_run:
        to_create = [
            session
            for session in selected
            if force_resync or session.id not in already_synced_ids
        ]
        skipped = len(selected) - len(to_create)
        synced = set(already_synced_ids)
        for session in to_create:
            synced.add(session.id)
        return GoogleSyncResult(
            attempted=len(selected),
            created=len(to_create),
            skipped=skipped,
            errors=0,
            synced_ids=synced,
        )

    service = _load_google_service(credentials_file=credentials_file, token_file=token_file)
    synced = set(already_synced_ids)
    created = 0
    skipped = 0
    errors = 0

    for session in selected:
        if not force_resync and session.id in synced:
            skipped += 1
            continue

        event = {
            "summary": f"Estudio - {session.materia}",
            "description": (
                f"Objetivo: {session.target_event_type} ({session.target_title})\n"
                f"Fecha objetivo: {session.target_date.isoformat()}\n"
                f"Duracion: {session.duration_minutes} minutos\n"
                f"Session ID: {session.id}"
            ),
            "start": {
                "dateTime": session.start.isoformat(),
                "timeZone": timezone,
            },
            "end": {
                "dateTime": session.end.isoformat(),
                "timeZone": timezone,
            },
            "extendedProperties": {
                "private": {"fiuba_session_id": session.id},
            },
        }

        event_id = _event_id_for_session(session.id)
        try:
            service.events().insert(calendarId=calendar_id, body=event, eventId=event_id).execute()
            created += 1
            synced.add(session.id)
        except Exception as exc:
            # 409 conflict -> already exists with same event id; treat as synced.
            message = str(exc)
            if "409" in message or "already exists" in message.lower():
                skipped += 1
                synced.add(session.id)
            else:
                errors += 1

    return GoogleSyncResult(
        attempted=len(selected),
        created=created,
        skipped=skipped,
        errors=errors,
        synced_ids=synced,
    )
