# RQ1.4 independent recoding of the 19 equivalence-invisible fixes — results (2026-09-08)

## What this is

`INSTRUCTIONS_FOR_CODER.md` and `invisible19_worksheet_BLINDED.csv` were sent to a second, independent
coder to re-assign the fault-mechanism category (the same 11 categories used in Table 6 / §5.5) for all
19 equivalence-invisible fixes, working from each PR's actual diff rather than its title, and blinded to
the existing single-coder labels. This is a full recoding of the exact subset the paper's Discussion
(§6) leans on, not a random spot-check mixing visible and invisible fixes (that was the earlier,
title-level check reported in `../rq14_spotcheck/`, κ = 0.41).

## Result

Comparing the second coder's 19 labels (`invisible19_worksheet_COMPLETED.csv`) against the existing
diff-verified labels (`invisible19_answer_key_DO_NOT_SEND.csv`):

| Metric | Value |
|---|---|
| n | 19 |
| Raw agreement | 17/19 = 89.5% |
| Cohen's kappa | **0.87 (almost-perfect, Landis & Koch 1977)** |

This is a materially stronger result than the earlier title-level spot-check (κ = 0.41) and is now
comparable to the paper's other reliability figures (channel taxonomy: κ 0.67–0.86; cross-SDK: κ
0.52–0.77).

## The two disagreements, adjudicated against the actual GitHub diff

**#14603 (`Fix ElidePermutations pass in the presence of PermutationGates`).** Original label:
`rust_port_metadata_loss`. Second coder: `logic_error_pass_specific`. Fetched the PR directly
(https://github.com/Qiskit/qiskit/pull/14603): the PR's own description and diff describe correcting
`ElidePermutations`'s internal permutation-update rule (`M[Q[i]] ← M[Q[P[i]]]`) — nothing in the PR's own
text or diff mentions a Rust port. The second coder's `logic_error_pass_specific` call is an accurate
read of what this PR's diff alone shows. The original `rust_port_metadata_loss` label instead rests on
separate, independently verified git archaeology tracing the *root cause* to an earlier commit
(`cbb4d5d5`, "Port ElidePermutations to Rust #13094") that the coding instructions did not ask anyone to
go looking for. **Adjudication: kept as `rust_port_metadata_loss`**, for the reason external to this PR's
own diff (this is the same documented exception the earlier title-level spot-check hit on this identical
item — see `../rq14_spotcheck/SPOTCHECK_RESULTS.md`). This is a scope difference between "what this
fix's diff shows" and "what the verified introducing commit was," not an error by either coder.

**#14939 (`Fix TranspileLayout.initial_index_layout with unordered virtuals`).** Original label:
`logic_error_pass_specific`. Second coder: `cross_representation_conversion`. Fetched the PR diff
directly (https://github.com/Qiskit/qiskit/pull/14939/files): the bug is that `enumerate(virtual_map.
items())`'s loop-position was used as if it were the qubit's actual input index; the fix replaces it with
a real lookup, `self.input_qubit_mapping[virt]`. This is a single function operating on one data
structure at a time — no second internal representation (e.g. a different pass's convention, a
Rust/Python boundary) is actually being converted into, which `cross_representation_conversion` requires
by its own definition. **Adjudication: kept as `logic_error_pass_specific`.** The second coder's read
was reasonable and specific, but the category boundary, applied strictly, favors the original label here.

## Net effect on the manuscript

**No category counts change.** Both disagreements were adjudicated toward the original label, so Table
6, the contract/metadata 60% figure (§5.5), and the representation-boundary discussion (§6) are
unchanged in substance. What changes is that this pattern — previously flagged as resting on a
single-coder pass with no independent check — now carries an almost-perfect independent-agreement figure
(κ = 0.87) on exactly the subset it depends on. `build_1a.js` §5.5 and §6 updated accordingly
(2026-09-08).

## Credit

The second coder is Muhammad Sajjad Saleem, the same R3 volunteer already introduced in §4.4-4.5 of the
manuscript (full-corpus channel-taxonomy third coding, and the earlier title-level RQ1.4 spot-check in
`../rq14_spotcheck/`). Credited in the Acknowledgements section (not Author Contributions, consistent
with how R2/R3 are credited elsewhere in this paper); `build_1a.js`'s Acknowledgements section reference
range extended from "(§4.4-4.5)" to "(§4.4-4.5, §5.5)" to cover this contribution (2026-09-08).

**Note on reusing the same volunteer as the earlier, weaker spot-check.** The earlier title-level
spot-check (`../rq14_spotcheck/SPOTCHECK_RESULTS.md`, κ = 0.41) was done by this same person under time
pressure — he told us at the time that he might not have gotten every call right, which the paper's own
methodology notes already treat as a legitimate reason the title-level check underperforms the channel
taxonomy's other reliability figures. This round, he had adequate time and worked from each PR's actual
diff rather than its title, per the same instructions given to any coder (`INSTRUCTIONS_FOR_CODER.md`).
The jump from κ = 0.41 to κ = 0.87 is attributable to those two changes (time, diff-level protocol), not
to reduced independence: he was blinded to the existing labels exactly as before, and the two disagreements
that did occur were resolved by checking the diff itself, not by deferring to either coder. Reusing an
already-trained, already-declared volunteer (declaration on file: `declarations/Coder_Declaration_
Sajjad.pdf`) who already knows the codebook is a normal efficiency choice, not a validity concern, given
that blinding protocol.
