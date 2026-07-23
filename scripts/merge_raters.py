#!/usr/bin/env python3
"""Merge the rater sheets into dual_rater_labels.csv (for Cohen's kappa in mining_stats.py).

Reads Rater 1 (data/observability_mining.csv), Rater 2 (rater2_sheet.csv), and optionally
Rater 3 (rater3_sheet.csv), matches them by `pr`, and writes the merged
data/mining_validation/dual_rater_labels.csv with r1_/r2_/(r3_) columns plus agreement flags.

Run after all raters have classified the expanded PR set:
    python scripts/merge_raters.py
    python scripts/merge_raters.py --rater3 data/mining_validation/rater3_sheet.csv
Then:  python scripts/mining_stats.py --rater3 data/mining_validation/rater3_sheet.csv
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    out = {}
    if not path.exists():
        return out
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pr = (row.get("pr") or "").strip()
            if pr:
                out[pr] = row
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Merge rater sheets into dual_rater_labels.csv.")
    p.add_argument("--rater1", default=str(_REPO / "data" / "observability_mining.csv"))
    p.add_argument("--rater2", default=str(_REPO / "data" / "mining_validation" / "rater2_sheet.csv"))
    p.add_argument("--rater3", default=None)
    p.add_argument("--out", default=str(_REPO / "data" / "mining_validation" / "dual_rater_labels.csv"))
    p.add_argument("--force", action="store_true", help="allow overwriting a larger existing dual file")
    args = p.parse_args(argv)

    r1, r2 = load(Path(args.rater1)), load(Path(args.rater2))
    r3 = load(Path(args.rater3)) if args.rater3 else {}
    prs = [pr for pr in r1 if pr in r2]  # need at least two raters to merge
    missing = [pr for pr in r1 if pr not in r2]

    cols = ["pr", "title", "r1_channel", "r1_observable", "r2_channel", "r2_observable"]
    if r3:
        cols += ["r3_channel", "r3_observable"]
    cols += ["binary_agree", "channel_agree", "note"]

    rows, bdis, cdis = [], 0, 0
    for pr in prs:
        a, b = r1[pr], r2[pr]
        def g(d, k):
            return (d.get(k) or "").strip().lower()
        row = {"pr": pr, "title": (a.get("title") or b.get("title") or "").strip(),
               "r1_channel": g(a, "manifestation_channel"), "r1_observable": g(a, "observable_by_output_oracle"),
               "r2_channel": g(b, "manifestation_channel"), "r2_observable": g(b, "observable_by_output_oracle")}
        if r3 and pr in r3:
            c = r3[pr]
            row["r3_channel"] = g(c, "manifestation_channel")
            row["r3_observable"] = g(c, "observable_by_output_oracle")
        elif r3:
            row["r3_channel"] = row["r3_observable"] = ""
        ba = row["r1_observable"] == row["r2_observable"]
        ca = row["r1_channel"] == row["r2_channel"]
        row["binary_agree"], row["channel_agree"] = ("Y" if ba else "N"), ("Y" if ca else "N")
        row["note"] = "" if (ba and ca) else "ADJUDICATE"
        bdis += (not ba); cdis += (not ca)
        rows.append(row)

    out_path = Path(args.out)
    if out_path.exists() and not args.force:
        existing = max(0, sum(1 for _ in open(out_path, encoding="utf-8")) - 1)
        if existing > len(rows):
            raise SystemExit(
                f"refusing to overwrite {out_path.name} ({existing} rows) with fewer rows ({len(rows)}); "
                f"this protects the current dual-rater data. Fully classify the expanded set first, "
                f"or pass --force if you really mean to shrink it.")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"merged {len(rows)} PRs -> {args.out}")
    print(f"  binary disagreements : {bdis}   (rows flagged ADJUDICATE)")
    print(f"  channel disagreements: {cdis}")
    if missing:
        print(f"  WARNING: {len(missing)} Rater-1 PRs not yet in Rater 2's sheet: {', '.join(sorted(missing)[:15])}"
              + (" ..." if len(missing) > 15 else ""))
    print("\nNext: fill 'note' for ADJUDICATE rows, then run:\n"
          "  python scripts/mining_stats.py" + (" --rater3 " + args.rater3 if args.rater3 else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
