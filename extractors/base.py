"""Shared Job model + helpers used by every extractor."""
from dataclasses import dataclass, field
from datetime import date, timedelta
import re

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


@dataclass
class Job:
    title: str
    url: str
    location: str = ""
    posted_text: str = ""          # raw, e.g. "Posted 3 Days Ago"
    posted_date: str = ""          # YYYY-MM-DD, or "" if unknown
    date_confidence: str = "low"   # high | medium | low
    source: str = ""               # site / extractor name
    description: str = ""
    score: int = 0
    matched: list = field(default_factory=list)
    req_exp: str = ""              # raw required-experience snippet, e.g. "5-8 years"
    exp_fit: str = ""              # Fits | Stretch (+Ny) | Over-qualified | Unknown


def parse_relative_date(text, today=None):
    """Turn '3 days ago' / 'Posted Today' / a timestamp into (iso_date, confidence)."""
    if today is None:
        today = date.today()
    if not text:
        return "", "low"
    t = str(text).lower()

    # already an ISO date or epoch-ish timestamp
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", t)
    if m:
        return m.group(0), "high"
    m = re.search(r"\b(1[0-9]{9}|[0-9]{13})\b", t)  # unix seconds / ms
    if m:
        val = int(m.group(0))
        if val > 1e12:
            val //= 1000
        try:
            return date.fromtimestamp(val).isoformat(), "high"
        except Exception:
            pass

    if "today" in t or "just posted" in t or "few hours" in t:
        return today.isoformat(), "high"
    if "yesterday" in t:
        return (today - timedelta(days=1)).isoformat(), "high"
    m = re.search(r"(\d+)\+?\s*day", t)
    if m:
        return (today - timedelta(days=int(m.group(1)))).isoformat(), "medium"
    m = re.search(r"(\d+)\+?\s*week", t)
    if m:
        return (today - timedelta(weeks=int(m.group(1)))).isoformat(), "medium"
    m = re.search(r"(\d+)\+?\s*month", t)
    if m:
        return (today - timedelta(days=30 * int(m.group(1)))).isoformat(), "low"
    return "", "low"
