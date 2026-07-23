# Adjudication log — 44-row worksheet

Status: proposed codebook-consistent calls, pending explicit R2 confirmation.

- PR #14655: `output_semantic`, observable `yes` — The issue concerns incorrect inverse cancellation that can alter the circuit unitary, so it is output_semantic and observable.
- PR #14670: `output_semantic`, observable `yes` — Incorrect dirty-ancilla accounting can synthesize an incorrect MCX decomposition, so it is output_semantic and observable.
- PR #14765: `output_semantic`, observable `yes` — Although this is Target-query plumbing, it feeds gate-direction decisions and can surface in the emitted circuit; classify as output_semantic (low confidence).
- PR #15074: `compilation_failure`, observable `yes` — Pickling SabreSwap fails as a crash during a supported workflow, so it is compilation_failure and observable.
- PR #15131: `circuit_quality`, observable `yes` — The affected decomposition remains valid but can be a poorer target-compatible choice, so classify as circuit_quality and observable.
- PR #15286: `output_semantic`, observable `yes` — Selecting the wrong unitary-synthesis path for the Target can yield an incorrect emitted decomposition, so it is output_semantic and observable.
- PR #15933: `compilation_failure`, observable `yes` — Oversized matrix input previously caused a panic, so Rule 1 assigns compilation_failure and it is observable.
- PR #16075: `compilation_failure`, observable `yes` — An incomplete basis leaves the decomposer unavailable and causes a crash, so it is compilation_failure and observable.
- PR #16151: `compilation_failure`, observable `yes` — The reported barrier-handling defect is a ConstrainedReschedule failure, so it is compilation_failure and observable.
- PR #16392: `output_semantic`, observable `yes` — A stale global cache can return inconsistent or incorrect synthesized output, so it is output_semantic and observable.
