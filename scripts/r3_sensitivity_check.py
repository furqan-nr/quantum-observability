#!/usr/bin/env python3
"""R1/R2-vs-R3 sensitivity check on the 68-fix corpus's headline observability rate.

Compares the adjudicated R1/R2 labels (data/mining_validation/labels_final_68.csv) against the
third volunteer's (R3) fully independent labels (data/mining_validation/rater3_sheet.csv) for the
68 items both label in common. R3's labels are not pooled into the reported channel-taxonomy
kappa (see PROVENANCE.md); this script answers a narrower question: if R3's labels were taken
alone instead of the adjudicated R1/R2 labels, would the headline rate move up or down?

Usage:
  python scripts/r3_sensitivity_check.py
"""
from __future__ import annotations

import csv


def load_adjudicated(path):
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            out[r["pr"].strip()] = (r["observable"].strip().lower() == "no")
    return out


def load_r3(path):
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            pr = r["pr"].strip()
            obs = (r.get("observable_by_output_oracle") or "").strip().lower()
            if obs in ("yes", "no"):
                out[pr] = (obs == "no")
    return out


def cohens_kappa(pairs):
    n = len(pairs)
    po = sum(1 for a, b in pairs if a == b) / n
    p_a1 = sum(1 for a, _ in pairs if a) / n
    p_b1 = sum(1 for _, b in pairs if b) / n
    pe = p_a1 * p_b1 + (1 - p_a1) * (1 - p_b1)
    if pe == 1:
        return 1.0, po, pe
    return (po - pe) / (1 - pe), po, pe


def main():
    adjudicated = load_adjudicated("data/mining_validation/labels_final_68.csv")
    r3 = load_r3("data/mining_validation/rater3_sheet.csv")

    common = sorted(set(adjudicated) & set(r3), key=int)
    if len(common) != 68:
        print(f"WARNING: expected 68 common items, found {len(common)}")

    pairs = [(adjudicated[pr], r3[pr]) for pr in common]
    kappa, po, pe = cohens_kappa(pairs)

    n = len(pairs)
    adj_invisible = sum(1 for a, _ in pairs if a)
    r3_invisible = sum(1 for _, b in pairs if b)
    disagreements = [pr for pr in common if adjudicated[pr] != r3[pr]]

    print(f"n = {n}")
    print(f"Adjudicated R1/R2 rate: {adj_invisible}/{n} = {100 * adj_invisible / n:.1f}%")
    print(f"R3-alone rate:          {r3_invisible}/{n} = {100 * r3_invisible / n:.1f}%")
    print(f"Raw agreement: {100 * po:.1f}%  (Pe = {pe:.3f})")
    print(f"Cohen's kappa: {kappa:.4f}")
    print(f"Disagreements ({len(disagreements)}): PR " + ", ".join(f"#{pr}" for pr in disagreements))
    for pr in disagreements:
        direction = "R3 says invisible, adjudicated says observable" if r3[pr] else \
                    "adjudicated says invisible, R3 says observable"
        print(f"  #{pr}: {direction}")


if __name__ == "__main__":
    main()
