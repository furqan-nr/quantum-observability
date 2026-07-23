#!/usr/bin/env python3
"""Inter-rater agreement for the transpiler-fix observability mining study.

Computes Cohen's kappa between Rater 1 and Rater 2 on:
  (a) the binary `observable_by_output_oracle` judgment  <- the headline claim
  (b) the multi-class `manifestation_channel` judgment

Authoritative source is the COMPLETE double-coding in `dual_rater_labels.csv`.
The older `rater2_sheet.csv` was only partially filled (n=9) and over-reported kappa;
this script no longer uses it for the headline number.

Reports raw agreement, Cohen's kappa, a bootstrap 95% CI, and a confidence breakdown.
Dependency-free. Run:  python3 data/mining_validation/compute_kappa.py
"""
import csv, os, random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DUAL = os.path.join(HERE, "dual_rater_labels.csv")
R1_CONF = os.path.join(HERE, "..", "observability_mining.csv")


def cohen_kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None, None, 0
    cats = sorted({c for ab in pairs for c in ab})
    po = sum(1 for a, b in pairs if a == b) / n
    ac = {c: 0 for c in cats}
    bc = {c: 0 for c in cats}
    for a, b in pairs:
        ac[a] += 1
        bc[b] += 1
    pe = sum((ac[c] / n) * (bc[c] / n) for c in cats)
    k = (po - pe) / (1 - pe) if (1 - pe) > 1e-12 else 1.0
    return k, po, n


def bootstrap_ci(pairs, iters=5000, seed=0):
    if len(pairs) < 2:
        return None, None
    rng = random.Random(seed)
    ks = []
    n = len(pairs)
    for _ in range(iters):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        k, _, _ = cohen_kappa(sample)
        if k is not None:
            ks.append(k)
    ks.sort()
    return ks[int(0.025 * len(ks))], ks[int(0.975 * len(ks)) - 1]


def interp(k):
    if k is None: return "n/a"
    if k < 0:    return "less than chance"
    if k <= .20: return "slight"
    if k <= .40: return "fair"
    if k <= .60: return "moderate"
    if k <= .80: return "substantial"
    return "almost perfect"


def main():
    rows = list(csv.DictReader(open(DUAL, newline="", encoding="utf-8")))
    conf = {}
    if os.path.exists(R1_CONF):
        for r in csv.DictReader(open(R1_CONF, newline="", encoding="utf-8")):
            conf[(r.get("pr") or "").strip()] = (r.get("confidence") or "").strip().lower()

    print("Source: dual_rater_labels.csv   PRs double-coded: %d" % len(rows))
    for f, lab in [("observable", "BINARY observable_by_output_oracle (headline)"),
                   ("channel", "manifestation_channel (7-class)")]:
        pairs = [((r["r1_" + f] or "").strip().lower(), (r["r2_" + f] or "").strip().lower())
                 for r in rows]
        k, po, n = cohen_kappa(pairs)
        lo, hi = bootstrap_ci(pairs)
        print("\n== %s ==" % lab)
        print("  n               : %d" % n)
        print("  raw agreement   : %.1f%%" % (po * 100))
        ci = ("  [95%% CI %.3f, %.3f]" % (lo, hi)) if lo is not None else ""
        print("  Cohen's kappa   : %.3f  (%s)%s" % (k, interp(k), ci))
        dis = [r["pr"] for r in rows
               if (r["r1_" + f] or "").strip().lower() != (r["r2_" + f] or "").strip().lower()]
        if dis:
            print("  disagreements   : %d -> %s" % (len(dis), ", ".join(dis)))

    no1 = sum(1 for r in rows if (r["r1_observable"] or "").strip().lower() == "no")
    print("\nOutput-invisible (R1 'no'): %d/%d = %d%%" % (no1, len(rows), round(no1 / len(rows) * 100)))

    if conf:
        c = Counter(conf.get(r["pr"], "?") for r in rows)
        print("Confidence distribution (R1): " + ", ".join("%s=%d" % (k, v) for k, v in sorted(c.items())))


if __name__ == "__main__":
    main()
