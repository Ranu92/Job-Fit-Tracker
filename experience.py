"""Extract a role's required years of experience from its description text, and
classify fit against the candidate's own PM experience (with a +/- tolerance).
"""
import re

# Ordered patterns: most specific first. Each yields (min, max|None).
_RANGE = re.compile(r"(\d{1,2})\s*(?:-|to|–|—)\s*(\d{1,2})\s*\+?\s*(?:years|yrs|yoe)", re.I)
_PLUS = re.compile(r"(\d{1,2})\s*\+\s*(?:years|yrs|yoe)", re.I)
_MIN = re.compile(r"(?:minimum|min\.?|at least|atleast)\s*(?:of\s*)?(\d{1,2})\s*(?:years|yrs|yoe)", re.I)
_SINGLE = re.compile(r"(\d{1,2})\s*(?:years|yrs|yoe)\b", re.I)


def extract_required_years(text):
    """Return (min_years, max_years_or_None, raw_snippet) or (None, None, '')."""
    if not text:
        return None, None, ""
    # Prefer text near the word 'experience' to avoid matching unrelated numbers.
    windows = []
    for m in re.finditer(r"experience", text, re.I):
        windows.append(text[max(0, m.start() - 90): m.end() + 90])
    search_spaces = windows or [text]

    for space in search_spaces:
        r = _RANGE.search(space)
        if r:
            a, b = int(r.group(1)), int(r.group(2))
            return min(a, b), max(a, b), r.group(0).strip()
    for space in search_spaces:
        for pat in (_PLUS, _MIN):
            m = pat.search(space)
            if m:
                return int(m.group(1)), None, m.group(0).strip()
    for space in search_spaces:
        m = _SINGLE.search(space)
        if m:
            n = int(m.group(1))
            if 0 < n <= 25:
                return n, None, m.group(0).strip()
    return None, None, ""


def classify_fit(req_min, req_max, candidate_years, tolerance):
    """Label how the role's requirement fits the candidate's experience +/- tolerance."""
    if req_min is None:
        return "Unknown"
    band_low = candidate_years - tolerance
    band_high = candidate_years + tolerance
    hi = req_max if req_max is not None else req_min + 2
    if req_min > band_high:
        return f"Stretch (+{req_min - candidate_years}y)"
    if hi < band_low:
        return "Over-qualified"
    return "Fits"
