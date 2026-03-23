"""
Calendar service for OptiHire
-------------------------------
Supports two modes:
  1. Google Calendar API  — when GOOGLE_SERVICE_ACCOUNT_JSON is set in .env,
     creates an event on the recruiter's calendar and sends invites to both
     the recruiter and candidate.
  2. ICS file generation  — always available as a fallback / download link.
"""
import os
import json
import uuid
from datetime import datetime, timedelta, timezone
from email import encoders
from email.mime.base import MIMEBase


# ─── ICS / iCalendar helpers ─────────────────────────────────────────────────

def _format_dt(dt: datetime) -> str:
    """Format a *naive* UTC datetime to iCal  YYYYMMDDTHHMMSSZ."""
    return dt.strftime('%Y%m%dT%H%M%SZ')


def build_ics(
    title: str,
    description: str,
    start_utc: datetime,
    end_utc: datetime,
    organizer_email: str,
    attendee_emails: list[str],
    location: str = "Video Call (link will be shared separately)",
    uid: str | None = None,
) -> str:
    """Return a standards-compliant .ics string for the event."""
    uid = uid or f"{uuid.uuid4()}@optihire"
    now_str = _format_dt(datetime.utcnow())
    start_str = _format_dt(start_utc)
    end_str = _format_dt(end_utc)

    attendees = "\r\n".join(
        f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;"
        f"RSVP=TRUE:mailto:{email}"
        for email in attendee_emails
    )

    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//OptiHire//Interview Scheduler//EN\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:REQUEST\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{uid}\r\n"
        f"DTSTAMP:{now_str}\r\n"
        f"DTSTART:{start_str}\r\n"
        f"DTEND:{end_str}\r\n"
        f"SUMMARY:{title}\r\n"
        f"DESCRIPTION:{description.replace(chr(10), '\\n')}\r\n"
        f"LOCATION:{location}\r\n"
        f"ORGANIZER:mailto:{organizer_email}\r\n"
        f"{attendees}\r\n"
        "STATUS:CONFIRMED\r\n"
        "SEQUENCE:0\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    return ics


# ─── Google Calendar API (service account) ───────────────────────────────────

def _get_google_calendar_service():
    """
    Build and return a Google Calendar API service using a service account.
    Returns None if credentials are not configured.
    """
    creds_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not creds_json:
        return None

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        # Accept either a file path or a raw JSON string
        if creds_json.strip().startswith('{'):
            info = json.loads(creds_json)
        else:
            with open(creds_json, 'r') as f:
                info = json.load(f)

        SCOPES = ['https://www.googleapis.com/auth/calendar']
        credentials = service_account.Credentials.from_service_account_info(
            info, scopes=SCOPES
        )

        # Delegate to the recruiter's Google account (domain-wide delegation)
        delegated_email = os.environ.get('GOOGLE_CALENDAR_DELEGATE_EMAIL')
        if delegated_email:
            credentials = credentials.with_subject(delegated_email)

        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"[CalendarService] Could not create Google service: {e}")
        return None


def create_google_calendar_event(
    title: str,
    description: str,
    start_utc: datetime,
    end_utc: datetime,
    organizer_email: str,
    attendee_emails: list[str],
    location: str = "Video Call (link will be shared separately)",
) -> dict | None:
    """
    Create a Google Calendar event and return the event dict (with htmlLink).
    Returns None if the API is not configured or fails.
    """
    service = _get_google_calendar_service()
    if service is None:
        return None

    try:
        event_body = {
            'summary': title,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_utc.isoformat() + 'Z',
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_utc.isoformat() + 'Z',
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in attendee_emails],
            'sendUpdates': 'all',     # send invite emails via Google
            'guestsCanSeeOtherGuests': True,
        }

        calendar_id = os.environ.get('GOOGLE_CALENDAR_ID', 'primary')
        event = service.events().insert(
            calendarId=calendar_id,
            body=event_body,
            sendNotifications=True,
        ).execute()

        return event
    except Exception as e:
        print(f"[CalendarService] Google Calendar API error: {e}")
        return None


# ─── Public interface ─────────────────────────────────────────────────────────

class InterviewScheduleResult:
    """Returned by schedule_interview() to the caller."""

    def __init__(
        self,
        success: bool,
        method: str,                 # 'google_calendar' | 'ics'
        google_event_link: str | None = None,
        ics_content: str | None = None,
        ics_filename: str | None = None,
        error: str | None = None,
    ):
        self.success = success
        self.method = method
        self.google_event_link = google_event_link
        self.ics_content = ics_content
        self.ics_filename = ics_filename
        self.error = error

    def to_dict(self) -> dict:
        return {
            'success': self.success,
            'method': self.method,
            'google_event_link': self.google_event_link,
            'ics_filename': self.ics_filename,
        }


def schedule_interview(
    candidate_name: str,
    candidate_email: str,
    recruiter_name: str,
    recruiter_email: str,
    job_title: str,
    company: str,
    interview_date: str,   # YYYY-MM-DD
    interview_time: str,   # HH:MM  (local time, treated as IST / UTC+5:30)
    duration_minutes: int = 60,
    notes: str = "",
) -> InterviewScheduleResult:
    """
    Schedule an interview.  Tries Google Calendar API first; falls back to
    generating an ICS string that can be served as a file download.
    """
    # Parse date + time → UTC datetime
    naive_dt = datetime.strptime(f"{interview_date} {interview_time}", "%Y-%m-%d %H:%M")
    # Assume IST (UTC+5:30) when no timezone info is available
    ist_offset = timedelta(hours=5, minutes=30)
    start_utc = naive_dt - ist_offset
    end_utc = start_utc + timedelta(minutes=duration_minutes)

    title = f"Interview: {candidate_name} for {job_title} at {company}"
    description = (
        f"OptiHire Interview Invitation\n\n"
        f"Candidate : {candidate_name} ({candidate_email})\n"
        f"Position  : {job_title}\n"
        f"Company   : {company}\n"
        f"Duration  : {duration_minutes} minutes\n"
    )
    if notes:
        description += f"\nAgenda / Notes:\n{notes}"

    attendees = list({recruiter_email, candidate_email})  # deduplicate

    # ── Try Google Calendar API first ────────────────────────────
    gc_event = create_google_calendar_event(
        title=title,
        description=description,
        start_utc=start_utc,
        end_utc=end_utc,
        organizer_email=recruiter_email,
        attendee_emails=attendees,
    )

    if gc_event:
        print(f"[CalendarService] Google Calendar event created: {gc_event.get('htmlLink')}")
        return InterviewScheduleResult(
            success=True,
            method='google_calendar',
            google_event_link=gc_event.get('htmlLink'),
        )

    # ── Fallback: generate ICS content ───────────────────────────
    ics_content = build_ics(
        title=title,
        description=description,
        start_utc=start_utc,
        end_utc=end_utc,
        organizer_email=recruiter_email,
        attendee_emails=attendees,
    )
    safe_name = candidate_name.replace(' ', '_')
    ics_filename = f"interview_{safe_name}_{interview_date}.ics"

    print(f"[CalendarService] ICS file generated: {ics_filename}")
    return InterviewScheduleResult(
        success=True,
        method='ics',
        ics_content=ics_content,
        ics_filename=ics_filename,
    )
