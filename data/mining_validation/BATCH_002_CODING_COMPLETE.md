# Batch 002 — dual coding complete (2026-09-06)

The 36 eligible batch-002 transpiler bug-fixes are now dual-coded, adjudicated, and merged into the
analytic corpus, taking it from **68 → 104**.

## Reliability
- Cohen's kappa (binary observable): **0.929**
- Cohen's kappa (7-way channel): **0.962**
- Raw agreement: 35/36 = 97.2%
- Disagreements: 1 (#11351), resolved to `contract_metadata` / no — see `adjudication_log_002.md`.

## Prevalence
- Batch-002 output-invisible: **10/36 = 27.8%**
- Merged corpus (n=104): **29/104 = 27.9%**, Wilson 95% CI **[20–37%]**
  (n=68 was 19/68 = 27.9% [19–40%]; point estimate unchanged, interval tightened).

Combined channel breakdown (n=104): compilation_failure 40, output_semantic 24,
contract_metadata 15, circuit_quality 9, determinism 8, global_phase 6, performance 2.
Output-invisible set = contract_metadata + determinism + global_phase = 15 + 8 + 6 = 29.

## Provenance / files
- R1 (author, Furqan Nasir): `batch_002_r1_completed.csv`
- R2 (independent, blinded; Muhammad Atif Saeed — same R2 as the 68-fix corpus and the tket/Cirq
  cross-SDK sets, see declarations/Coder_Declaration_Atif.pdf): `batch_002_r2_completed.csv`. His
  on-file declaration predates this round and does not yet cover it; a short addendum would close
  that documentation gap (author action).
- Adjudication: `adjudication_002.csv`, `adjudication_log_002.md`
- Merged labels: `labels_final_104.csv`
- Codebook: `CODEBOOK_v2_FROZEN.md` (unchanged; frozen)

## Not yet done (author actions)
- Update the manuscript prevalence figures (§4.5 / §6.3 and abstract) from n=68 to n=104 if the
  larger corpus is to be the headline. Point estimate is unchanged (27.9%); the gain is a tighter CI
  and a larger, three-rater-consistent corpus.
- Decide whether to report a pooled κ across the seed + 44 + batch-002 batches, or per-batch κ.
