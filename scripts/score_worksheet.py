#!/usr/bin/env python3
"""Score a coded mining worksheet: output-invisible rate + Wilson CI + channel breakdown, and (with a
second rater) Cohen's kappa on the binary observability judgment.

Accepts the blinded worksheet format (columns in_scope_bugfix(yes/no), manifestation_channel,
observable_by_output_oracle(yes/no)) OR the candidate CSV format (manifestation_channel,
observable_by_output_oracle, with 'exclude' channel = out of scope).

Usage:
  python scripts/score_worksheet.py data/mining_validation/tket_worksheet_BLINDED.csv
  python scripts/score_worksheet.py rater1.csv --rater2 rater2.csv
"""
from __future__ import annotations

import argparse
import csv
import math
from collections import Counter

INVIS = {"contract_metadata", "determinism", "global_phase"}


def _get(row, *prefixes):
    for pfx in prefixes:
        for k in row:
            if k.strip().lower().startswith(pfx):
                return (row[k] or "").strip().lower()
    return ""


def _load(path):
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
        text = fh.read().replace("\x00", "")
    out = []
    for r in csv.DictReader(text.splitlines()):
        inscope_col = _get(r, "in_scope_bugfix", "in_scope")
        channel = _get(r, "manifestation_channel")
        obs = _get(r, "observable_by_output_oracle")
        if inscope_col:
            inscope = inscope_col in ("yes", "y", "true", "1")
        else:
            inscope = channel not in ("exclude", "")
        if not inscope:
            continue
        if obs in ("no", "yes"):
            invisible = (obs == "no")
        else:
            invisible = channel in INVIS
        out.append({"key": _get(r, "sdk_commit", "pr", "sha") or r.get("pr", ""),
                    "channel": channel, "invisible": invisible})
    return out


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def cohen_kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    po = sum(1 for a, b in pairs if a == b) / n
    a1 = sum(1 for a, _ in pairs if a) / n
    b1 = sum(1 for _, b in pairs if b) / n
    pe = a1 * b1 + (1 - a1) * (1 - b1)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("worksheet")
    ap.add_argument("--rater2", default=None)
    args = ap.parse_args()

    rows = _load(args.worksheet)
    n = len(rows)
    inv = sum(1 for r in rows if r["invisible"])
    ch = Counter(r["channel"] for r in rows)
    print("file: " + args.worksheet)
    print("in-scope n = " + str(n))
    if n:
        lo, hi = wilson(inv, n)
        print("OUTPUT-INVISIBLE: {}/{} = {:.0f}%  [Wilson 95% CI {:.0f}-{:.0f}%]".format(
            inv, n, 100 * inv / n, 100 * lo, 100 * hi))
        print("channels: " + str(dict(ch)))
        print("invisible-channel breakdown: " + str({c: ch[c] for c in INVIS if ch.get(c)}))
    else:
        print("no in-scope rows (code the worksheet first: set in_scope_bugfix and the channel columns)")

    if args.rater2:
        r1 = {row["key"]: row for row in rows}
        r2 = {row["key"]: row for row in _load(args.rater2)}
        common = [k for k in r1 if k in r2]
        pairs = [(r1[k]["invisible"], r2[k]["invisible"]) for k in common]
        if pairs:
            agree = sum(1 for a, b in pairs if a == b) / len(pairs)
            k = cohen_kappa(pairs)
            print("\n-- two-rater agreement (binary observability, n={} both-in-scope) --".format(len(pairs)))
            print("raw agreement = {:.1f}%   Cohen's kappa = {:.3f}".format(100 * agree, k))
        else:
            print("\nno overlapping in-scope rows between raters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
