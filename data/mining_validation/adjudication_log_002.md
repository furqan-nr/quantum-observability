# Adjudication log — Batch 002 (36 fixes; R1 author + R2 independent coder)

Reliability **before** adjudication: Cohen's kappa = **0.929** (binary observable), **0.962**
(7-way channel), 97.2% raw agreement, n = 36. Channel disagreements: **1 of 36**
(PR #11351), which was also the single binary (visible/invisible) disagreement.

Both raters coded independently and blind: R1 = Furqan Nasir (author), R2 = Muhammad Atif Saeed
(the same independent coder as R2 for the 68-fix corpus and the tket/Cirq cross-SDK sets; see
declarations/Coder_Declaration_Atif.pdf), against the frozen `CODEBOOK_v2_FROZEN.md`. R1 and R2
files are distinct (different notes wording on every row), and R2 never saw R1's labels.
Note: Atif's on-file declaration (dated 2026-07-25) predates this round and does not yet tick a
batch-002 box; a short addendum confirming this round would close that gap (author action).

## The single disagreement

- **#11351** (Don't substitute ideal gates in target with Optimize1qGatesDecomposition):
  R1 `circuit_quality` / yes (high) vs R2 `contract_metadata` / no (low) →
  AGREED **`contract_metadata` / no**.

  **Resolution basis: primary source (PR diff + release note).** The fix adds a guard so the pass
  defers to the circuit's existing gate when the candidate resynthesis has the **same error and the
  same gate count**; the added test asserts the output circuit is unchanged. The pre-fix bug was
  therefore an *equivalent, same-count* gate substitution — no extra gates, no added depth, identical
  unitary — which an output-equivalence oracle (modulo global phase and qubit permutation) cannot
  see. Under codebook **Rule 3** (quality-vs-metadata decisive test) this is `contract_metadata`
  (observable = no), not `circuit_quality`. R1's original premise ("adding avoidable translated
  gates") does not hold on the diff, since the gate count is unchanged. R1 revised to
  `contract_metadata`, which matches R2's original label.

  Provenance note: the diff was retrieved and codebook Rule 3 applied with assistant support; the
  resolution was reviewed and accepted by R1 (author). R2 already held this label independently, so
  the adjudicated label is the R2 label confirmed by source evidence.

## Effect on the headline

- Batch-002 output-invisible: **10 / 36 = 27.8%**.
- Merged analytic corpus: **29 / 104 = 27.9%** output-invisible, Wilson 95% CI **[20–37%]**
  (was 19/68 = 27.9% [19–40%]; the point estimate is unchanged and the interval tightens with n).

Per-row detail: `adjudication_002.csv`. Merged labels: `labels_final_104.csv`.
