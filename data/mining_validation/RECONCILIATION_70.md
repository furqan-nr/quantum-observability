# Reconciliation: manuscript (26 / 38%) vs roadmap (70 / 34%) — resolved toward n=70

**Prepared 2026-07-04 · resolves Task #1 of the Q1 roadmap.**
**Decision: expand the manuscript corpus to the 70-candidate set.**

## 1. Why the two documents disagreed

| Source | n | Output-invisible | Basis |
|---|---|---|---|
| Submitted manuscript | 26 | 38% (10/26) | Rater-1 preliminary labels only |
| Adjudicated human dataset (`labels_final.csv`) | 24 | 46% (11/24) [Wilson 28–65%] | 3-rater + adjudication, after #14998 correction and 2 scope-gate exclusions |
| Roadmap (fable 5) | 70 | 34%; channels 15 / 4 / 5 | **Not grounded** — these exact figures appear in no artifact in the repo |

Two facts drove the mismatch:

1. **The manuscript's 38% is stale.** It reports Rater-1-only labels on the nominal 26. The real, adjudicated human number is **46% on n=24** (two PRs — a non-bugfix and an out-of-scope item — were removed by the frozen scope gate; #14998 was corrected from invisible to visible after PR verification).
2. **The roadmap's "70 / 34% / 15-4-5" is a projection, not data.** The 70-set exists only as a *screened candidate corpus*: 26 baseline + 44 newly screened-in PRs (`candidate_queue_70.csv`, `screening_log_70.csv`). The 44 new PRs had **no channel/observability labels** until this pass. The specific "34%" and "15 contract / 4 determinism / 5 global-phase" numbers are nowhere in the artifacts and must not be cited as if measured.

## 2. What was done to reconcile toward 70

Per the hybrid decision:

- **Provisional coding of the 44 new PRs** against the frozen codebook v2, using the `exact_fault_manifestation` descriptions in `screening_log_70.csv`. Stored in `provisional_llm_labels_44.csv` as auxiliary rater **LLM_R4_provisional** — explicitly *not* the headline human IRR. 8 low-confidence rows are flagged `FLAG:` for priority human review.
- **Blinded human worksheet** `human_worksheet_44_BLINDED.csv` prepared for human Raters 2 & 3 (metadata only, no labels, no LLM codes) so the publishable human inter-rater agreement can be computed on the full 70.

## 3. Preliminary combined result (n=68 analytic)

Combining the 24 human-adjudicated rows with the 44 provisional rows:

- **Output-invisible: 19/68 = 27.9% [Wilson 95% CI 19–40%].**
- Invisible-channel breakdown: **contract_metadata 10, global_phase 5, determinism 4**.
- Full channel counts: compilation_failure 27, output_semantic 14, contract_metadata 10, circuit_quality 7, global_phase 5, determinism 4, performance 1.
- Sensitivity (drop 8 low-confidence new rows): **18/60 = 30.0% [20–43%]**.

Nominal candidate corpus = 70 (26 + 44); analytic n = 68 after two scope-gate exclusions in the baseline. Report both counts transparently.

## 4. The headline moves DOWN, not up

The new 44 PRs are dominated by **crashes/panics/rejections (19 compilation_failure) — all output-visible**. So the new batch is only **18% invisible**, pulling the combined figure to **~28%**, below the manuscript's 38%, below the adjudicated 46%, and below the roadmap's projected 34%. Note the invisible *channel shape* still matches the roadmap on global_phase (5) and determinism (4); the gap is entirely in contract_metadata (10 measured vs 15 projected) and the large visible tail the projection omitted.

This is the correct, defensible direction: a larger, less cherry-picked corpus regularizes the estimate. The finding — that a substantial minority (~1 in 4 to 1 in 3, CI 19–40%) of real transpiler regressions are invisible to output-equivalence oracles — is intact and now better powered.

## 5. Canonical numbers to use going forward

Until the human round closes, cite the corpus as **n≈70 (68 analytic), ~28% output-invisible [95% CI 19–40%], preliminary — human coding of the 44 new PRs in progress**. Do **not** cite 34%, 38%, 15/4/5, or 46% as the headline. The 46% remains reportable only as the *seed-corpus* (n=24) figure.

## 6. Remaining steps to finalize (hand-off)

1. Human Raters 2 & 3 code `human_worksheet_44_BLINDED.csv` independently (frozen codebook v2, blinded).
2. Merge with existing labels; run `compute_kappa.py` for combined Cohen's/Fleiss κ + adjudicate disagreements (priority: the 8 `FLAG` rows and every invisible-channel call, esp. 14765 which may cascade to visible).
3. Recompute the invisible fraction + Wilson CI on the final human-adjudicated n≈68–70.
4. Propagate the single reconciled number into the manuscript (abstract, RQ1) and the artifact metadata. Replace every stale 26/38% and remove roadmap 34%/15-4-5.
5. Update `MINING_STATUS.md` with the closed number and archive this memo.

## 7. Files produced
- `provisional_llm_labels_44.csv` — auxiliary LLM_R4 codes for the 44 new PRs (not headline IRR).
- `human_worksheet_44_BLINDED.csv` — blinded worksheet for human Raters 2 & 3.
- `RECONCILIATION_70.md` — this memo.
