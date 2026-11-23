"""Calendar via private iCal link (optional)."""
import os
from datetime import date
import requests
import icalendar
import recurring_ical_events


def today_events():
    url = os.getenv("CALENDAR_ICS_URL")
    if not url:
        return []
    cal = icalendar.Calendar.from_ical(requests.get(url, timeout=20).content)
    today = date.today()
    out = []
    for e in recurring_ical_events.of(cal).at((today.year, today.month, today.day)):
        start = e.get("DTSTART").dt
        out.append((str(start), f"{start} - {e.get('SUMMARY', '(no title)')}"))
    return [t for _, t in sorted(out)]
