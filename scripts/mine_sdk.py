#!/usr/bin/env python3
"""N3 — cross-SDK mining harvester (build-free; commit metadata only).

Clones (blobless) another quantum SDK's repo and harvests merged BUG-FIX commits touching its
transpiler/compilation passes into a candidate CSV for channel coding with the SAME frozen codebook
used for Qiskit. Commit subject+body come from commit objects (no blob fetch).

Usage:
  python scripts/mine_sdk.py --repo https://github.com/CQCL/tket --sdk tket \
      --paths tket/src/Mapping tket/src/Placement tket/src/Transformations \
      --out data/mining_validation/tket_candidates.csv
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

FIX_RE = re.compile(r"\b(fix|bug|bugfix|incorrect|wrong|crash|segfault|regress|broken|invalid)\b", re.I)
EXCLUDE_RE = re.compile(r"\b(doc|docs|doxygen|format|clang-format|typo|changelog|ci|infra|lint|"
                        r"test only|test-only|version bump|release)\b", re.I)


def clone(repo: str) -> Path:
    d = Path(tempfile.mkdtemp(prefix="mine_sdk_")) / "repo"
    print(f">> cloning {repo} (blobless) ...")
    subprocess.run(["git", "clone", "--filter=blob:none", "--quiet", repo, str(d)], check=True)
    return d


def harvest(repo_dir: Path, paths: list[str]) -> list[dict]:
    fmt = "%H%x1f%cs%x1f%s%x1f%b%x1e"
    raw = subprocess.run(["git", "-C", str(repo_dir), "--no-pager", "log", "--no-merges",
                          f"--format={fmt}", "--", *paths],
                         capture_output=True, check=True).stdout
    out = raw.decode("utf-8", "replace")   # git messages are UTF-8; avoid Windows cp1252 default
    rows = []
    for rec in out.split("\x1e"):
        rec = rec.strip()
        if not rec:
            continue
        parts = rec.split("\x1f")
        if len(parts) < 4:
            continue
        h, date, subj, body = parts[0], parts[1], parts[2], parts[3]
        if not FIX_RE.search(subj) or EXCLUDE_RE.search(subj):
            continue
        m = re.search(r"\(#(\d+)\)", subj)
        pr = m.group(1) if m else ""
        rows.append({"sdk_commit": h[:12], "date": date, "pr": pr,
                     "subject": subj.strip(),
                     "body_excerpt": " ".join(body.split())[:400]})
    return rows


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--sdk", required=True)
    p.add_argument("--paths", nargs="+", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--repo-dir", default=None, help="use an existing clone instead of cloning")
    args = p.parse_args()

    repo_dir = Path(args.repo_dir) if args.repo_dir else clone(args.repo)
    rows = harvest(repo_dir, args.paths)
    outp = _ROOT / args.out
    outp.parent.mkdir(parents=True, exist_ok=True)
    fields = ["sdk_commit", "date", "pr", "subject", "body_excerpt",
              "manifestation_channel", "observable_by_output_oracle", "confidence", "notes"]
    with open(outp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            r.update(manifestation_channel="", observable_by_output_oracle="", confidence="", notes="")
            w.writerow(r)
    print(f">> {len(rows)} candidate bug-fix commits for {args.sdk} -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
