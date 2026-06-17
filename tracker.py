#!/usr/bin/env python3
"""PM Job Tracker — paste any careers-site URL, get relevant Product Manager roles
matched against your resume, sorted by latest posting date.

Usage:
  python tracker.py scan <url> [<url> ...]   Scan one or more URLs
  python tracker.py scan-all                 Scan every saved source
  python tracker.py add-source <url>         Save a URL to your watchlist
  python tracker.py remove-source <url>      Remove a saved URL
  python tracker.py list-sources             Show saved sources
  python tracker.py set-resume <path>        Point at a new resume file

Options (for scan / scan-all):
  --min-score N    Only show jobs scoring >= N (default from config, 40)
  --new-only       Only show jobs not seen in a previous run
  --limit N        Show at most N results
"""
import json
import os
import sys

import extractors
import enrich
import experience
from profile import build_profile
from scorer import score_job
import store
import xlsx_export

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "config.json")


def load_config():
    with open(CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def _label_for(jobs):
    """Name the output file after the source when a single site was scanned."""
    srcs = {(j.source or "").split(":")[0] for j in jobs if j.source}
    if len(srcs) == 1:
        return next(iter(srcs)).capitalize()   # e.g. "Linkedin", "Greenhouse"
    return "All"


def scan(urls, cfg, min_score, new_only, limit, do_exp=True):
    profile = build_profile(cfg.get("resume_path", ""))
    if not profile["resume_present"]:
        print(f"!! Resume not found at {cfg.get('resume_path')!r} — scoring on keywords only.\n")

    hist = store.load_history()
    all_jobs = []
    for url in urls:
        print(f"Scanning: {url}")
        try:
            jobs, adapter = extractors.fetch(url)
        except Exception as e:
            print(f"  FAILED: {e}\n")
            continue
        print(f"  [{adapter}] {len(jobs)} raw listings")
        for j in jobs:
            score_job(j, profile)
        all_jobs.extend(jobs)

    # de-dupe by url, keep highest score
    by_url = {}
    for j in all_jobs:
        if j.url not in by_url or j.score > by_url[j.url].score:
            by_url[j.url] = j
    jobs = list(by_url.values())

    jobs = [j for j in jobs if j.score >= min_score]
    store.mark_seen(jobs, hist)
    store.save_history(hist)
    if new_only:
        jobs = [j for j in jobs if getattr(j, "is_new", False)]

    if do_exp:
        cand = cfg.get("pm_experience_years", 4)
        tol = cfg.get("exp_tolerance", 1)
        print(f"\nReading job descriptions for experience fit ({len(jobs)} roles, "
              f"you = {cand}y +/-{tol})...")
        for n, j in enumerate(jobs, 1):
            enrich.ensure_description(j)
            rmin, rmax, raw = experience.extract_required_years(j.description)
            j.req_exp = raw
            j.exp_fit = experience.classify_fit(rmin, rmax, cand, tol)
            if n % 25 == 0:
                print(f"  ...{n}/{len(jobs)}")

    # Order: "Fits" first, then newest posting date, then Fit% high -> low.
    jobs.sort(key=lambda j: (1 if j.exp_fit == "Fits" else 0, j.posted_date or "0000-00-00", j.score),
              reverse=True)
    if limit:
        jobs = jobs[:limit]

    _print_table(jobs, min_score)
    if jobs:
        label = _label_for(jobs)
        rows = [{"score": j.score, "posted_date": j.posted_date or "unknown",
                 "title": j.title, "location": j.location, "req_exp": j.req_exp or "-",
                 "exp_fit": j.exp_fit or "Unknown", "source": j.source, "url": j.url}
                for j in jobs]
        xpath = store.output_path(label, ".xlsx")
        xlsx_export.write_xlsx(rows, xpath)
        print(f"\nSaved Excel: {xpath}")


def _print_table(jobs, min_score):
    print(f"\n=== {len(jobs)} relevant PM role(s), score >= {min_score}, Fits first, latest date first ===\n")
    if not jobs:
        print("  (nothing matched — try a lower --min-score or a different URL)")
        return
    for i, j in enumerate(jobs, 1):
        tag = " [NEW]" if getattr(j, "is_new", False) else ""
        date_s = j.posted_date or "unknown"
        if j.posted_date and j.date_confidence != "high":
            date_s += f" (~{j.date_confidence})"
        print(f"{i:>2}. [{j.score:>3}] {date_s:<22}{tag} {j.title}")
        if j.location:
            print(f"     {j.location}")
        if j.exp_fit:
            print(f"     exp: {j.req_exp or '?'} -> {j.exp_fit}")
        print(f"     {j.url}")
        if j.matched:
            print(f"     match: {', '.join(j.matched[:8])}")
        print()


def main():
    args = sys.argv[1:]
    cfg = load_config()
    if not args:
        # No args -> run the default daily India sweep (all configured sources, no limit).
        print("No URL given -> running default India scan (all saved sources, no limit)...\n")
        scan(cfg.get("sources", []), cfg, cfg.get("min_score", 50),
             new_only=False, limit=None, do_exp=True)
        return
    cmd, rest = args[0], args[1:]

    if cmd == "add-source":
        for u in rest:
            if u not in cfg["sources"]:
                cfg["sources"].append(u)
        save_config(cfg)
        print(f"Sources now: {len(cfg['sources'])}")
        return
    if cmd == "remove-source":
        cfg["sources"] = [s for s in cfg["sources"] if s not in rest]
        save_config(cfg)
        print(f"Sources now: {len(cfg['sources'])}")
        return
    if cmd == "list-sources":
        for s in cfg["sources"]:
            print(" -", s)
        if not cfg["sources"]:
            print(" (none saved — add with: python tracker.py add-source <url>)")
        return
    if cmd == "set-resume":
        if not rest:
            print("Usage: python tracker.py set-resume <path>")
            return
        cfg["resume_path"] = rest[0]
        save_config(cfg)
        print(f"Resume path set to: {rest[0]}")
        return

    if cmd in ("scan", "scan-all"):
        min_score = cfg.get("min_score", 40)
        new_only = "--new-only" in rest
        do_exp = "--no-exp" not in rest
        limit = None
        urls = []
        it = iter(rest)
        for a in it:
            if a == "--min-score":
                min_score = int(next(it))
            elif a == "--limit":
                limit = int(next(it))
            elif a in ("--new-only", "--no-exp"):
                pass
            else:
                urls.append(a)
        if cmd == "scan-all":
            urls = cfg.get("sources", [])
        if not urls:
            print("No URL given. Usage: python tracker.py scan <url>")
            return
        scan(urls, cfg, min_score, new_only, limit, do_exp)
        return

    print(__doc__)


if __name__ == "__main__":
    main()
