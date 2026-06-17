"""Lever adapter — jobs.lever.co/<company>.

Public postings API returns createdAt (epoch ms) for each role.
"""
import re

from .base import Job, parse_relative_date
from .http import get_json


def matches(url: str) -> bool:
    return "lever.co" in url


def _company(url: str):
    m = re.search(r"lever\.co/([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None


def fetch(url: str):
    company = _company(url)
    if not company:
        return []
    api = f"https://api.lever.co/v0/postings/{company}?mode=json"
    try:
        data = get_json(api)
    except Exception:
        return []
    jobs = []
    for j in data:
        created = j.get("createdAt", "")
        iso, conf = parse_relative_date(str(created))
        cats = j.get("categories", {}) or {}
        jobs.append(Job(
            title=j.get("text", "").strip(),
            url=j.get("hostedUrl", ""),
            location=cats.get("location", ""),
            posted_text=str(created),
            posted_date=iso,
            date_confidence=conf,
            source=f"lever:{company}",
            description=re.sub(r"<[^>]+>", " ", j.get("descriptionPlain", "") or j.get("description", ""))[:12000],
        ))
    return jobs
