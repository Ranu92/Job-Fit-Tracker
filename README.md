# PM Job Tracker

Paste **any** careers-site URL → get the **Product Manager roles relevant to your
resume**, with **link + latest posting date**, newest first. Your resume stays
local; nothing is uploaded.

## How it matches "any" site

| Site type | How it's read | Dates? |
|-----------|---------------|--------|
| Workday (`*.myworkdayjobs.com` — PwC, etc.) | Official JSON API | ✅ |
| Greenhouse / Lever / Ashby | Official JSON API | ✅ |
| LinkedIn | Public guest jobs API (no login) | ✅ (relative) |
| Any other careers page | Real headless Chrome (Playwright) renders + extracts | when shown |

> LinkedIn rate-limits aggressively — large/fast pulls may get temporarily
> blocked. The tool paces requests and falls back to the browser renderer.

## Setup (one time)

```powershell
pip install -r requirements.txt
python -m playwright install chromium
# create your own config from the template, then edit the resume path:
copy config.example.json config.json
```

Playwright + Chromium are only needed for the generic (non-API) sites. The
Workday/Greenhouse/Lever/Ashby/LinkedIn paths work without them.

## Usage

```powershell
# Scan a single URL
python tracker.py scan "https://pwc.wd3.myworkdayjobs.com/en-US/Global_Experienced_Careers"

# Scan a LinkedIn search URL
python tracker.py scan "https://www.linkedin.com/jobs/search?keywords=product%20manager&location=India"

# Only newly-appeared roles since last run
python tracker.py scan "<url>" --new-only

# Loosen / tighten the relevance bar (default 40)
python tracker.py scan "<url>" --min-score 30

# Build a watchlist and scan it all at once
python tracker.py add-source "<url1>"
python tracker.py add-source "<url2>"
python tracker.py scan-all
```

## When you update your resume

Just save the edited file at the same path — the tool re-reads it on every run, so
nothing else to do. If the new file lives elsewhere:

```powershell
python tracker.py set-resume "C:\path\to\your_resume.docx"
```

## Output

- A ranked table in the terminal (score, date, NEW tag, title, location, link).
- A CSV in `results\` for each scan.
- `history.json` remembers seen jobs so `--new-only` works.

## Tuning

- Relevance bar: `min_score` in `config.json` (or `--min-score`).
- Keyword weights / penalised titles: `profile.py` and `scorer.py`.

## Disclaimer

For personal, educational use. It reads public job-board endpoints; respect each
site's Terms of Service and rate limits. Your resume, config and results stay
local and are git-ignored — they are never committed.
