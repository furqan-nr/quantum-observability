# RQ1.4 mechanism-coding spot-check — results and adjudication (2026-09-04)

## SUPERSEDING UPDATE (2026-09-04, same day): full 68-item diff verification

Everything below this box describes the kappa spot-check and the **title-based** adjudication that
followed it. That adjudication was reasoned from PR titles/descriptions, not from the code itself, and
the user correctly challenged it ("what if coder 2 was wrong?"). In response, every one of the 68
mechanism-category assignments — not just the 19-item sample, not just the 10 disputed items — was
checked against the actual PR diff fetched from GitHub. Full per-item citations are in
`rq14_mechanism_coding_EVIDENCE_VERIFIED.csv`.

**Result: this evidence-checking process itself found the title-based adjudication wrong on several
items it had not flagged**, beyond the ones the spot-check disputed. Net result across all 68: 7 items
changed category on evidence, not 8 as the title-based pass had concluded, and not the same 8. Two
examples the adjudication missed entirely: `#14939` (adjudication kept it as
`cross_representation_conversion`; the diff shows a plain ordering bug in one function —
`logic_error_pass_specific`) and `#15685` (adjudication never flagged it; the diff shows a wrong
qubit-index range in one function, not a missing check). One example the earlier disputed-phase
diff-reading got right and the title-adjudication had gotten wrong by guessing: `#14597`, confirmed by
diff to be a local-vs-outer clbit-index bug (`cross_representation_conversion`), not a `control_flow_gap`
despite the PR title's wording.

**The `contract_metadata` headline figure, now fully evidence-grounded: 6/10 = 60%** are
representation- or port-boundary bugs (`cross_representation_conversion`: `#13910`, `#13945`, `#14919`,
`#15137` = 4; `rust_port_metadata_loss`: `#14603`, `#15024` = 2, both independently git-verified).
The other 4: `missing_validation_or_contract_check` (`#13833`, `#14938` — both genuinely unhandled
idle/disjoint-qubit cases, not representation bugs at all despite the original coding's guess),
`logic_error_pass_specific` (`#14939`), `api_plumbing_or_serialization` (`#14041`).

60% sits between the original unchecked claim (80%) and the title-based adjudicated claim (40%) — closer
to the former than the latter. This is the number the manuscript should report, together with the
process: single-coder open coding, third-coder spot-check (κ=0.41), then full-corpus verification against
actual PR diffs rather than descriptions. One corpus data-integrity issue was also found and flagged
(not fixed) in this pass: `#14869`'s title in the mining data does not match its own PR diff content —
see the CSV note on that row.

Full corpus-wide evidence-verified category totals (n=68): `missing_validation_or_contract_check` 15,
`logic_error_pass_specific` 9, `unchecked_numeric_edge_case` 9, `commutation_checker_defect` 7,
`control_flow_gap` 6, `cross_representation_conversion` 5, `global_phase_bookkeeping` 5,
`nondeterministic_ordering` 4, `api_plumbing_or_serialization` 3, `stateful_reuse_or_global_cache` 3,
`rust_port_metadata_loss` 2.

## What this is (original, kappa spot-check + title-based adjudication — kept for the reliability-methodology record)

`RQ14_MECHANISM_CODING_STATUS.md` flagged the original 68-item mechanism-category coding as
single-coder and exploratory, and recommended a 15-20 item spot-check by an independent third coder as
the cheapest upgrade path. That coder completed a 19-item blind worksheet
(`spotcheck_worksheet_BLINDED.csv` → `spotcheck_worksheet_COMPLETED.csv`), sampling all 10
`contract_metadata` items (the channel the manuscript's Discussion leans on) plus 9 more drawn at random
(`random.seed(42)`). This file reports that result plus the adjudication it triggered.

## Reliability result

Comparing the coder's 19 labels against the original single-pass coding
(`spotcheck_answer_key_DO_NOT_SEND.csv`):

| Metric | Value |
|---|---|
| n | 19 |
| Raw agreement | 9/19 = 47.4% |
| Expected agreement by chance (Pe) | 0.108 |
| **Cohen's kappa** | **0.410 (moderate, Landis & Koch 1977)** |
| Agreement on the `contract_metadata` subset (n=10) | 5/10 = 50% |

This is meaningfully below the paper's other reliability figures (channel taxonomy: κ 0.67-0.86 across
rounds; cross-SDK: κ 0.52-0.77). On the specific subset the Discussion's headline number depends on,
agreement was close to what an 11-category scheme would produce by chance.

**The disagreement was systematic, not noise.** Of the 19 items, the original coding used the catch-all
category `logic_error_pass_specific` once; the third coder used it ten times. In 9 of the 10 disputed
items, the coder chose that catch-all where the original coding had assigned a more specific category —
meaning the original single-pass coding was, on average, applying the specific categories more liberally
than an independent reader of the same PR text would.

## Adjudication

Rather than discard the finding or leave it at "unreliable," the 10 disagreements were adjudicated by
hand against one explicit, stated rule, applied uniformly:

> Assign a specific mechanism category only when the fix's own description names the qualifying pattern
> explicitly — a second representation or pass boundary being crossed, an explicit port/rewrite
> statement, an explicit panic/overflow/shape check, an explicit `ControlFlowOp`/loop, an explicit
> missing check being added, or an explicit cache/state-persistence bug. Otherwise, default to
> `logic_error_pass_specific`.

Outcome on the 10 disagreements: the coder's call was adopted on 7 items, my original call was kept on 2
(one of them, `#14603`, kept for a reason external to the disagreement — see below), and the coder's
*alternative* reading was adopted over both original options on 1 item (`#14597`, recoded to
`cross_representation_conversion` for a more precise reason than either coder's first instinct).

**`#14603` is a documented exception, not a normal adjudication.** It stays `rust_port_metadata_loss`
on the strength of git archaeology independently verified in prior work (introduced by `cbb4d5d5`, "Port
ElidePermutations to Rust #13094") — not because its PR text names a Rust port. The coder could not have
derived that from the PR text alone under the blind-coding instructions given to them, which is exactly
why they (correctly, given their information) called it `logic_error_pass_specific`. This exposed an
inconsistency in the original coding, not in the coder's judgment: the original pass used external
git-archaeology knowledge for this one item that the stated coding method did not license.

**Because the sample showed the original coding was systematically over-liberal with specific categories
— not just on the 10 disputed items — the same tightened rule was reapplied to all 68 items**, not only
the 19 sampled, for internal consistency. Full reasoning per item is in
`rq14_mechanism_coding_ADJUDICATED.csv`. Net effect: 8 of 68 items changed category (7 flips into
`logic_error_pass_specific`, 1 flip from `control_flow_gap` into `cross_representation_conversion`).

## Revised headline number

The manuscript's Discussion (§6) previously reported `contract_metadata` as 8/10 (80%)
`cross_representation_conversion` + `rust_port_metadata_loss` combined. After adjudication:

| | Original (single-pass) | Adjudicated |
|---|---|---|
| `cross_representation_conversion` in `contract_metadata` | 6 | 2 |
| `rust_port_metadata_loss` in `contract_metadata` | 2 | 2 |
| **Representation/port-boundary total** | **8/10 = 80%** | **4/10 = 40%** |

40% is still the largest identifiable pattern within `contract_metadata` (the next largest,
`logic_error_pass_specific`, is 5/10 — barely larger, and itself a catch-all rather than a positive
finding), and it still rests on the two independently git-verified cases (`#14603`, `#15024`) plus two
more where the fix text itself explicitly names a cross-representation composition (`#13945`, `#14919`).
That is a materially weaker but more defensible claim than the original 80%, and it is now the number the
manuscript should report.

## Full corpus-wide shift

| Category | Original n | Adjudicated n |
|---|---|---|
| `logic_error_pass_specific` | 8 | 15 |
| `missing_validation_or_contract_check` | 13 | 13 |
| `unchecked_numeric_edge_case` | 10 | 8 |
| `commutation_checker_defect` | 6 | 6 |
| `control_flow_gap` | 7 | 6 |
| `global_phase_bookkeeping` | 5 | 5 |
| `cross_representation_conversion` | 7 | 4 |
| `nondeterministic_ordering` | 4 | 4 |
| `api_plumbing_or_serialization` | 3 | 3 |
| `rust_port_metadata_loss` | 2 | 2 |
| `stateful_reuse_or_global_cache` | 3 | 2 |

`missing_validation_or_contract_check` (19%, unhandled edge cases) is now the largest *non-catch-all*
category, unchanged by adjudication — the sample gave no reason to doubt it, and one disputed item
(`#16151`) was adjudicated in its favor rather than against it.

## What this upgrades the finding to

Exploratory-with-a-reliability-check, honestly reported at κ=0.41, is a legitimate and common outcome
for open coding on a fine-grained scheme — it is not a failure state, provided the manuscript reports the
adjudicated, weaker number rather than the original unchecked one. `RQ14_MECHANISM_CODING_STATUS.md` and
`build_1a.js` §5.5/§6 should both be updated to cite 40%, the κ=0.41 reliability figure, and the
adjudication process above, replacing the current 80% claim and the "not yet checked" framing.
