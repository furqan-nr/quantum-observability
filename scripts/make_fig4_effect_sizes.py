#!/usr/bin/env python3
"""Figure 4 (RQ1.3): Cliff's delta effect sizes, equivalence-invisible vs observable fixes,
on BOTH the primary 68-fix corpus and the extended 104-fix corpus, paired per metric.

Reuses the exact statistical methodology already published as Table 5 / scripts/table5_stats.py:
two-sided Mann-Whitney U, Cliff's delta, and a 10,000-resample bootstrap 95% CI (seed=42) on
Cliff's delta, computed independently from each corpus's own raw PR-characteristic CSV
(data/mining_validation/pr_characterization_raw.csv for n=68, pr_characterization_raw_104.csv
for n=104). This script does not hardcode any number from the manuscript: every value plotted is
recomputed here from the released raw data.

Usage (run from the repo root, with both CSVs under data/mining_validation/):
  python scripts/make_fig4_effect_sizes.py

Requires: numpy, scipy, matplotlib.
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from scipy.stats import mannwhitneyu

METRICS = [
    ("additions", "Lines added"),
    ("deletions", "Lines deleted"),
    ("changed_files", "Files changed"),
    ("commits", "Commits"),
    ("time_to_merge_days", "Time-to-merge (days)"),
]

N_RESAMPLES = 10_000
SEED = 42

NAVY = "#1F4E79"     # 68-fix corpus (primary)
TEAL = "#4FA3C7"     # 104-fix corpus (extended)
GRID = "#D9D9D9"
TEXT = "#1F2A33"


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


def compute(path):
    invisible, observable = load(path)
    rng = np.random.default_rng(SEED)
    rows = []
    for col, label in METRICS:
        x = [float(r[col]) for r in invisible]
        y = [float(r[col]) for r in observable]
        _, p = mannwhitneyu(x, y, alternative="two-sided")
        delta = cliffs_delta(x, y)
        lo, hi = bootstrap_ci(x, y, rng)
        rows.append({"label": label, "p": p, "delta": delta, "lo": lo, "hi": hi})
    return len(invisible), len(observable), rows


def pick_serif():
    for name in ("Liberation Serif", "Nimbus Roman", "Times New Roman", "DejaVu Serif"):
        if any(name.lower() in f.name.lower() for f in fm.fontManager.ttflist):
            return name
    return "serif"


def main():
    n68_inv, n68_obs, rows68 = compute("data/mining_validation/pr_characterization_raw.csv")
    n104_inv, n104_obs, rows104 = compute("data/mining_validation/pr_characterization_raw_104.csv")

    serif = pick_serif()
    plt.rcParams["font.family"] = serif
    plt.rcParams["text.color"] = TEXT
    plt.rcParams["axes.edgecolor"] = TEXT

    n_metrics = len(METRICS)
    pair_gap = 0.85
    group_gap = 2.0
    ys68 = [(n_metrics - 1 - i) * group_gap + pair_gap for i in range(n_metrics)]
    ys104 = [(n_metrics - 1 - i) * group_gap for i in range(n_metrics)]
    ymid = [(n_metrics - 1 - i) * group_gap + pair_gap / 2 for i in range(n_metrics)]

    fig_h = 2.2 + n_metrics * group_gap * 0.62
    fig, ax = plt.subplots(figsize=(15.5, fig_h), dpi=340)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    all_los = [r["lo"] for r in rows68] + [r["lo"] for r in rows104]
    all_his = [r["hi"] for r in rows68] + [r["hi"] for r in rows104]
    xmax = max(all_his + [0])
    xlo_disp = -0.42
    xhi_disp = max(1.02, xmax + 0.35)

    def draw_row(y, row, color, n_x, n_y):
        ax.plot([row["lo"], row["hi"]], [y, y], color=color, linewidth=4.2, zorder=2,
                solid_capstyle="butt")
        ax.plot([row["lo"], row["lo"]], [y - 0.10, y + 0.10], color=color, linewidth=4.2, zorder=2)
        ax.plot([row["hi"], row["hi"]], [y - 0.10, y + 0.10], color=color, linewidth=4.2, zorder=2)
        ax.plot(row["delta"], y, "o", color=color, markersize=17, zorder=3,
                markeredgecolor="white", markeredgewidth=1.2)
        label = (f"δ = {row['delta']:+.2f}  [{row['lo']:+.2f}, {row['hi']:+.2f}]  p = {row['p']:.2f}")
        ax.text(xhi_disp - 0.03, y, label, ha="right", va="center",
                fontsize=20.5, color=color)

    for i in range(n_metrics):
        draw_row(ys68[i], rows68[i], NAVY, n68_inv, n68_obs)
        draw_row(ys104[i], rows104[i], TEAL, n104_inv, n104_obs)
        ax.text(xlo_disp - 0.03, ymid[i], METRICS[i][1], ha="right", va="center",
                fontsize=24, color=TEXT)
    sorted_pairs = sorted(zip(ys104, ys68))
    for k in range(len(sorted_pairs) - 1):
        sep_y = (sorted_pairs[k][1] + sorted_pairs[k + 1][0]) / 2
        ax.axhline(sep_y, color=GRID, linewidth=1.0, xmin=0.0, xmax=1.0, zorder=0)

    ax.axvline(0, color="#8C8C8C", linestyle="--", linewidth=2.0, zorder=1)

    top = max(ys68) + 0.75
    bottom = min(ys104) - 0.75
    ax.set_ylim(bottom, top)
    ax.set_xlim(xlo_disp - 0.02, xhi_disp)
    ax.set_yticks([])
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_linewidth(1.4)

    ax.set_xticks(np.arange(-0.4, 1.01, 0.2))
    ax.tick_params(axis="x", labelsize=21, length=6, width=1.2, colors=TEXT)
    ax.grid(axis="x", color=GRID, linewidth=1.0, zorder=0)
    ax.set_axisbelow(True)

    ax.text(-0.06, top + 0.02, "← Observable higher", ha="center", va="bottom",
            fontsize=21, style="italic", color="#595959", transform=ax.transData)
    ax.text(0.62, top + 0.02, "Invisible higher →", ha="center", va="bottom",
            fontsize=21, style="italic", color="#595959", transform=ax.transData)

    ax.set_title("Effect sizes: equivalence-invisible vs observable fixes (RQ1.3)",
                 fontsize=29, fontweight="bold", color=NAVY, pad=48)
    ax.set_xlabel("Cliff's δ  (negative = observable higher, positive = invisible higher)",
                  fontsize=22, color=TEXT, labelpad=14)

    legend_handles = [
        plt.Line2D([0], [0], marker="o", color=NAVY, markerfacecolor=NAVY, markersize=14,
                   linewidth=4.2, label=f"Primary corpus (n = {n68_inv} vs {n68_obs})"),
        plt.Line2D([0], [0], marker="o", color=TEAL, markerfacecolor=TEAL, markersize=14,
                   linewidth=4.2, label=f"Extended corpus (n = {n104_inv} vs {n104_obs})"),
    ]
    leg = fig.legend(handles=legend_handles, loc="lower center", ncol=2, frameon=False,
                      fontsize=21, handlelength=2.2, columnspacing=3.0,
                      bbox_to_anchor=(0.61, 0.005))
    for text in leg.get_texts():
        text.set_color(TEXT)

    fig.subplots_adjust(left=0.235, right=0.985, top=0.84, bottom=0.27)
    fig.savefig("fig4_effect_sizes.png", facecolor="white")
    print("wrote fig4_effect_sizes.png")
    print(f"aspect ratio (w/h): {fig.get_figwidth()/fig.get_figheight():.4f}")

    for name, n_inv, n_obs, rows in (("68-fix", n68_inv, n68_obs, rows68),
                                      ("104-fix", n104_inv, n104_obs, rows104)):
        print(f"\n{name} corpus (n={n_inv} invisible, {n_obs} observable):")
        for r in rows:
            print(f"  {r['label']:<22} delta={r['delta']:+.2f}  "
                  f"CI=[{r['lo']:+.2f}, {r['hi']:+.2f}]  p={r['p']:.2f}")


if __name__ == "__main__":
    main()
