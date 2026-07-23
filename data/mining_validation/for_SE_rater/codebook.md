# Mining classification codebook, transpiler-fix manifestation channels

This codebook governs the independent classification of merged Qiskit transpiler
bug-fix pull requests (label `mod: transpiler`) used in the observability study.
A second rater should classify **independently**, using only the PR title,
description, and linked issues, **without** seeing Rater 1's labels.

## Two judgments per PR

### 1. `manifestation_channel`, the channel through which the fixed fault could be detected
Assign exactly one:

- **output_semantic**, the bug makes the compiled circuit compute a *different
  unitary / different measured output* (e.g. unsafe cancellation, wrong commutation,
  wrong control modifiers, wrong routing of control flow).
- **compilation_failure**, the bug causes a crash, exception, panic, or rejected
  input during transpilation (functional failure), rather than a wrong output.
- **circuit_quality**, the output is semantically correct but *worse* (more 2-qubit
  gates, larger depth, worse layout), a quality regression, not a correctness one.
- **performance**, the bug only affects *compile-time cost* (slower or more memory),
  output and quality unchanged.
- **contract_metadata**, the bug corrupts an internal transpiler **contract or
  metadata** property (e.g. `TranspileLayout`, `final_layout`,
  `virtual_permutation_layout`, `routing_permutation`, circuit `name`) while the
  *layout-applied output unitary remains correct*.
- **determinism**, the bug makes output **non-deterministic** across fixed-seed runs
  (same input, varying result), without a single run being "wrong".
- **global_phase**, the bug drops/alters the **global phase**, which is invisible to
  any equivalence check performed *modulo global phase*.

### 2. `observable_by_output_oracle`, yes / no
Answer **the headline question**: *Could a black-box output-equivalence oracle that
compares the compiled circuit's output map, modulo global phase and modulo qubit-layout
permutation, detect this fault?*

- **yes**, output_semantic, compilation_failure, circuit_quality, performance
  (a wrong/absent output, a crash, a measurably worse circuit, or a measurable slowdown
  are all observable in principle).
- **no**, contract_metadata, determinism, global_phase
  (these leave the layout-applied output map intact, so an output-only oracle cannot see
  them). This **`no` set is the study's key quantity** (output-invisible channels).

## `confidence`, high / medium / low
- **high**, title/description make the channel unambiguous.
- **medium**, channel is clear but some interpretation is needed.
- **low**, genuinely borderline (e.g. an enhancement vs. a fix, or a metadata-vs-quality
  ambiguity); record the reasoning in `notes`.

## Borderline rules (decide consistently)
- A metadata property is corrupted **but** the applied output could differ →
  prefer `contract_metadata` only if the *layout-applied output unitary is correct*;
  otherwise `output_semantic`.
- API/serialization plumbing fixes at the edge of transpiler scope → `compilation_failure`
  if they manifest as a crash; `contract_metadata` if they only affect a property; mark
  `low` confidence.
- "Idle/uncoupled qubit" layout fixes → `circuit_quality` if they change layout quality,
  `compilation_failure` if they cause an edge-case crash.

## Output
Fill `data/mining_validation/rater2_sheet.csv` (channel, observable, confidence, notes),
then run `compute_kappa.py` to obtain Cohen's kappa on both judgments. Reconcile any
disagreements in a short adjudication note and report the agreed labels plus kappa.

---

## Version 2 — tightened borderline rules (2026-06-29)

`version: 2` · `frozen: true` · `frozen_on: 2026-06-29`  
No classification-rule changes are permitted until the next 75 eligible PRs have completed independent R1/R2 coding and their raw labels have been sealed.

These sharpen the three boundaries that caused every channel disagreement in the n=26 seed set
(PRs 15258, 14938, 14667, 14041, 13874, 13820, 14603). Apply them top-to-bottom; the first rule
that matches wins.

1. **Crash vs wrong-output (compilation_failure vs output_semantic).** If transpilation raises /
   panics / rejects input on the trigger -> `compilation_failure`, regardless of any wrong output it
   *would* have produced. Only if transpilation completes and returns a circuit whose layout-applied
   unitary is wrong -> `output_semantic`. (Resolves 15258, 13820.)

2. **Quality vs performance (circuit_quality vs performance).** If the *output circuit* is worse
   (more 2q gates, more depth, worse layout) -> `circuit_quality`. If the output circuit is identical
   and only *compile time / memory* changed -> `performance`. A pass that does redundant work but
   emits the same circuit is `performance`, not quality. (For a PR with multiple trigger paths, record secondary behavior in notes; a documented crash/rejection takes precedence under Rule 1, as in the final 14667 decision.)

3. **Quality vs metadata (circuit_quality vs contract_metadata).** Decisive test: *would a
   black-box output-equivalence oracle, comparing the layout-applied output modulo global phase and
   qubit permutation, see any difference?* If yes (the applied circuit is measurably worse) ->
   `circuit_quality` (observable=yes). If no (the applied output map is correct and only an internal
   property/metadata field is wrong) -> `contract_metadata` (observable=no). (Applied to 14938; 13874 instead had direct non-equivalence evidence and was classified `output_semantic`.)

4. **Quality/semantic vs metadata when the output is correct.** If the layout-applied output is
   correct but `TranspileLayout` / `final_layout` / `final_index_layout` / `routing_permutation` /
   circuit `name` is corrupted -> `contract_metadata`/no. (Confirms 14603 = H1.)

5. **Edge-of-scope plumbing (serialization, deepcopy/pickle, framework dunder).** If it manifests
   as a crash -> `compilation_failure`; if it only corrupts a property -> `contract_metadata`;
   mark `low` confidence and record reasoning. (Flags 14041 for author adjudication.)

**Headline reminder:** the `observable_by_output_oracle = no` set = {contract_metadata, determinism,
global_phase}. These three are the output-invisible channels and the study's key quantity.
---

## Freeze record

**Status:** frozen after seed-corpus adjudication on 2026-06-29.

The following are calibration outcomes, not additional categories: documented panic/exception/rejection
takes priority (`compilation_failure`); direct circuit non-equivalence is `output_semantic`; intact
layout-applied behavior with a broken layout/representation property is `contract_metadata`; and
identical emitted circuits with only added compile-time work are `performance`.

**Single-label handling for multiple trigger paths:** use the first matching rule in the ordered
borderline rules above, and record other documented manifestations in `notes`. Do not change this
precedence rule during Batch 002.

**Scope gate before classification:** include only a merged Qiskit transpiler **bug-fix** PR. Exclude
feature requests, enhancements, documentation-only changes, refactors, and pure test/maintenance work.
Record every exclusion with an evidence URL and reason. PR 14120 is excluded from the analytic corpus
under this gate.

**Blinding rule:** Rater 2 receives this frozen codebook plus PR metadata and source evidence, but never
Rater 1 labels, final labels, adjudication notes, seed kappa values, or third-rater labels.

