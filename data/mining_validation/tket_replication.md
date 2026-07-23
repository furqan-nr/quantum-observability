# N3 — cross-SDK replication on tket (provisional first pass)

**Question:** does the output-invisible rate (Qiskit ~28% [19–40%], n=68) replicate on another quantum
compiler? **Answer (provisional): yes.**

## Method
`scripts/mine_sdk.py` blobless-cloned CQCL/tket and harvested merged BUG-FIX commits touching the
compilation passes (Mapping, Placement, Transformations, Predicates, Converters, ArchAwareSynth,
Clifford, PauliGraph, Diagonalisation, Circuit). 24 candidates; 4 excluded as out-of-scope (WASM,
serialisation, get_statevector/simulation, QASM I/O plumbing) → **n = 20 in-scope**. Each coded
provisionally against the SAME frozen codebook used for Qiskit (auxiliary LLM_R4 pass; NOT human IRR).

## Result
- **Output-invisible: 5/20 = 25% [Wilson 95% CI 11–47%]** — overlaps the Qiskit ~28% [19–40%].
- Channel mix (in-scope 20): output_semantic 9, compilation_failure 5, **contract_metadata 5**,
  performance 1, determinism 0, global_phase 0.
- All 5 invisible fixes are **contract/permutation-metadata** faults, e.g.:
  - #2072 GreedyPauliSimp ignores the circuit's implicit qubit permutation
  - #146 no wire-swap (implicit permutation) handling in phase-poly-box creation
  - #1632 symbol substitution doesn't preserve opgroup annotation
  - #1441 FlattenRelabelRegisters register-metadata fix; #285 single-qubit placement labelling

## Honest caveats
- n = 20 is small → wide CI; provisional LLM codes, several borderline (flagged), **pending human
  triple-coding** as for the Qiskit corpus.
- The invisible MIX differs from Qiskit: tket's invisible faults here are permutation/metadata-dominated
  with **no global-phase or determinism** cases in this sample (tket tracks global phase differently;
  larger n may surface them). Report this difference, don't hide it.

## Significance for the paper
The observability gap is **not Qiskit-specific** — it appears on a structurally different compiler at a
comparable rate, dominated by the same permutation/contract-metadata channel. This is the field-level
generalization that strengthens a flagship (Q1) submission. Next: broaden the harvest, human-code the
sample, and optionally add Cirq as a third point.

---

## Three-SDK picture (provisional; add cirq)

| SDK | invisible / in-scope | rate | Wilson 95% CI | note |
|-----|----------------------|------|---------------|------|
| Qiskit | 19/68 | 28% | 19–40% | full study (24 human-adjudicated + 44 provisional) |
| tket   |  5/20 | 25% | 11–47% | strong replication; permutation/contract-metadata dominant |
| Cirq   |  1/10 | 10% | 2–40%  | weaker/noisier; see interpretation |

**Cirq harvest:** 34 candidates, but 24 were housekeeping (ruff/mypy/typos/coverage) leaving only
n=10 genuine transformer bug-fixes. Conservative coding gives 1/10 invisible (a merge_moments
empty-moment structural fix); 2–3 borderline structural/ordering cases (align_right order,
drop_diagonal context) could raise it to ~20–30%.

**Honest interpretation (this is the defensible claim):** the output-invisible gap **replicates
strongly on tket** (25% ≈ Qiskit 28%), a compiler architecturally close to Qiskit with explicit
layout/routing/permutation-metadata contracts. On **Cirq** — a leaner moment-based model that exposes
far fewer such metadata contracts — the rate is lower and the estimate noisy (n=10). This suggests the
phenomenon's *magnitude scales with how much layout/permutation/metadata contract a compiler exposes*,
which is a more nuanced and credible claim than a uniform rate. The invisible channel is real and
cross-compiler; its prevalence is architecture-dependent. All three are provisional pending human
coding; the CIs overlap.
