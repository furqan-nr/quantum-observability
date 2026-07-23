#!/usr/bin/env python3
"""Agreement statistics for the analytic Qiskit transpiler bug-fix corpus.

Default input is the 25-row, scope-screened seed corpus.  For later batches, pass
a merged analytic CSV with the same r1_/r2_ columns:

    python3 compute_kappa_analytic.py --input dual_rater_labels_analytic_full.csv

This measures agreement between the frozen Rater 1 and blinded ChatGPT Rater 2 raw
labels.  It does not use adjudicated/final labels or third-rater audit labels.
"""
import argparse
import csv
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "dual_rater_labels_analytic_seed.csv"

def cohen_kappa(pairs):
    n = len(pairs)
    if not n:
        return None, None, 0
    cats = sorted({label for pair in pairs for label in pair})
    observed = sum(a == b for a, b in pairs) / n
    counts_a = {c: 0 for c in cats}
    counts_b = {c: 0 for c in cats}
    for a, b in pairs:
        counts_a[a] += 1
        counts_b[b] += 1
    expected = sum((counts_a[c] / n) * (counts_b[c] / n) for c in cats)
    kappa = (observed - expected) / (1 - expected) if (1 - expected) > 1e-12 else 1.0
    return kappa, observed, n

def bootstrap_ci(pairs, iters=5000, seed=0):
    if len(pairs) < 2:
        return None, None
    rng = random.Random(seed)
    n = len(pairs)
    values = []
    for _ in range(iters):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        value, _, _ = cohen_kappa(sample)
        if value is not None:
            values.append(value)
    values.sort()
    return values[int(0.025 * len(values))], values[int(0.975 * len(values)) - 1]

def interpretation(kappa):
    if kappa is None: return "n/a"
    if kappa < 0: return "less than chance"
    if kappa <= 0.20: return "slight"
    if kappa <= 0.40: return "fair"
    if kappa <= 0.60: return "moderate"
    if kappa <= 0.80: return "substantial"
    return "almost perfect"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                        help="CSV containing pr, r1_channel, r1_observable, r2_channel, r2_observable.")
    args = parser.parse_args()
    rows = list(csv.DictReader(args.input.open(newline="", encoding="utf-8-sig")))
    required = {"pr", "r1_channel", "r1_observable", "r2_channel", "r2_observable"}
    if not rows:
        raise SystemExit("Input CSV has no data rows.")
    missing = required - set(rows[0])
    if missing:
        raise SystemExit(f"Input CSV is missing required columns: {sorted(missing)}")

    print(f"Source: {args.input.name}   eligible PRs double-coded: {len(rows)}")
    for suffix, headline in [
        ("observable", "BINARY observable_by_output_oracle (headline)"),
        ("channel", "manifestation_channel (7-class)"),
    ]:
        pairs = [
            ((r[f"r1_{suffix}"] or "").strip().lower(),
             (r[f"r2_{suffix}"] or "").strip().lower())
            for r in rows
        ]
        if any(not a or not b for a, b in pairs):
            raise SystemExit(f"Blank {suffix} label found; do not calculate kappa until double-coding is complete.")
        kappa, raw, n = cohen_kappa(pairs)
        lo, hi = bootstrap_ci(pairs)
        disagreements = [
            r["pr"] for r, (a, b) in zip(rows, pairs) if a != b
        ]
        print(f"\n== {headline} ==")
        print(f"  n               : {n}")
        print(f"  raw agreement   : {raw * 100:.1f}%")
        print(f"  Cohen's kappa   : {kappa:.3f}  ({interpretation(kappa)})  [95% CI {lo:.3f}, {hi:.3f}]")
        print(f"  disagreements   : {len(disagreements)}" +
              (f" -> {', '.join(disagreements)}" if disagreements else ""))

if __name__ == "__main__":
    main()
