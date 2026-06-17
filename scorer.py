"""Score a job 0-100 for how well it fits the resume's PM profile.

TIGHT mode: a job only qualifies if its TITLE contains a genuine Product-Manager
role phrase (Product Manager / Owner / Management / Lead / Head of Product, etc.).
Roles like "Software Engineer - AI Product" are NOT product-management roles, so
they score 0 even though 'product' appears in the title. Resume-derived keywords
then refine the score among the real PM roles.
"""
import re

# Genuine PM role phrases (must appear in the TITLE). "Senior/AI/Digital/Data
# Product Manager" all contain "product manager" and are caught automatically.
PM_TITLE = [
    ("group product manager", 60),
    ("senior product manager", 60),
    ("principal product manager", 60),
    ("technical product manager", 58),
    ("associate product manager", 54),
    ("lead product manager", 58),
    ("product manager", 56),
    ("product owner", 54),
    ("director of product", 60),
    ("head of product", 60),
    ("vp of product", 60),
    ("vice president of product", 60),
    ("chief product officer", 60),
    ("product lead", 52),
    ("product management", 52),
]


def kw_in(blob, kw):
    """Word-boundary match so short tokens ('ai','ml') don't match inside
    'chennai'/'html'. Handles punctuation in keywords (a/b test, gen ai)."""
    return re.search(r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])", blob) is not None


def score_job(job, profile) -> int:
    title = (job.title or "").lower()
    matched = []

    # GATE: must be a real PM role by title, else it's not for us.
    title_score = 0
    for kw, w in PM_TITLE:
        if kw_in(title, kw):
            title_score = max(title_score, w)
            matched.append(kw)
    if title_score == 0:
        job.score = 0
        job.matched = []
        return 0

    # Refine with resume-derived keyword overlap (title + description + location).
    blob = " ".join([title, (job.description or "").lower(), (job.location or "").lower()])
    kw_score = 0
    for kw, w in profile["keywords"].items():
        if kw_in(blob, kw):
            kw_score += w
            matched.append(kw)
    kw_score = min(kw_score, 44)

    job.score = int(min(title_score + kw_score, 100))
    job.matched = sorted(set(matched))
    return job.score
