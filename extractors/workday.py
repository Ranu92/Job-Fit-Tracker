"""Workday adapter — works for ANY *.myworkdayjobs.com tenant (PwC, Deloitte, etc.).

Uses the public CXS jobs search API which returns titles, locations and a
'postedOn' date string, so it is far more reliable than scraping the rendered page.
"""
import re

from .base import Job, parse_relative_date
from .http import post_json

SEARCH_TERMS = ["product manager", "product owner", "product"]


def matches(url: str) -> bool:
    return "myworkdayjobs.com" in url


def _parse_url(url: str):
    """Return (host, tenant, site). URL: https://<tenant>.<wdN>.myworkdayjobs.com/<locale>/<site>/..."""
    m = re.match(r"https?://([^/]+)", url)
    host = m.group(1) if m else ""
    tenant = host.split(".")[0]
    path = re.sub(r"https?://[^/]+", "", url).strip("/")
    parts = [p for p in path.split("/") if p]
    site = None
    for p in parts:
        if re.fullmatch(r"[a-z]{2}-[A-Z]{2}", p):  # locale like en-US
            continue
        site = p
        break
    return host, tenant, site


def fetch(url: str):
    host, tenant, site = _parse_url(url)
    if not site:
        return []
    api = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    referer = {"Referer": url, "Origin": f"https://{host}"}
    seen, jobs = set(), []
    for term in SEARCH_TERMS:
        offset = 0
        while offset < 200:  # safety cap per term
            try:
                data = post_json(
                    api,
                    {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": term},
                    headers=referer,
                )
            except Exception:
                break
            postings = data.get("jobPostings", []) or []
            if not postings:
                break
            for p in postings:
                path = p.get("externalPath", "")
                full = f"https://{host}/{site}{path}" if path else url
                if full in seen:
                    continue
                seen.add(full)
                posted = p.get("postedOn", "")
                iso, conf = parse_relative_date(posted)
                jobs.append(Job(
                    title=p.get("title", "").strip(),
                    url=full,
                    location=p.get("locationsText", ""),
                    posted_text=posted,
                    posted_date=iso,
                    date_confidence=conf,
                    source=f"workday:{tenant}",
                ))
            total = data.get("total", 0)
            offset += 20
            if offset >= total:
                break
    return jobs
