"""Fetch a job's full description when an extractor didn't already provide one,
so we can read its required years of experience. Source-aware + paced.
"""
import re
import time

from extractors.http import get, get_json


def ensure_description(job):
    """Populate job.description in place if empty. Best-effort; never raises."""
    if job.description and len(job.description) > 80:
        return job.description
    src = (job.source or "").split(":")[0]
    try:
        if src == "workday":
            job.description = _workday(job.url)
        elif src == "linkedin":
            job.description = _linkedin(job.url)
        else:
            job.description = _plain(job.url)
    except Exception:
        job.description = job.description or ""
    return job.description


def _workday(url):
    # url: https://<host>/<site>/job/...   tenant = first host label
    m = re.match(r"https?://([^/]+)/([^/]+)(/.*)", url)
    if not m:
        return ""
    host, site, ext = m.group(1), m.group(2), m.group(3)
    tenant = host.split(".")[0]
    api = f"https://{host}/wday/cxs/{tenant}/{site}{ext}"
    data = get_json(api, headers={"Referer": url})
    info = data.get("jobPostingInfo", {}) or {}
    return re.sub(r"<[^>]+>", " ", info.get("jobDescription", "") or "")[:12000]


def _linkedin(url):
    m = re.search(r"-(\d{6,})(?:\?|$)", url) or re.search(r"(\d{6,})", url)
    if not m:
        return ""
    job_id = m.group(1)
    api = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    html = get(api, headers={"Accept": "text/html"})
    m2 = re.search(r'show-more-less-html__markup[^>]*>(.*?)</div>', html, re.S)
    body = m2.group(1) if m2 else html
    time.sleep(0.6)  # pace to reduce block risk
    return re.sub(r"<[^>]+>", " ", body)[:12000]


def _plain(url):
    html = get(url, headers={"Accept": "text/html"})
    return re.sub(r"<[^>]+>", " ", html)[:12000]
