"""Generic adapter for ANY other careers site.

Renders the page in a real headless Chromium (Playwright) so JavaScript-built
listings load, scrolls to pull in lazy content, then heuristically extracts links
that look like individual job postings. Posting dates are captured when the page
exposes a <time> element; otherwise left unknown (we never invent a date).
"""
import re
import urllib.parse

from .base import Job, USER_AGENT, parse_relative_date

JOB_HINTS = ("/job/", "/jobs/", "/careers/", "/career/", "/position", "/opening",
             "/vacancy", "/req", "gh_jid", "/postings/", "/o/")


def fetch(url: str):
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        raise RuntimeError(
            "Playwright not installed. Run: pip install playwright && playwright install chromium"
        )

    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2500)
            for _ in range(8):  # scroll to trigger lazy-loading / infinite scroll
                page.mouse.wheel(0, 6000)
                page.wait_for_timeout(700)
            rows = page.eval_on_selector_all(
                "a",
                """els => els.map(a => {
                    let t = (a.querySelector('time') ||
                             a.closest('li,div,article,tr')?.querySelector('time'));
                    return {
                        href: a.href,
                        text: (a.innerText || '').trim(),
                        when: t ? (t.getAttribute('datetime') || t.innerText || '') : ''
                    };
                })""",
            )
        finally:
            browser.close()

    base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
    seen, jobs = set(), []
    for r in rows:
        href = (r.get("href") or "").strip()
        text = re.sub(r"\s+", " ", r.get("text") or "").strip()
        if not href or not text or len(text) < 4:
            continue
        low = href.lower()
        if not any(h in low for h in JOB_HINTS):
            continue
        if href in seen or len(text) > 120:
            continue
        seen.add(href)
        iso, conf = parse_relative_date(r.get("when", ""))
        jobs.append(Job(
            title=text,
            url=href,
            posted_text=r.get("when", ""),
            posted_date=iso,
            date_confidence=conf,
            source="generic:" + urllib.parse.urlparse(url).netloc,
        ))
    return jobs
