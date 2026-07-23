# Mining-study expansion guide (C2): 26 → ≥ 60 fixes

The original 26 were mined from **merged pull requests labelled `mod: transpiler`** on the Qiskit
repo. Keep that source (it is PR-keyed and matches the existing sheet); the release notes are a poor
substitute because they key fixes by the *issue* number, not the fixing PR, and duplicate silently.

## Status: 70-PR corpus staged (1 Jul)
Harvesting is **done** — 44 screened-in PRs (audit: 44 include / 15 exclude, no overlap with the 26)
were appended to every rater sheet with **blank** label fields, giving a **70-PR** corpus. Provenance is
in `screening_log_70.csv`, `included_candidate_audit_70.csv`, `mining_seed_issue_resolution_70.csv`, and
`HARVESTING_70_README.md`. **Raters' next action: classify the 44 blank rows** in `rater1_sheet.csv` /
`observability_mining.csv`, `rater2_sheet.csv`, and `rater3_sheet.csv` (Mistral = Rater 4,
`mistral_rater4_raw.csv`, kept separate from the human agreement analysis). Note: `rater2_sheet.csv` is at
53 rows — Rater 2 still owes 17 of the original 26 plus the 44 new. Then run `merge_raters.py` →
`mining_stats.py`.

## Primary method — GitHub PR search (faithful, PR-keyed)

Open these in a browser (you're signed in, so no rate limit) and page through the results:

- **All merged transpiler PRs (newest first):**
  `https://github.com/Qiskit/qiskit/pulls?q=is%3Apr+is%3Amerged+label%3A%22mod%3A+transpiler%22+sort%3Acreated-desc`
- **Narrow to bug fixes** (add the bug label, or scan titles for "Fix"):
  `https://github.com/Qiskit/qiskit/pulls?q=is%3Apr+is%3Amerged+label%3A%22mod%3A+transpiler%22+label%3Abug`

For each **bug-fix** PR (exclude features/enhancements/refactors), add a row to
`data/observability_mining.csv` (Rater 1): `pr, title, manifestation_channel,
observable_by_output_oracle, confidence, notes` — classified per `CODEBOOK.md`. Work newest→oldest
across the 2.x line; extend into 1.4/1.3 if you need more to clear 60. Target **n ≥ 60** (ideally 80–100).

### Keying + de-dup rules
- **Key by the fixing PR number** (not the issue it closes). If a source gives you an issue, open it and
  take the PR that closed it.
- De-dup against the existing 26 **by fix identity** (pass + description), not just the number — an issue
  and its PR are different numbers for the *same* fix.

## Supplementary seeds (harvested from 2.1–2.3 release notes)

These are candidate transpiler fixes to **map to their fixing PR, then classify** (they are *issue*
numbers). Unlabelled on purpose — classify them independently per the codebook.

| issue | release | fix (short) |
|---|---|---|
| 15579 | 2.3 | BreakLoopOp/ContinueLoopOp wrongly treated as control-flow in some passes |
| 15145 | 2.2 | ALAP/ASAP scheduling raised a false "No durations" error on empty circuits |
| 15116 | 2.2 | Optimize1qGatesDecomposition: Rust panic → TranspilerError on oversized circuit |
| 15071 | 2.2 | SabreSwap pickle failure after run() |
| 14974 | 2.2 | CommutationChecker mishandled controlled gates not controlled on all-ones |
| 14743 | 2.2 | Optimize1qGatesDecomposition emitted gates not in the Target (fixed-angle 1q) |
| 14646 | 2.2 | ConsolidateBlocks panicked instead of raising on stale PropertySet analysis |
| 14407 | 2.2 | CommutativeInverseCancellation wrong on Clifford / control-flow / non-invertible ops |
| 14329 | 2.1 | generate_preset_pass_manager ignored Target timing constraints |

> Skip **issue 14729** (VF2Layout non-determinism) — it is already study event **H3** (PR #14730).
> Two entries the auto-scan flagged are **not transpiler** (14107 `is_unitary`, 14653 `ParameterExpression`) — exclude.

## Third rater
Rater 3’s existing 26-row independent human classifications are retained. After Rater 1 freezes the expanded PR list, Rater 3 will independently classify each newly added PR using the codebook and PR evidence only.

## Fourth rater
Mistral provides an auxiliary LLM classification and is excluded from the primary human inter-rater reliability statistics

## Merge + adjudicate
Once all three sheets cover the full expanded PR set, merge them (this overwrites `dual_rater_labels.csv`,
so the guard blocks it until your merge is at least as large as the current file — use `--force`):
```
python scripts/merge_raters.py --rater3 data/mining_validation/rater3_sheet.csv --force
```
It writes `dual_rater_labels.csv` with `r1_/r2_/r3_` columns and flags every disagreement `ADJUDICATE`.
Resolve each flagged row (majority-of-three or discussion) and record the reasoning in its `note`.

## Recompute
```
python scripts/mining_stats.py --rater3 data/mining_validation/rater3_sheet.csv
```
Report the new proportion + Wilson CI, Cohen's κ + CI, and Fleiss' κ; update §6.6 and Table 17.
