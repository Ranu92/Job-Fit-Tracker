"""Persistence: remember every job we've seen (for 'new since last run') + CSV export."""
import csv
import json
import os
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
HISTORY = os.path.join(HERE, "history.json")
RESULTS_DIR = os.path.join(HERE, "results")


def load_history():
    if os.path.exists(HISTORY):
        try:
            with open(HISTORY, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_history(hist):
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2, ensure_ascii=False)


def mark_seen(jobs, hist):
    """Tag each job as new/seen and record first-seen date in history."""
    today = date.today().isoformat()
    for j in jobs:
        rec = hist.get(j.url)
        if rec is None:
            hist[j.url] = {"first_seen": today, "title": j.title}
            j.is_new = True
        else:
            j.is_new = False
    return jobs


def output_path(label, ext=".xlsx"):
    """results/<Label>_<DD-MM><ext>, e.g. results/Linkedin_17-06.xlsx"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%d-%m")
    return os.path.join(RESULTS_DIR, f"{label}_{stamp}{ext}")


def export_csv(jobs, label="scan"):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%d-%m")     # e.g. Linkedin_17-06
    path = os.path.join(RESULTS_DIR, f"{label}_{stamp}.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["score", "posted_date", "date_confidence", "title", "location",
                    "req_exp", "exp_fit", "new", "source", "url", "matched"])
        for j in jobs:
            w.writerow([j.score, j.posted_date or "unknown", j.date_confidence,
                        j.title, j.location, j.req_exp, j.exp_fit,
                        "NEW" if getattr(j, "is_new", False) else "",
                        j.source, j.url, ", ".join(j.matched)])
    return path
