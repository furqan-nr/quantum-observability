#!/usr/bin/env python3
"""Table 5 (RQ1.3): surface-characteristic comparison of equivalence-invisible vs observable fixes.

For each of five PR-level signals (lines added, lines deleted, files changed, commits,
time-to-merge in days), computes the two-sided Mann-Whitney U test, Cliff's delta effect size,
and a 10,000-resample bootstrap 95% CI on Cliff's delta (seed = 42), from
data/mining_validation/pr_characterization_raw.csv (19 invisible vs 49 observable fixes).

Reproduces the manuscript's Table 5 medians, Mann-Whitney p-values, and Cliff's delta point
estimates exactly. The bootstrap CI bounds match the published table to within about +/-0.01:
"10,000 resamples, seed 42" fixes the random state but not the exact order in which the RNG is
drawn from, so a logically equivalent bootstrap loop can land on a very slightly different set of
resamples. All five CIs still bracket zero and support the same conclusion either way.

Usage:
  python scripts/table5_stats.py
"""
from __future__ import annotations

import csv

import numpy as np
from scipy.stats import mannwhitneyu

METRICS = [
    ("additions", "lines added"),
    ("deletions", "lines deleted"),
    ("changed_files", "files changed"),
    ("commits", "commits"),
    ("time_to_merge_days", "time-to-merge (days)"),
]

N_RESAMPLES = 10_000
SEED = 42


def load(path):
    invisible, observable = [], []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            target = invisible if r["observable"].strip().lower() == "no" else observable
            target.append(r)
    return invisible, observable


def cliffs_delta(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    gt = (x[:, None] > y[None, :]).sum()
    lt = (x[:, None] < y[None, :]).sum()
    return (gt - lt) / (len(x) * len(y))


def bootstrap_ci(x, y, rng, n_resamples=N_RESAMPLES):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    deltas = np.empty(n_resamples)
    for i in range(n_resamples):
        xs = rng.choice(x, size=len(x), replace=True)
        ys = rng.choice(y, size=len(y), replace=True)
        deltas[i] = cliffs_delta(xs, ys)
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return lo, hi


def main():
    invisible, observable = load("data/mining_validation/pr_characterization_raw.csv")
    print(f"n invisible = {len(invisible)}, n observable = {len(observable)}\n")

    header = f"{'metric':<22}{'inv. median':>12}{'obs. median':>12}{'MW p':>9}{'Cliff d':>10}{'95% CI':>18}"
    print(header)
    print("-" * len(header))

    rng = np.random.default_rng(SEED)
    for col, label in METRICS:
        x = [float(r[col]) for r in invisible]
        y = [float(r[col]) for r in observable]
        med_x, med_y = float(np.median(x)), float(np.median(y))
        _, p = mannwhitneyu(x, y, alternative="two-sided")
        delta = cliffs_delta(x, y)
        lo, hi = bootstrap_ci(x, y, rng)
        print(f"{label:<22}{med_x:>12.2f}{med_y:>12.2f}{p:>9.2f}{delta:>+10.2f}"
              f"  [{lo:+.2f}, {hi:+.2f}]")


if __name__ == "__main__":
    main()
