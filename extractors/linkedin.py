"""LinkedIn adapter — uses the public 'jobs-guest' search API (no login).

Honest limits: LinkedIn rate-limits and may temporarily block by IP if you pull a
lot quickly. It returns a relative posting date ('x days ago'). If it gets blocked
the generic Playwright path is used as a fallback by the router.
"""
import re
import time
import urllib.parse

from .base import Job, parse_relative_date
from .http import get

GUEST = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


def matches(url: str) -> bool:
    return "linkedin.com" in url


def _params_from_url(url: str):
    q = urllib.parse.urlparse(url).query
    qs = urllib.parse.parse_qs(q)
    params = {}
    if "keywords" in qs:
        params["keywords"] = qs["keywords"][0]
    if "location" in qs:
        params["location"] = qs["location"][0]
    if "f_C" in qs:
        params["f_C"] = qs["f_C"][0]          # company id filter
    if "geoId" in qs:
        params["geoId"] = qs["geoId"][0]
    params.setdefault("keywords", "product manager")
    return params


_CARD = re.compile(r"<li>.*?</li>", re.S)


def _parse_cards(htmlsrc):
    out = []
    for li in _CARD.findall(htmlsrc):
        title = _grab(li, r'base-search-card__title">\s*(.*?)\s*<')
        link = _grab(li, r'href="(https://[^"]*?/jobs/view/[^"]+)"')
        company = _grab(li, r'base-search-card__subtitle">\s*<a[^>]*>\s*(.*?)\s*<')
        loc = _grab(li, r'job-search-card__location">\s*(.*?)\s*<')
        dt = _grab(li, r'datetime="([^"]+)"')
        ago = _grab(li, r'listdate[^>]*>\s*(.*?)\s*<')
        if not title or not link:
            continue
        link = re.sub(r"\?.*$", "", link)
        out.append((title, link, company, loc, dt or ago))
    return out


def _grab(s, pat):
    m = re.search(pat, s, re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""


def fetch(url: str):
    base = _params_from_url(url)
    seen, jobs = set(), []
    for start in range(0, 200, 25):  # up to ~200 results
        params = dict(base)
        params["start"] = start
        api = GUEST + "?" + urllib.parse.urlencode(params)
        try:
            htmlsrc = get(api, headers={"Accept": "text/html"})
        except Exception:
            break
        cards = _parse_cards(htmlsrc)
        if not cards:
            break
        for title, link, company, loc, when in cards:
            if link in seen:
                continue
            seen.add(link)
            iso, conf = parse_relative_date(when)
            jobs.append(Job(
                title=title,
                url=link,
                location=" - ".join(x for x in (company, loc) if x),
                posted_text=when,
                posted_date=iso,
                date_confidence=conf,
                source="linkedin",
            ))
        time.sleep(1.0)  # be polite; reduces block risk
    return jobs
