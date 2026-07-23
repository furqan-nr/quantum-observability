#!/usr/bin/env python3
"""R2-4 characterization: pull GitHub PR metadata for the 68 mined transpiler fixes.

Reads  data/mining_validation/labels_final_68.csv
Writes data/mining_validation/pr_characterization_raw.csv
       (pr, channel, observable, title, created_at, merged_at,
        time_to_merge_days, additions, deletions, changed_files, commits)

Auth: set GITHUB_TOKEN to avoid the 60-req/hour unauthenticated limit
      (a classic token with NO scopes is enough for a public repo).
Resumable: re-run to fill any rows that failed or were rate-limited.
"""
import csv, json, os, time, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN   = ROOT / "data" / "mining_validation" / "labels_final_68.csv"
OUT  = ROOT / "data" / "mining_validation" / "pr_characterization_raw.csv"
REPO = "Qiskit/qiskit"
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
FIELDS = ["pr", "channel", "observable", "title", "created_at", "merged_at",
          "time_to_merge_days", "additions", "deletions", "changed_files", "commits"]
FMT = "%Y-%m-%dT%H:%M:%SZ"

def fetch(pr):
    url = "https://api.github.com/repos/%s/pulls/%s" % (REPO, pr)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "cart-r2-4"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main():
    rows = list(csv.DictReader(open(IN)))
    done = {}
    if OUT.exists():
        done = {r["pr"]: r for r in csv.DictReader(open(OUT)) if r.get("merged_at")}
    out = []
    for i, row in enumerate(rows, 1):
        pr = row["pr"]
        if pr in done:
            out.append(done[pr]); print("[%d/%d] #%s cached" % (i, len(rows), pr)); continue
        for _ in range(5):
            try:
                d = fetch(pr)
                ca, ma = d.get("created_at"), d.get("merged_at")
                ttm = ""
                if ca and ma:
                    ttm = round((datetime.strptime(ma, FMT) - datetime.strptime(ca, FMT)).total_seconds() / 86400.0, 2)
                out.append({"pr": pr, "channel": row["channel"], "observable": row["observable"],
                            "title": (d.get("title") or "").replace("\n", " "),
                            "created_at": ca, "merged_at": ma, "time_to_merge_days": ttm,
                            "additions": d.get("additions"), "deletions": d.get("deletions"),
                            "changed_files": d.get("changed_files"), "commits": d.get("commits")})
                print("[%d/%d] #%s ok  (+%s/-%s, %sd)" % (i, len(rows), pr, d.get("additions"), d.get("deletions"), ttm))
                break
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    reset = int(e.headers.get("X-RateLimit-Reset", time.time() + 120))
                    wait = max(5, reset - int(time.time()) + 2)
                    print("  rate-limited; sleeping %ds (set GITHUB_TOKEN to avoid)" % wait); time.sleep(wait); continue
                print("  #%s HTTP %s" % (pr, e.code)); break
            except Exception as e:
                print("  #%s error %s; retry" % (pr, e)); time.sleep(3)
        time.sleep(0.4 if TOKEN else 1.1)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for r in out:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    print("\nwrote %d rows -> %s" % (len(out), OUT))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
