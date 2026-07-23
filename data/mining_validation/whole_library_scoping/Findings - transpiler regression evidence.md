# Post-BASR evidence: are the observability-gap channels a real problem?

Repository: Qiskit/qiskit · Window: merged 2025-07-15 to 2026-07-16 · Retrieved 2026-07-17
Companion data: `qiskit_transpiler_regressions.xlsx` (this folder)

## Question

Before starting the full study, we wanted to know whether the three fault channels our
framework targets, contract/metadata, non-determinism, and global-phase, actually receive
real fixes in the last year. If they were rare, the research would be solving a non-problem.

## Headline numbers

Across the whole Qiskit library, 217 bug-fixes (label `Changelog: Fixed`) were merged in
the window. Counting on a like-for-like basis, including backports:

- Transpiler fixes: 64, about 29 per cent of all Qiskit bug-fixes.
- Observability-gap fixes: 44, about 20 per cent of all Qiskit bug-fixes.
- Within the transpiler, 69 per cent of fixes sit in the gap channels (27 of 39 distinct).

So roughly one in five of every bug-fix in the entire library is a transpiler fault our
framework is built to catch and the standard output-equivalence oracle can miss.

## Distinct fixes by channel (backports removed)

| Channel | Label query | Missed by label | Combined |
|---|---|---|---|
| contract/metadata | 12 | 1 | 13 |
| non-determinism | 3 | 2 | 5 |
| global-phase | 3 | 6 | 9 |
| compilation-failure | 5 | 2 | 7 |
| circuit-quality | 5 | 0 | 5 |
| Total | 28 | 11 | 39 |

Target-channel total: 27 of 39 distinct fixes (69 per cent).

## The methodological lesson (important for Year 2 mining)

Label-based mining undercounts badly. We found the fixes in three widening passes, and each
pass caught real regressions the previous one missed:

1. Labels only (`mod: transpiler` + `Changelog: Fixed`): 28 distinct fixes.
2. Title-keyword sweep (pass names and channel terms): +8 distinct. Caught fixes tagged
   `mod: circuit` or left unlabelled, e.g. Commuting2qGateRouter, UnrollForLoops.
3. Semantic review of the remainder: +3 distinct. Caught a second global-phase bug in
   CommutativeCancellation (#14956, distinct from #16402, so the same pass regressed in the
   same channel twice in one year) and a silently broken transpiler-seed contract (#16336,
   tagged `Changelog: None`, invisible to any label or keyword search).

Global-phase, one of our target channels, grew from 3 to 9 across the three passes, so it is
the channel labels under-represent the most. The mining protocol for the full study must
therefore combine labels, pass-name and channel keywords, and a semantic review pass, or it
will silently miss real observability-gap regressions.

## Honest caveats

- The channel classification in the workbook is an AI first pass. It is a screening aid, not
  ground truth. Human raters confirm each channel in the sheet's Rater columns, then we
  compute inter-rater agreement (Cohen's or Fleiss' kappa).
- The 217 denominator is a pure label count and includes backports, so the percentages above
  include backports on both sides for consistency. On a distinct basis the shape is the same.
- These are fixes merged in the last year. The underlying bug may be older. Establishing that
  a regression was introduced in the window needs introducing-commit tracing, which is the
  forward-regression cohort work for Year 2.
- Even the three-pass search is keyword and judgement bounded, so treat 39 distinct transpiler
  fixes as a solid floor, not a complete census.

## Next steps for the full study

- Trace introducing commits for the target-channel fixes to build the forward-regression cohort.
- Run the human-rater pass on the workbook, then report kappa.
- Reuse this three-layer mining protocol (labels + keywords + semantic review) at scale.
