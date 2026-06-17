"""Greenhouse adapter — boards.greenhouse.io / job-boards.greenhouse.io.

Public board API returns every posting with an updated_at timestamp.
"""
import html
import re

from .base import Job, parse_relative_date
from .http import get_json


def matches(url: str) -> bool:
    return "greenhouse.io" in url


def _token(url: str):
    m = re.search(r"greenhouse\.io/(?:embed/job_board\?for=)?([A-Za-z0-9_-]+)", url)
    if m and m.group(1) not in ("embed",):
        return m.group(1)
    m = re.search(r"[?&]for=([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None


def fetch(url: str):
    token = _token(url)
    if not token:
        return []
    api = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    try:
        data = get_json(api)
    except Exception:
        return []
    jobs = []
    for j in data.get("jobs", []):
        posted = j.get("updated_at") or j.get("first_published") or ""
        iso, conf = parse_relative_date(posted)
        loc = (j.get("location") or {}).get("name", "")
        jobs.append(Job(
            title=j.get("title", "").strip(),
            url=j.get("absolute_url", ""),
            location=loc,
            posted_text=posted,
            posted_date=iso,
            date_confidence=conf,
            source=f"greenhouse:{token}",
            description=re.sub(r"<[^>]+>", " ", html.unescape(j.get("content", "") or ""))[:12000],
        ))
    return jobs
