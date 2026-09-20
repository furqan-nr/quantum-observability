#!/usr/bin/env python3
"""Figure 1: screening flow from the nominal candidate pool to the 68-fix analytic corpus,
extended to show the confirmatory 104-fix corpus (the independent third round of 36 further
fixes, mined from a wider window and dual-coded against the same frozen codebook).

All counts are the manuscript's own published, source-cited numbers (screening_log_70.csv,
candidate_queue_70.csv, included_candidate_audit_70.csv, labels_final_68.csv,
labels_final_104.csv, and Sec. 4.1/4.2/5.1 of build_1a.js) -- this script only draws them; it
does not recompute anything (unlike make_fig4_effect_sizes.py, there is no per-fix raw signal
to recompute here, only the funnel's stage counts, which are already fixed and audited).

Usage:
  python scripts/make_fig1_screening_flow.py
Requires: matplotlib.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- palette (matches the original fig_screening_flow.drawio) ----
BLUE_FILL, BLUE_STROKE, BLUE_TEXT = "#DCE9F9", "#2E5C8A", "#13293D"
RED_FILL, RED_STROKE, RED_TEXT = "#FBE4E4", "#B33A3A", "#7A1F1F"
TAN_FILL, TAN_STROKE, TAN_TEXT = "#FFF3D6", "#C98A1B", "#6B4400"
GRAY_FILL, GRAY_STROKE, GRAY_TEXT = "#F0F0F0", "#8A8A8A", "#3A3A3A"
GREEN_FILL, GREEN_STROKE, GREEN_TEXT = "#E3F2E3", "#3A7D44", "#1F4620"
NAVY_FILL, NAVY_STROKE, NAVY_TEXT = "#1F3B57", "#16283C", "#FFFFFF"
TITLE_COLOR = "#13293D"
ARROW_COLOR = "#333333"


def pick_serif():
    for name in ("Liberation Serif", "Nimbus Roman", "Times New Roman", "DejaVu Serif"):
        if any(name.lower() in f.name.lower() for f in fm.fontManager.ttflist):
            return name
    return "serif"


# ---- geometry: (id, x, y, w, h, fill, stroke, textcolor, lines) ----
# lines: list of (text, bold, fontsize)
PAGE_W, PAGE_H = 900, 1500

BOXES = {
    "baseline": (20, 90, 390, 85, BLUE_FILL, BLUE_STROKE, BLUE_TEXT, [
        ("Baseline corpus", False, 18), ("(existing human-coded PRs)", False, 18),
        ("n = 26", True, 18)]),
    "pool": (470, 90, 390, 85, BLUE_FILL, BLUE_STROKE, BLUE_TEXT, [
        ("New-candidate pool identified", False, 18), ("(3-pass discovery, 4 source streams)", False, 18),
        ("n = 59 reviewed", True, 18)]),
    "scopegate": (20, 210, 390, 55, RED_FILL, RED_STROKE, RED_TEXT, [
        ("Scope-gate exclusions, n = 2", True, 18), ("(1 non-bugfix, 1 out-of-scope)", False, 18)]),
    "retained": (20, 315, 390, 55, BLUE_FILL, BLUE_STROKE, BLUE_TEXT, [
        ("Baseline retained", False, 18), ("n = 24", True, 18)]),
    "screened_in": (470, 210, 390, 55, BLUE_FILL, BLUE_STROKE, BLUE_TEXT, [
        ("Screened in (passes scope rules)", False, 18), ("n = 44", True, 18)]),
    "excluded15": (470, 300, 390, 170, RED_FILL, RED_STROKE, RED_TEXT, [
        ("Excluded, n = 15", True, 18), ("backport duplicate (4)", False, 16),
        ("duplicate of baseline/candidate (5)", False, 16), ("feature/enhancement, not a fix (2)", False, 16),
        ("performance enhancement (2)", False, 16), ("documentation-only (1)", False, 16),
        ("refactor, no product defect (1)", False, 16)]),
    "eligibility": (470, 495, 390, 85, TAN_FILL, TAN_STROKE, TAN_TEXT, [
        ("Eligibility re-audit", False, 18), ("(duplication + scope check)", False, 18),
        ("n = 44", True, 18)]),
    "reaudit": (470, 615, 390, 55, GRAY_FILL, GRAY_STROKE, GRAY_TEXT, [
        ("39 retained as screened + 5 added", False, 18), ("(net n = 44 unchanged)", False, 18)]),
    "nominal": (20, 800, 840, 60, BLUE_FILL, BLUE_STROKE, BLUE_TEXT, [
        ("Nominal candidate corpus", False, 18), ("26 + 44 = 70", True, 18)]),
    "analytic": (20, 900, 840, 60, GREEN_FILL, GREEN_STROKE, GREEN_TEXT, [
        ("Analytic corpus, human double-coded and adjudicated", False, 18), ("24 + 44 = 68", True, 18)]),
    "headline": (20, 1000, 840, 130, NAVY_FILL, NAVY_STROKE, NAVY_TEXT, [
        ("Equivalence-invisible", True, 22), ("19 / 68 = 27.9% ≈ 28%", True, 24),
        ("95% Wilson CI [19%, 40%]", True, 20)]),
    # --- confirmatory extension (new) ---
    "third_round": (20, 1160, 840, 70, TAN_FILL, TAN_STROKE, TAN_TEXT, [
        ("Independent third round (wider mining window, same frozen codebook)", False, 18),
        ("n = 36 further fixes, dual-coded", True, 18)]),
    "extended": (20, 1250, 840, 60, GREEN_FILL, GREEN_STROKE, GREEN_TEXT, [
        ("Extended corpus (confirmatory)", False, 18), ("68 + 36 = 104", True, 18)]),
    "headline2": (20, 1330, 840, 130, NAVY_FILL, NAVY_STROKE, NAVY_TEXT, [
        ("Equivalence-invisible (confirmatory)", True, 22), ("29 / 104 = 27.9%", True, 24),
        ("95% Wilson CI [20%, 37%]", True, 20)]),
}

EDGES = [
    ("baseline", "scopegate", 2.0), ("scopegate", "retained", 2.0),
    ("retained", "nominal", 2.5),
    ("pool", "screened_in", 2.0), ("screened_in", "excluded15", 2.0),
    ("excluded15", "eligibility", 2.0), ("eligibility", "reaudit", 2.0),
    ("reaudit", "nominal", 2.5),
    ("nominal", "analytic", 2.5), ("analytic", "headline", 2.5),
    ("headline", "third_round", 2.5), ("third_round", "extended", 2.5),
    ("extended", "headline2", 2.5),
]


def to_mpl_y(y, h):
    """drawio y grows downward from the top; matplotlib data y grows upward."""
    return PAGE_H - y - h


def draw_box(ax, key, serif):
    x, y, w, h, fill, stroke, textcolor, lines = BOXES[key]
    ym = to_mpl_y(y, h)
    box = FancyBboxPatch((x, ym), w, h, boxstyle="round,pad=0,rounding_size=10",
                          linewidth=2, edgecolor=stroke, facecolor=fill, zorder=2)
    ax.add_patch(box)
    n = len(lines)
    line_h = h / (n + 0.9)
    top_y = ym + h - line_h * 0.68
    for i, (text, bold, fs) in enumerate(lines):
        ax.text(x + w / 2, top_y - i * line_h, text, ha="center", va="center",
                fontsize=fs, fontweight="bold" if bold else "normal",
                color=textcolor, family=serif, zorder=3)
    return x, ym, w, h


def draw_arrow(ax, src, dst, geoms, lw):
    sx, sy, sw, sh = geoms[src]
    dx, dy, dw, dh = geoms[dst]
    x0, y0 = sx + sw / 2, sy
    x1, y1 = dx + dw / 2, dy + dh
    arr = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=16,
                           linewidth=lw, color=ARROW_COLOR, zorder=1, shrinkA=0, shrinkB=0)
    ax.add_patch(arr)


def main():
    serif = pick_serif()
    fig, ax = plt.subplots(figsize=(PAGE_W / 100, PAGE_H / 100), dpi=200)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, PAGE_W)
    ax.set_ylim(0, PAGE_H)
    ax.axis("off")

    ax.text(PAGE_W / 2, PAGE_H - 45,
            "Screening flow: 68-fix corpus, extended to 104",
            ha="center", va="center", fontsize=25, fontweight="bold",
            color=TITLE_COLOR, family=serif)

    geoms = {}
    for key in BOXES:
        geoms[key] = draw_box(ax, key, serif)

    for src, dst, lw in EDGES:
        draw_arrow(ax, src, dst, geoms, lw)

    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig("fig_screening_flow.png", facecolor="white")
    print("wrote fig_screening_flow.png")
    print(f"pixel size: {fig.get_figwidth()*200:.0f} x {fig.get_figheight()*200:.0f}, "
          f"aspect ratio (w/h): {PAGE_W/PAGE_H:.4f}")


if __name__ == "__main__":
    main()
