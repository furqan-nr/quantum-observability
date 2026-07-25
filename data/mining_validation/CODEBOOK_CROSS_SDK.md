# Cross-SDK codebook mapping (tket, Cirq) — companion to CODEBOOK_v2_FROZEN.md

The Qiskit codebook (7 manifestation channels; binary observability) applies unchanged in principle.
This note fixes the **scope gate** and the **channel mapping** so tket/Cirq are coded consistently with
Qiskit. Observability rule is identical: **output-invisible = {contract_metadata, determinism,
global_phase}**; everything else is output-observable.

## Scope gate (in_scope_bugfix = yes only if ALL hold)
1. It is a **merged bug-fix** (not a feature, refactor, or perf-only cleanup unless the perf itself is
   the fault).
2. It fixes a **compilation/transpilation pass** (routing, placement/layout, synthesis/rebase,
   optimisation, scheduling, predicates that gate compilation).
3. It is **not** docs/typo, lint/format (ruff, clang-format, black), CI/coverage/infra, type-checking
   (mypy/numpy-typing), pure serialisation/QASM I/O, or simulation (statevector/unitary sim).
   (Cirq's transformer history is dominated by these — exclude them.)

## Channel mapping
| Channel (Qiskit) | tket analogue | Cirq analogue | observable? |
|---|---|---|:--:|
| output_semantic | wrong compiled unitary/measured output (bad cancellation, wrong control, wrong rebase) | same | yes |
| compilation_failure | crash/segfault/exception/rejected input during compile | same | yes |
| circuit_quality | correct but worse (more 2q gates/depth) | same | yes |
| performance | slower/more memory only | same | yes |
| **contract_metadata** | corrupted layout/permutation/qubit-mapping metadata while applied output is correct: **implicit qubit permutation dropped, wire-swap not tracked, register/opgroup annotation lost, placement labelling incomplete** | moment-structure/qubit-order bookkeeping with output unitary intact (rarer — Cirq exposes fewer such contracts) | **no** |
| **determinism** | non-deterministic compile under a fixed seed | same | **no** |
| **global_phase** | dropped/altered global phase (invisible mod global phase) | same | **no** |

## SDK-specific borderline rules
- **tket** exposes explicit routing/placement/permutation contracts like Qiskit → the contract_metadata
  channel is well-populated (implicit permutation, wire-swap, opgroup, register-flatten are the H1/#14919
  analogues; code as contract_metadata/no).
- **Cirq** is moment-based with few explicit layout/permutation contracts. "Empty-moment / moment-order
  bookkeeping fixes where the output unitary is unchanged" → contract_metadata/no (structural metadata);
  but if op ordering can change semantics (non-commuting ops), code output_semantic/yes. Flag low
  confidence and record reasoning.
- A **predicate/verifier** that wrongly raises on a valid circuit manifests as a rejection →
  compilation_failure/yes (visible), not contract_metadata.

## Rating protocol
Code the blinded worksheets (`{tket,cirq}_worksheet_BLINDED.csv`) independently (>=2 human raters,
your own judgement), fill in_scope_bugfix / manifestation_channel / observable / confidence, adjudicate
disagreements against this note, then run `scripts/score_worksheet.py <file>` (add `--rater2 <file2>`
for Cohen's kappa). Report the pre-adjudication kappa as the reliability, mirroring the Qiskit corpus.
