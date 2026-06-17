# PM Job Tracker

Paste **any** careers-site URL → get the **Product Manager roles relevant to your
resume**, with **link + latest posting date**, newest first. Your resume stays
local; nothing is uploaded.

## What it does

A personal job-hunt assistant for Product Managers. Give it a careers-site URL —
or just run it for a default India-wide sweep — and in one pass it:

1. **Fetches the latest openings** directly from the source: Workday, Greenhouse,
   Lever, Ashby and LinkedIn through their own APIs (real posting dates included),
   and any other careers page by rendering it in a real headless browser.
2. **Reads your resume** afresh on every run and builds a matching profile from it —
   your skills (product strategy, roadmaps, agile, analytics, A/B testing) and
   domains (fintech, telematics, SaaS, AI/LLM). Edit the resume and the matching
   adjusts on its own; there's no re-import step.
3. **Scores and tags each role** against that profile — relevance and experience-fit
   (explained below).
4. **Ranks and exports** the matches to a formatted Excel — best experience-fit
   first, then most recent — with clickable links, a fresh file per scan
   (e.g. `Linkedin_17-06.xlsx`), and a `NEW` tag on anything posted since your last run.

Nothing leaves your machine — your resume, settings and results all stay local.

## What each column means

| Column | What it tells you |
|--------|-------------------|
| **Fit%** | How well the role matches your résumé (0–100): title relevance (is it really a PM role?) + how many of your résumé's skills/domains the posting mentions. Higher = closer fit. |
| **Exp Fit** | How the role's *required years* compare to your own PM experience (set in `config.json`), within a ±tolerance. **Fits** = your level · **Stretch (+Ny)** = wants N more years · **Over-qualified** = wants less · **Unknown** = the posting didn't state it. |
| **Posted** | The posting date (exact from APIs, "x days ago" → date from LinkedIn). |
| **Title / Company / Location** | The role, employer and city. |
| **Req Exp** | The raw experience line pulled from the job description (e.g. `5–8 years`). |
| **Source** | Which board it came from (`linkedin`, `greenhouse:razorpay`, `workday:pwc`, …). |
| **Link** | Clickable link straight to the live posting. |

Roles are ordered **Fits first → newest date → Fit%**, so the most relevant,
freshest, right-level roles sit at the top.

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

- A ranked table in the terminal (Fit%, date, NEW tag, title, location, exp-fit, link).
- A formatted **Excel** in `results\` per scan — named by source + date
  (`Linkedin_17-06.xlsx`): bold/centered/coloured headers, colour-coded **Exp Fit**,
  clickable links, frozen header and filters on.
- `history.json` remembers seen jobs so `--new-only` shows only what's new.

Run with no arguments for the default India-wide sweep:

```powershell
python tracker.py
```

## Tuning

- Relevance bar: `min_score` in `config.json` (or `--min-score`).
- Keyword weights / penalised titles: `profile.py` and `scorer.py`.

## Disclaimer

For personal, educational use. It reads public job-board endpoints; respect each
site's Terms of Service and rate limits. Your resume, config and results stay
local and are git-ignored — they are never committed.
