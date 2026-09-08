# RQ1.4 spot-check — instructions (should take about 30-45 minutes)

## What this is

We coded 68 Qiskit transpiler bug-fixes by "what kind of fault this is" (a fault-mechanism category),
separately from the existing channel taxonomy you may have coded before. This was done by one person in
a single pass, so it needs an independent check before it can be reported as a reliable finding rather
than just one person's read. This worksheet is that check, on a sample of 19 of the 68 (not all of
them — we're keeping this short given your time).

## What to do

1. Open `spotcheck_worksheet_BLINDED.csv`. For each row you have the PR number, a link, and its title.
2. Open the PR link and read the title and description (and the linked issue, if any). You do not need
   to read the code diff unless the description is unclear.
3. Assign exactly **one** category from the list below to the `your_mechanism_category` column.
4. Fill `your_confidence` (high / med / low) and a one-line `your_notes` explaining your call, especially
   if confidence is low.
5. Do not discuss this with anyone else or look at any other coding of these PRs before you finish all 19.
6. Save and send the file back. That's it — there's a separate answer key on our side; you don't need to
   see it or compute anything.

## The 11 categories (assign exactly one)

- **missing_validation_or_contract_check** — a precondition, edge case, or contract wasn't checked
  (e.g. empty input, missing backend, unvalidated target) and the fix adds that check.
- **unchecked_numeric_edge_case** — a crash/panic on malformed or boundary-value numeric/shape input
  (mostly Rust-side panics), and the fix adds bounds/shape handling.
- **control_flow_gap** — the bug is specifically about handling `ControlFlowOp` / loops / if-else /
  switch structures; the fix repairs that handling.
- **cross_representation_conversion** — something (metadata, state, an attribute) was lost or corrupted
  when converting between two internal representations (e.g. a Python object into a Rust struct, one
  pass's layout convention composed into another's).
- **commutation_checker_defect** — the bug is specifically in `CommutationChecker`'s correctness logic
  (wrongly decides two gates commute, or don't).
- **global_phase_bookkeeping** — global phase wasn't correctly tracked/propagated through a
  transformation that should have preserved or updated it.
- **nondeterministic_ordering** — output varies across runs with a fixed seed because of unordered
  iteration, hashing, or similar.
- **stateful_reuse_or_global_cache** — a pass instance or a cache incorrectly retains state across calls
  or across incompatible settings.
- **api_plumbing_or_serialization** — the issue is about pickling, deepcopy, delegation, or another API
  surface concern, not compiler semantics per se.
- **logic_error_pass_specific** — a genuine bug in a specific pass's logic that doesn't fit any category
  above and doesn't look like part of a broader recurring pattern.
- **rust_port_metadata_loss** — the fix's own description explicitly says the bug was introduced by
  porting/rewriting a pass from Python to Rust and metadata was dropped in that port. (You'll likely
  only use this if the PR text itself says so explicitly — don't infer a Rust port from general
  knowledge of the project.)

If two categories seem to fit, pick the one closer to what the fix's own description emphasizes as the
root cause, and say so in your notes — that's exactly the kind of disagreement we want to see, not a
sign you're doing it wrong.

## What we'll do with your answers

We compute agreement (Cohen's kappa) between your labels and the original single-pass coding on these
19 items. If it's low, that tells us the category scheme needs tightening before we report the finding
with confidence — which is useful information either way, not a failure state.

## One optional extra (2 minutes, skip if you're out of time)

A 20th item, `#8271` in **Cirq** (not Qiskit — a different corpus, see below), turned up in a fresh
mining pass and hasn't been coded by anyone yet: https://github.com/quantumlib/Cirq/pull/8271
("Fix flaky Shannon decomposition test"). If you have two extra minutes, code it the same way the
original Cirq worksheets were done (in-scope bug-fix? manifestation channel? observable by output
oracle?) — same categories as the main Qiskit codebook. This is a nice-to-have, not required.
