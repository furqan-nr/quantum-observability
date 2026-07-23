#!/usr/bin/env python3
"""Statistics for the observability mining study (C2): proportion + interval, and inter-rater agreement.

Extends data/mining_validation/compute_kappa.py with the intervals a reviewer will require:
  * the output-invisible PROPORTION with a Wilson 95% CI;
  * Cohen's kappa (Rater 1 vs Rater 2) on the binary and channel judgments, each with a 95% CI;
  * Fleiss' kappa across >=3 raters when a rater3 sheet is present;
  * a per-channel breakdown.

Dependency-free (standard library only). Run from the repo root:
    python scripts/mining_stats.py
    python scripts/mining_stats.py --rater3 data/mining_validation/rater3_sheet.csv
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
INVISIBLE = {"contract_metadata", "determinism", "global_phase"}


def load(path: Path, fields):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pr = (row.get("pr") or "").strip()
            if pr:
                out[pr] = {k: (row.get(k) or "").strip().lower() for k in fields}
    return out


def wilson_ci(x: int, n: int, z: float = 1.96):
    if n == 0:
        return (None, None, None)
    p = x / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = (z / den) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def cohen_kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    cats = sorted({c for ab in pairs for c in ab})
    po = sum(1 for a, b in pairs if a == b) / n
    ac = {c: 0 for c in cats}
    bc = {c: 0 for c in cats}
    for a, b in pairs:
        ac[a] += 1
        bc[b] += 1
    pe = sum((ac[c] / n) * (bc[c] / n) for c in cats)
    k = (po - pe) / (1 - pe) if (1 - pe) > 1e-12 else 1.0
    se = math.sqrt(po * (1 - po) / (n * (1 - pe) ** 2)) if (1 - pe) > 1e-12 else 0.0
    return {"kappa": k, "se": se, "lo": k - 1.96 * se, "hi": k + 1.96 * se, "po": po, "n": n}


def fleiss_kappa(rows):
    """rows: list of dicts {category: count} with a constant number of raters per item."""
    if not rows:
        return None
    cats = sorted({c for r in rows for c in r})
    N = len(rows)
    n = sum(rows[0].get(c, 0) for c in cats)  # raters per item (assumed constant)
    if n < 2:
        return None
    p = {c: sum(r.get(c, 0) for r in rows) / (N * n) for c in cats}
    Pe = sum(v * v for v in p.values())
    Pi = [(sum(r.get(c, 0) ** 2 for c in cats) - n) / (n * (n - 1)) for r in rows]
    Pbar = sum(Pi) / N
    return {"kappa": (Pbar - Pe) / (1 - Pe) if (1 - Pe) > 1e-12 else 1.0, "N": N, "raters": n}


def interpret(k):
    if k is None:
        return "n/a"
    return ("less than chance" if k < 0 else "slight" if k <= .20 else "fair" if k <= .40
            else "moderate" if k <= .60 else "substantial" if k <= .80 else "almost perfect")


def main(argv=None):
    p = argparse.ArgumentParser(description="Observability mining statistics (proportion + kappa intervals).")
    p.add_argument("--rater1", default=str(_REPO / "data" / "observability_mining.csv"))
    p.add_argument("--dual", default=str(_REPO / "data" / "mining_validation" / "dual_rater_labels.csv"),
                   help="merged dual-rater file (r1_/r2_ columns) for Cohen's kappa")
    p.add_argument("--rater2", default=str(_REPO / "data" / "mining_validation" / "rater2_sheet.csv"))
    p.add_argument("--rater3", default=None, help="optional third-rater sheet (enables Fleiss' kappa)")
    p.add_argument("--truth", default="rater1", choices=["rater1", "rater2"],
                   help="which sheet's labels define the headline proportion (use the adjudicated sheet)")
    args = p.parse_args(argv)

    fields = ["observable_by_output_oracle", "manifestation_channel", "confidence"]
    r1 = load(Path(args.rater1), fields)
    r2 = load(Path(args.rater2), fields) if Path(args.rater2).exists() else {}
    r3 = load(Path(args.rater3), fields) if args.rater3 and Path(args.rater3).exists() else {}

    truth = r1 if args.truth == "rater1" else r2
    N = len(truth)
    x = sum(1 for v in truth.values() if v["observable_by_output_oracle"] == "no"
            or v["manifestation_channel"] in INVISIBLE)
    prop, lo, hi = wilson_ci(x, N)
    print(f"# Observability mining statistics  (truth = {args.truth}, N = {N})")
    print("# NOTE: this reads an EARLIER provisional rater sheet and is retained for provenance only.")
    print("# The AUTHORITATIVE, human-adjudicated headline is 19/68 = 28% [19-40%] in")
    print("# data/mining_validation/labels_final_68.csv (kappa 0.86 on the 44, 0.67 on the seed).")
    print("\n## Output-invisible proportion (headline)")
    print(f"  {x}/{N} = {prop*100:.1f}%   Wilson 95% CI [{lo*100:.0f}%, {hi*100:.0f}%]")

    # per-channel breakdown
    print("\n## Manifestation channels (truth sheet)")
    chans = {}
    for v in truth.values():
        chans[v["manifestation_channel"]] = chans.get(v["manifestation_channel"], 0) + 1
    for c in sorted(chans, key=lambda k: -chans[k]):
        mark = "  (invisible)" if c in INVISIBLE else ""
        print(f"  {c:22} {chans[c]:>3}{mark}")

    # Cohen's kappa from the merged dual-rater file (r1_/r2_ columns), binary + channel
    dual_path = Path(args.dual)
    if dual_path.exists():
        dual = load(dual_path, ["r1_observable", "r2_observable", "r1_channel", "r2_channel"])
        print(f"\n## Cohen's kappa, Rater 1 vs Rater 2  (n = {len(dual)}, from {dual_path.name})")
        for a, b, label in [("r1_observable", "r2_observable", "binary observability"),
                            ("r1_channel", "r2_channel", "7-class channel")]:
            pairs = [(v[a], v[b]) for v in dual.values() if v[a] and v[b]]
            k = cohen_kappa(pairs)
            if k:
                print(f"  {label:22} kappa = {k['kappa']:.3f}  95% CI [{k['lo']:.2f}, {k['hi']:.2f}]  "
                      f"({interpret(k['kappa'])}; agree {k['po']*100:.1f}%)")

    # Fleiss' kappa across 3 raters (binary), when rater3 present
    if r2 and r3:
        common3 = [pr for pr in r1 if pr in r2 and pr in r3]
        rows = []
        for pr in common3:
            labels = [r1[pr]["observable_by_output_oracle"], r2[pr]["observable_by_output_oracle"],
                      r3[pr]["observable_by_output_oracle"]]
            if all(labels):
                rows.append({c: labels.count(c) for c in set(labels)})
        fk = fleiss_kappa(rows)
        if fk:
            print(f"\n## Fleiss' kappa, 3 raters, binary observability  (N = {fk['