# RQ1.4 independent recoding of the 19 equivalence-invisible fixes — instructions

## What this is

Paper 1A classifies 68 merged Qiskit transpiler bug-fixes by two things: (1) which correctness
*channel* the fault falls in (already independently dual-coded and adjudicated — not what this
worksheet is about), and (2) for a secondary, exploratory question, what *fault mechanism* recurs
among the fixes (one of 11 categories below). The mechanism coding was done by a single coder and
verified against each fix's own source diff, but never independently coded by a second person at
diff level. This worksheet is that missing independent pass, restricted to the 19 fixes the paper
calls "equivalence-invisible" (the ones an output-equivalence oracle cannot see), because that is
the subset the paper's Discussion (§6, §5.5) actually leans on.

This is expected to take roughly 60–90 minutes for 19 items, since it asks you to read each PR's
actual code diff, not just its title.

## What to do

1. Open `invisible19_worksheet_BLINDED.csv`. For each row you have the PR number, a GitHub link, and
   its title. You do **not** have any existing category assignment, channel, or evidence note — this
   is deliberate, so your coding is independent.
2. Open each PR link and read the **Files changed / diff tab**, not just the title and description.
   The category should follow from what the code actually does, not from how the PR is titled (titles
   are sometimes imprecise or incomplete — that is exactly what this check is meant to catch).
3. Assign exactly **one** category from the list below to `your_mechanism_category`.
4. Fill `your_confidence` (high / med / low).
5. Fill `your_diff_evidence` with one or two sentences citing the specific file, function, or code
   change that justifies your category choice — not a restatement of the title. This is the field
   that makes your coding checkable against the diff, the same standard the original coding was held
   to.
6. Do this for all 19 rows before comparing notes with anyone or looking at any other coding of these
   PRs.
7. Save and send the completed CSV back. You do not need to compute agreement yourself — that will be
   done separately once your labels are in.

## The 11 categories (assign exactly one)

- **missing_validation_or_contract_check** — a precondition, edge case, or contract wasn't checked
  (e.g. empty input, missing backend, unvalidated target, idle/disjoint qubits) and the fix adds that
  check.
- **unchecked_numeric_edge_case** — a crash/panic on malformed or boundary-value numeric/shape input
  (mostly Rust-side panics), and the fix adds bounds/shape handling.
- **control_flow_gap** — the bug is specifically about handling `ControlFlowOp` / loops / if-else /
  switch structures; the fix repairs that handling.
- **cross_representation_conversion** — something (metadata, state, an attribute) was lost or
  corrupted when converting between two internal representations (e.g. a Python object into a Rust
  struct, one pass's layout convention composed into another's).
- **commutation_checker_defect** — the bug is specifically in `CommutationChecker`'s correctness logic
  (wrongly decides two gates commute, or don't).
- **global_phase_bookkeeping** — global phase wasn't correctly tracked, propagated, or composed
  through a transformation that should have preserved or updated it.
- **nondeterministic_ordering** — output varies across runs with a fixed seed because of unordered
  iteration, hashing, or similar.
- **stateful_reuse_or_global_cache** — a pass instance or a cache incorrectly retains state across
  calls or across incompatible settings.
- **api_plumbing_or_serialization** — the issue is about pickling, deepcopy, delegation, or another
  API surface concern, not compiler semantics per se.
- **logic_error_pass_specific** — a genuine bug in a specific pass's logic that doesn't fit any
  category above and doesn't look like part of a broader recurring pattern. Use this as the default
  only when nothing more specific applies — do not use it just because a case is hard; if you're
  unsure between this and a more specific category, say so in your notes and pick the more specific
  one when the diff supports it.
- **rust_port_metadata_loss** — the diff (or its linked issue/commit history) shows the bug was
  introduced by porting or rewriting a pass from Python to Rust, and metadata was dropped in that
  port. Only use this if the diff or its history actually shows this, not because the file is `.rs`.

If two categories seem to fit, pick the one the diff itself most directly supports as the root cause,
and explain the tension in `your_diff_evidence` — that is useful signal, not a mistake.

## Why diff-level, not title-level, this time

An earlier, separate spot-check of a mixed 19-item sample (10 of these same fixes plus 9 unrelated
ones) was done at title level and produced only moderate agreement (Cohen's κ = 0.41) with the
original coding. When every item was subsequently checked against the actual PR diff, several
categories changed from what the title suggested. This worksheet is deliberately diff-level from the
start so the resulting agreement figure is comparable to the standard the paper's own numbers are
held to, not a repeat of the weaker title-based check.

## What we'll do with your answers

We'll compute Cohen's kappa between your 19 labels and the existing single-coder, diff-verified
labels, and adjudicate any disagreements against the diff itself (not by majority vote or by
deferring to either coder's seniority). The result — agreement figure, adjudicated labels, and any
category the adjudication changes — will be reported in the paper's RQ1.4 section in place of the
current single-coder framing, with your role credited per the paper's Acknowledgements / Author
Contributions conventions (tell us how you'd like to be credited if this goes forward).
