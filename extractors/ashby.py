"""Ashby adapter — jobs.ashbyhq.com/<org>.

Public job-board API returns publishedDate per posting.
"""
import re

from .base import Job, parse_relative_date
from .http import get_json


def matches(url: str) -> bool:
    return "ashbyhq.com" in url


def _org(url: str):
    m = re.search(r"ashbyhq\.com/([A-Za-z0-9_.-]+)", url)
    return m.group(1) if m else None


def fetch(url: str):
    org = _org(url)
    if not org:
        return []
    api = f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=false"
    try:
        data = get_json(api)
    except Exception:
        return []
    jobs = []
    for j in data.get("jobs", []):
        posted = j.get("publishedAt") or j.get("updatedAt") or ""
        iso, conf = parse_relative_date(posted)
        jobs.append(Job(
            title=j.get("title", "").strip(),
            url=j.get("jobUrl", "") or j.get("applyUrl", ""),
            location=j.get("location", ""),
            posted_text=posted,
            posted_date=iso,
            date_confidence=conf,
            source=f"ashby:{org}",
            description=(j.get("descriptionPlain", "") or "")[:12000],
        ))
    return jobs
