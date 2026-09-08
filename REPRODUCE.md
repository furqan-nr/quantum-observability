# Reproducibility package

This archive accompanies the manuscript **"An Empirical Study of Equivalence-Invisible Bug Fixes in
Quantum Transpilers (Qiskit, tket, Cirq)"** (Nasir, Shah, Alam; submitted to the *Journal of Systems
and Software*, Elsevier).

- Repository: https://github.com/furqan-nr/quantum-observability
- Archive (DOI): [10.5281/zenodo.22484774](https://doi.org/10.5281/zenodo.22484774) (Zenodo, archiving GitHub release `v1.0.0`)
- License: MIT (see `LICENSE`)

This repository is the reproduction artifact only; the manuscript and its figures are maintained
separately.

## What is here

```
scripts/             the five reproduction entry points (see the commands below)
data/
  mining_validation/  final 68-fix labels, the 104-fix secondary check, human
                       worksheets, the frozen codebook, adjudication trail,
                       source-validation, R3's independent labels, surface-
                       characteristic data, and the tket/Cirq cross-SDK worksheets
                       (labels_final_68.csv is the canonical 68-fix corpus, 28% equivalence-invisible)
  rq14_spotcheck/                RQ1.4 mechanism-coding: title-level spot-check (kappa=0.41)
  rq14_invisible19_recode/       RQ1.4 mechanism-coding: diff-level recheck of all 19
                                 equivalence-invisible fixes (kappa=0.87)
declarations/         signed independent-coder declarations (R2, R3)
```

## Requirements

Python 3.9+, standard library only, plus `scipy` and `numpy` for `scripts/table5_stats.py`. No
package install is needed — the scripts are run directly from the repository root.

## 1. Oracle-observability mining study (the headline finding)

```bash
# authoritative headline over the final, human-adjudicated 68-fix corpus:
python -c "import csv; r=list(csv.DictReader(open('data/mining_validation/labels_final_68.csv'))); inv=sum(x['observable']=='no' for x in r); print(f'{inv}/{len(r)} = {round(100*inv/len(r))}% equivalence-invisible')"
python scripts/score_worksheet.py data/mining_validation/human_worksheet_44_R1.csv --rater2 data/mining_validation/human_worksheet_44_R2.csv   # pairwise kappa on the 44
```

Expected: of 68 in-scope merged Qiskit transpiler bug-fixes, **19/68 = 28%** lie in channels a
black-box output-equivalence oracle cannot observe (contract/metadata 10, non-determinism 4, dropped
global phase 5), Wilson 95% CI **[19%, 40%]**. The 44 newly coded fixes reached pairwise Cohen's
**kappa = 0.86** (95.5% agreement) and the 24-fix seed **kappa = 0.67**. Final labels:
`data/mining_validation/labels_final_68.csv`; the codebook and adjudication trail are alongside it.

A secondary, wider-window robustness check (36 further fixes, same frozen codebook) merges into
`data/mining_validation/labels_final_104.csv`: **29/104 = 27.9%**, Wilson 95% CI **[20%, 37%]**
(`BATCH_002_CODING_COMPLETE.md`). A fully independent third coder (R3) also labelled all 68 fixes;
`scripts/r3_sensitivity_check.py` compares R3 against the adjudicated R1/R2 labels (94.1% raw
agreement, Cohen's kappa = 0.86; taking R3 alone would raise the rate to 23/68 = 33.8%, not lower it).

## 1a. Cross-SDK replication — RQ1.2

```bash
python scripts/score_worksheet.py data/mining_validation/tket_worksheet_R1.csv --rater2 data/mining_validation/tket_worksheet_R2.csv
python scripts/score_worksheet.py data/mining_validation/cirq_worksheet_R1.csv --rater2 data/mining_validation/cirq_worksheet_R2.csv
```

Expected: tket **7/21 = 33%**, Wilson 95% CI [17%, 55%], Cohen's kappa = 0.77 (substantial) —
independently dual-coded replication evidence, comparable in scale to Qiskit. Cirq **2/10 = 20%**,
CI [6%, 51%], kappa = 0.52 (moderate) — reported as exploratory rather than replication evidence,
since Cirq's transformer bug-fix history has too few remaining eligible cases at this scope to grow
the sample responsibly (see `data/mining_validation/tket_replication.md`).

## RQ1.3 — are equivalence-invisible fixes distinguishable by surface characteristics?

```bash
python scripts/pull_pr_metadata.py      # set GITHUB_TOKEN to avoid the API rate limit (no scope needed)
#   -> data/mining_validation/pr_characterization_{raw,summary}.csv
python scripts/table5_stats.py          # Table 5: medians, Mann-Whitney U, Cliff's delta, bootstrap 95% CI
```

Expected: a two-sided Mann–Whitney U over the 19 invisible vs 49 observable fixes finds no dimension
distinguishing the groups (all p ≥ 0.12, all Cliff's |delta| ≤ 0.22, every bootstrap 95% CI on delta
brackets zero) — equivalence-invisible fixes are ordinary-looking on these five cheap signals, so they
cannot be triaged by a surface heuristic. The comparison is underpowered (19 vs 49) rather than proof
of no true difference.

## RQ1.4 — recurring fault-mechanism categories (exploratory)

Single-coder, diff-verified mechanism-category coding of all 68 fixes is in
`data/rq14_spotcheck/rq14_mechanism_coding_EVIDENCE_VERIFIED.csv` (see `RQ14_MECHANISM_CODING_STATUS.md`
for how this superseded two earlier, less reliable passes). Two independent-coder reliability checks
sit alongside it, both human-coding studies rather than re-runnable scripts:

- `data/rq14_spotcheck/` — an earlier title-level spot-check on a mixed 19-item sample (10
  contract/metadata fixes + 9 random draws): Cohen's kappa = 0.41 (moderate). Superseded as the basis
  for any reported reliability figure, but kept for the methodological record
  (`SPOTCHECK_RESULTS.md`).
- `data/rq14_invisible19_recode/` — a full, diff-level independent recoding of all 19
  equivalence-invisible fixes specifically (the subset the manuscript's Discussion depends on):
  17/19 raw agreement (89.5%), Cohen's kappa = 0.87 (almost-perfect). Both disagreements were
  adjudicated against each PR's own GitHub diff; both resolved in favor of the original label, so no
  category count changes (`RECODE_RESULTS.md`).

## Label source-validation

16 fixes were source-checked in both directions (11 primary source validations plus a 5-case
symmetric false-negative audit); all 16 agreed with the coded channel. This is a manual
construct-validity check, not a re-runnable script — `data/mining_validation/label_source_validation.csv`
is the artifact.

## Notes

- The reported inter-rater agreement is a pairwise Cohen's kappa between the two independent human
  coders; disagreements were adjudicated against the frozen codebook.
- Every number reported in the manuscript traces to a file in `data/mining_validation/` or one of the
  two `rq14_*` folders; none is re-derived from data outside this archive.
