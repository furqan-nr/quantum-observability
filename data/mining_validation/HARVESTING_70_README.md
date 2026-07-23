# C2 Harvesting Workflow — 70-Event Candidate Corpus

## Corpus count
- Existing human Rater 1 baseline: **26** PRs.
- New screened-in candidate PRs: **44**.
- Candidate corpus: **70** PR-keyed events.
- Screening log: **59** reviewed PRs: **44 include**, **15 exclude**.

## What changed from the 65-event set
Five distinct fixes were added:
- #16249 — ConstrainedReschedule underflow panic.
- #16246 — ConstrainedReschedule without Target raises AttributeError.
- #16151 — ConstrainedReschedule rejects barriers.
- #16154 — `synth_cz_depth_line_mr` can panic on an invalid matrix shape.
- #15137 — HighLevelSynthesis misses nested custom-gate calibrations.

## Re-audit outcome
- All 39 previously included candidates were retained.
- **No replacement was required.**
- The audit checked PR-number duplication against the 26-event baseline and 44-candidate list, known backport duplication, stated defect content, and scope at the pass/component level.
- The audit is an eligibility screen only; it does not classify manifestation channel, observability, or confidence.

## Files
- `observability_mining_70.csv`: full screening log. No Rater 1 labels.
- `rater1_candidate_queue_full_70.csv`: blinded queue of 44 new candidates.
- `included_candidate_audit_70.csv`: retain/add decisions and audit rationale.
- `mining_seed_issue_resolution_70.csv`: seed issue-to-PR map.

## Scope/label caveat
GitHub's current public PR pages do not consistently show historical `mod: transpiler` or `bug` labels. The five added PRs were selected from official Qiskit release/PR evidence with concrete transpiler or high-level-synthesis defects; this limitation is explicitly recorded in the screening log. PR #15137 is a stable/1.4 HighLevelSynthesis fix and is included under the planned 1.4 extension, with the missing current public `mod: transpiler` badge noted.

## Rater separation
Raters 1–3 are human. Rater 4 is the LLM and remains outside the primary human inter-rater agreement analysis.

## Integrity check — unchanged human-rater files
- rater1_sheet.csv: ddb5ae96545bc92acef58758d907c095c440742881e7dbe15a7fd79a22eb0b5f
- rater2_sheet.csv: 30f3ef349428acc69e90c48d1252660a54ea064577e1bd669a73e43010570c67
- rater3_sheet.csv: 644acdec8887880723356d70cf2a689bf1e92f8d78389eb5bdbabfe1e75811ae
