# PM Job Tracker

Paste **any** careers-site URL → get the **Product Manager roles relevant to your
resume**, with **link + latest posting date**, newest first. Your resume stays
local; nothing is uploaded.

## What it does

A personal job-hunt assistant for Product Managers. Point it at any careers site
(or just run it for a default India-wide sweep) and it will:

1. **Pull the latest job postings** straight from the source — Workday, Greenhouse,
   Lever, Ashby and LinkedIn via their own APIs (so you get real posting dates),
   and any other careers page by rendering it in a real headless browser.
2. **Read your résumé** (`.docx`) on every run and turn it into a matching profile —
   skills (product strategy, roadmaps, agile, analytics, A/B testing) and domains
   (fintech, telematics, SaaS, AI/LLM). Update the résumé and the matching updates
   itself, no extra step.
3. **Score and categorise every role** against you (see below).
4. **Rank and export** the matches to a formatted Excel — *roles that fit your
   experience first, then newest first* — with clickable links, one file per scan
   (`Linkedin_17-06.xlsx`), and a `NEW` tag for anything that appeared since your
   last run.

Everything runs locally. Your résumé, settings and results never leave your machine.

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
