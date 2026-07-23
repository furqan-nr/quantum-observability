# Next 75 eligible-PR mining protocol

**Frozen-rule start date:** 2026-06-29  
**Analytic seed:** 25 eligible bug-fix PRs  
**Target:** collect and independently double-code **75 additional eligible PRs** to reach an analytic n=100.

> The earlier phrase “next 74+” assumed 26 eligible seed rows. PR 14120 is now excluded because it is a feature request, so the correct target is **75**, not 74.

## Files to use

- `CODEBOOK_v2_FROZEN.md` — the only classification rules for Batch 002.
- `batch_002_master_template.csv` — private master file; contains R1 and later R2/final columns.
- `batch_002_r2_blinded_template.csv` — the only file passed to R2. It intentionally has no R1 or final columns.
- `dual_rater_labels_analytic_seed.csv` — 25-row, scope-screened baseline.
- `compute_kappa_analytic.py` — agreement script for the analytic data only.

## 1. Mine candidates, then apply the eligibility screen

Use the existing mining sources in this order:

1. `is:pr is:merged label:"mod: transpiler" label:"Changelog: Bugfix"`
2. `is:pr is:merged label:"mod: transpiler" label:bug`
3. Qiskit 2.x release-note **Transpiler → Fixed** entries.
4. Pass-specific sweeps in layout, routing, basis/translation, optimization, scheduling, analysis, and pass-manager code.

For each candidate, populate only metadata plus `eligibility_status` in the master file:

- `include` only when the PR is a merged transpiler **bug fix**.
- `exclude_not_bugfix` for a feature/enhancement/refactor/docs/test-only item.
- `exclude_out_of_scope` for non-transpiler scope.
- Record one concrete evidence URL for every exclusion.

Deduplicate by `fix_pr`. Gather about **90 candidates** so that you still have 75 eligible items after screening.

## 2. Work in three sealed batches of 25

For each batch:

1. Fill PR metadata and R1 labels in the private master file using the frozen codebook.
2. Copy only metadata/evidence fields into the R2 blinded file. Do **not** include any R1 labels, final labels, adjudication history, prior kappa, or Mistral labels.
3. Have R2 complete `manifestation_channel`, `observable_by_output_oracle`, confidence, and notes against the same frozen codebook.
4. Merge R2 results back into the master only after R2 has completed all 25 rows.
5. Auto-fill final fields only when R1 and R2 agree. Record each disagreement; do not alter either raw rating.
6. Run kappa. You may adjudicate after the batch is sealed, but **do not change the codebook** or show adjudications to the next independent rater.

## 3. Compute agreement

For the seed baseline:

```bash
python3 compute_kappa_analytic.py
```

For the full 100-row analytic corpus after combining the 25 seed and 75 new eligible PRs:

```bash
python3 compute_kappa_analytic.py --input dual_rater_labels_analytic_full.csv
```

Current scope-screened seed baseline (R1 vs ChatGPT R2 raw labels, n=25):

| Judgment | Raw agreement | Cohen's kappa | Bootstrap 95% CI |
|---|---:|---:|---:|
| Binary observability | 84.0% | 0.667 | [0.333, 0.920] |
| 7-class channel | 72.0% | 0.646 | [0.406, 0.845] |

## 4. Lock down reproducibility

Record the model name/version, date, exact prompt, temperature (or “default”), source-evidence bundle, and whether the rater saw any prior labels. Use the same frozen codebook and rater prompt for all new rows.

Mistral remains a **third LLM-assisted audit pass**. It must not replace raw R2 labels after you have seen agreement scores. Use it only on a pre-declared random audit subset or on sealed disagreements, and report it separately.

## 5. Stop condition

Stop mining only when all are true:

- at least 100 **eligible** bug-fix PRs are double-coded;
- raw R1/R2 labels are preserved;
- all disagreements have an adjudication record;
- kappa and bootstrap confidence intervals are recomputed on the scope-screened analytic file;
- the final paper reports the output-invisible fraction with its confidence interval.
