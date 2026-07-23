# Adjudication log — the 44-fix batch (R1 author + R2 friend)

Reliability before adjudication: Cohen's kappa = 0.86 (binary observability), 95.5% raw agreement,
n = 44. Channel disagreements: 10 of 44. Only 2 touched the binary observable/invisible judgment.
All 10 resolved to the OBSERVABLE side, so the output-invisible count for the batch is 8/44 and the
full-corpus headline is 19/68 = 28% [Wilson 95% CI 19-40%].

## Binary-critical disagreements (the only two that could move the headline)
- **#14765** (Target.py_instruction_supported): R1 output_semantic vs R2 contract_metadata ->
  AGREED **output_semantic** (observable). Wrong-qargs support result feeds GateDirection; a gate left
  in an unsupported direction/qargs is catchable by a target-compliance/equivalence check. Codebook
  Rule 5 (edge-of-scope plumbing), low confidence. Not output-invisible.
- **#15074** (pickle SabreSwap): R1 compilation_failure vs R2 contract_metadata ->
  AGREED **compilation_failure** (observable). Pickling raised an exception (crash); Rule 5 -> crash
  goes to compilation_failure. Not output-invisible.

## Observable-vs-observable disagreements (do not affect the 28%, only the channel breakdown)
- #14655 -> output_semantic;  #14670 -> output_semantic;  #15131 -> circuit_quality;
  #15286 -> output_semantic  (human-adjudicated from the coded sheets).
- #15933 -> compilation_failure;  #16075 -> compilation_failure;  #16151 -> compilation_failure;
  #16392 -> output_semantic  (resolved per frozen codebook; these four were dropped from the
  truncated save and are pending a quick R2 confirm - no headline impact either way).

Per-row detail with reasons: `adjudication_44.csv`.
