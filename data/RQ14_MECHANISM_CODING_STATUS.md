# RQ1.4 mechanism coding — status and how to verify it (2026-09-04, updated same day with spot-check result)

## UPDATE 2026-09-08: independent diff-level recoding of the 19 equivalence-invisible fixes

A second, independent coder re-assigned mechanism categories for all 19 equivalence-invisible fixes
(the subset the paper's Discussion §6 depends on), working from each PR's own diff and blinded to the
existing labels. Result: 17/19 raw agreement (89.5%), Cohen's κ = 0.87 (almost-perfect). Both
disagreements were adjudicated against the actual GitHub diff; both were resolved in favor of the
original label, so no category counts changed. Full detail in
`rq14_invisible19_recode/RECODE_RESULTS.md`. `build_1a.js` §5.5 and §6 now cite this reliability figure
alongside the 60% contract/metadata finding.

## What this is

`rq14_mechanism_coding_DRAFT.csv` assigns each of the 68 corpus fixes to one of 11 recurring
**fault-mechanism categories**, derived by open-coding the fix titles and one-line notes already
present in `data/mining_validation/rater1_sheet.csv` (the same descriptive text used for the channel
taxonomy, not new research). Category totals cross-checked against `labels_final_68.csv`'s final
adjudicated channel: the channel marginals reproduce Table 4 exactly (compilation_failure 24,
output_semantic 20, contract_metadata 10, circuit_quality 4, global_phase 5, determinism 4,
performance 1), which is the internal-consistency check this kind of derived table needs.

**UPDATE 2026-09-04 (superseded same day, see next box): spot-checked and adjudicated by title.** A
third coder independently labeled a 19-item blind sample; agreement came back at κ=0.41 (moderate) — see
`rq14_spotcheck/SPOTCHECK_RESULTS.md` for the full result. The 10 disagreements were then adjudicated by
hand against an explicit rule and the same rule reapplied across all 68 items for consistency, producing
`rq14_spotcheck/rq14_mechanism_coding_ADJUDICATED.csv` and a headline figure of 4/10 (40%). **This
title-based adjudication was itself superseded the same day — see the box immediately below.**

**UPDATE 2026-09-04 (final): every one of the 68 items diff-verified against real PR code.** Guessing
from titles and descriptions — even carefully, even adjudicated against an explicit rule — turned out to
be unreliable: fetching the actual GitHub diff for all 68 fixes found additional miscategorizations the
title-based adjudication had missed. Full per-item evidence citations are in
`rq14_spotcheck/rq14_mechanism_coding_EVIDENCE_VERIFIED.csv`; the process and final numbers are in the
"SUPERSEDING UPDATE" box at the top of `rq14_spotcheck/SPOTCHECK_RESULTS.md`. **The manuscript should
cite the evidence-verified numbers, not the 80% original or the 40% title-adjudicated figure**: the
`contract_metadata` headline claim is **6/10 (60%)** representation/port-boundary bugs. The rest of this
file's "what this is NOT" section is kept for the historical record of what the *original* single-pass
coding was and was not; treat the evidence-verified box as overriding wherever any of the three disagree.

## What this is NOT (the original single-pass coding, before the spot-check — historical)

**This is a single-coder, exploratory pass — mine, done in one sitting from the existing fix
descriptions — not an independently verified coding round like the channel taxonomy (§4.4-4.6).**
It has no kappa, no blinding, no adjudication [**now superseded — it has both, see the Update box
above**]. Two important honesty points:

1. **"Mechanism category" is not the same claim as "introducing circumstance."** A true
   introducing-circumstance analysis would trace each fix's git history to find and characterize the
   commit that introduced the fault. I only did that for two fixes — `#14603` (introduced by `cbb4d5d5`,
   "Port ElidePermutations to Rust #13094") and `#15024` (introduced by `dd8269969`, "Port ApplyLayout
   to Rust #14904") — both confirmed in prior work (`../../Paper 2 - Selection/FWD_15024_RETRACE.md`).
   Those two are labelled `rust_port_metadata_loss` and are the only category in this table backed by
   verified git archaeology. The other 66 rows are categorized from what the *fix itself* reveals about
   the fault's nature, which is a legitimately weaker claim than "this is what introduced it" — it is
   closer to "this is the kind of fault it is."
2. **Category boundaries involved real judgment calls** (documented inline where non-obvious, e.g. is a
   control-flow qubit-mapping bug a `control_flow_gap` or a `cross_representation_conversion`? I called
   several of these one way; a second coder could reasonably call some differently).

## The finding, evidence-verified (supersedes both the 80% and 40% claims below)

After diff-checking all 68 items against real PR code (see Update box above), `contract_metadata` breaks
down as 4 `cross_representation_conversion` + 2 `rust_port_metadata_loss` + 2
`missing_validation_or_contract_check` + 1 `logic_error_pass_specific` + 1 `api_plumbing_or_serialization`.
That is **6 of 10 (60%) of the contract/metadata fixes are representation- or language-boundary
issues** — the largest pattern in the channel by a clear margin, anchored by the two independently
git-verified Rust-port cases (`#14603`, `#15024`) plus two fixes whose diff shows an explicit cross-pass
layout composition (`#13945`, `#14919`) plus two more confirmed by reading the code itself (`#13910`,
`#15137`). This is a real, evidence-grounded claim, weaker than the original unchecked 80% but stronger
than the title-based adjudication's 40% — report it as 60%, with the κ=0.41 reliability figure and the
diff-verification process alongside it.

*(Superseded intermediate claim: a title-based adjudication of the 10 disagreements from the spot-check
produced 40% — 2 `cross_representation_conversion` + 2 `rust_port_metadata_loss` + 5
`logic_error_pass_specific` + 1 `api_plumbing_or_serialization`. Diff-reading `#13833`/`#14938`/`#14939`
found the adjudication itself had over-corrected: `#13833` and `#14938` are genuinely unhandled
idle/disjoint-qubit cases — `missing_validation_or_contract_check`, not
`cross_representation_conversion`/`logic_error_pass_specific` as either the original or the adjudicated
coding had it — while `#14939` is a plain ordering bug — `logic_error_pass_specific`, not
`cross_representation_conversion` as both the original and the adjudication had it.)*

*(Original single-pass claim, no longer current: 6 `cross_representation_conversion` + 2
`rust_port_metadata_loss` + 1 `logic_error_pass_specific` + 1 `api_plumbing_or_serialization` = 8/10
(80%). This did not survive the spot-check — see `rq14_spotcheck/SPOTCHECK_RESULTS.md`.)*

Two other categories remain larger than the metadata-conversion one and worth reporting even though they
are not this paper's headline: `missing_validation_or_contract_check` (15/68, 22% after evidence
verification, up from 13/68 — mostly unhandled edge cases: empty layouts, missing backends, unvalidated
targets, idle/disjoint qubits) and `unchecked_numeric_edge_case` (9/68, 13% after evidence verification,
down from 10/68 — almost entirely Rust-side panics on malformed or boundary-value input, all
compilation_failure and therefore already output-visible).

## Spot-check: done (2026-09-04)

A third, independent coder blind-coded a 19-item sample (all 10 `contract_metadata` rows plus 9 random
draws, `random.seed(42)`). Result: κ=0.410 (moderate), raw agreement 47.4%, `contract_metadata` subset
agreement 50%. Full result, adjudication rule, and per-item reasoning in
`rq14_spotcheck/SPOTCHECK_RESULTS.md` and `rq14_spotcheck/rq14_mechanism_coding_ADJUDICATED.csv`.

## Where this is used in the manuscript

`Paper 1A/paper/build_1a.js` §5.5/§6 — **update to cite the evidence-verified 60% figure and κ=0.41**,
not the original 80% claim and not the intermediate 40% title-based adjudication. Frame as: single-coder
open coding, independently spot-checked (κ=0.41, moderate), then every one of the 68 items verified
against the actual PR diff rather than titles or descriptions — a defensible, evidence-grounded finding
weaker than the unchecked original but stronger than a title-based guess.
