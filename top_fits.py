"""Show the best India roles that FIT the candidate's 4yr +/-1 experience."""
import csv, glob, os, re

f = max(glob.glob("results/scan_*.csv"), key=os.path.getmtime)
rows = list(csv.DictReader(open(f, encoding="utf-8-sig")))
CITY = re.compile(r"india|bengaluru|bangalore|gurugram|gurgaon|mumbai|hyderabad|pune|delhi|noida|chennai|kolkata|jaipur|kochi", re.I)

fits = [r for r in rows if r.get("exp_fit") == "Fits" and CITY.search(r["location"] or "")]
fits.sort(key=lambda r: (int(r["score"]), r["posted_date"]), reverse=True)

print("Top FITS roles (your 4yr +/-1), best score first:\n")
for r in fits[:18]:
    print(f"{r['score']:>3} | {r['posted_date']} | {(r['req_exp'] or '-'):<10} | {r['title'][:44]:<44} | {r['location'][:34]}")
    print(f"      {r['url']}")
