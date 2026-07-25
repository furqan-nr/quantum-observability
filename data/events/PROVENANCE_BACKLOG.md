# Provenance backlog — forward-regression candidates (not in the verified ledger)

The canonical event ledger (`events.csv` / `events.json`, **14 events**: 5 historical + 9 mutation) is
reproduction-verified. This backlog holds **forward-regression candidates** whose introducing commits
have been traced (by `git bisect` / `git blame`) but whose forward pair has **not yet been built and
run through the matched oracle**. They are deliberately kept out of the verified ledger so that the
study's single verified forward-regression event remains **H4 (#14120)** (METHODOLOGY §5.4 claim-scope
rule). Promote a candidate into `events.csv` / `events.json` only after step 4 below passes.

## Forward-regression candidates (bisection-traced; forward-pair verification pending)
| candidate_id | channel | introducing commit (candidate) | last-good parent (baseline) | fix PR | status |
|---|---|---|---|---|---|
| fwd-elide-14603 | contract/metadata | `cbb4d5d5` (#13094, Rust port) | `c34743a8` | #14603 | bisection-traced; forward-pair run pending |
| fwd-tlayout-registers-15024 | contract/metadata | `ccc2c77b` (#14778) | `e364cd96` | #15024 | bisection-traced; forward-pair run pending |
| fwd-pr14919 | contract/metadata | `df59ab0c` (#11399) | `090b2b19` | #14919 | bisection-traced; forward-pair run pending |
| fwd-pr16215 | global phase | `f2f85a94` | `a241dd19` | #16215 | bisection-traced; forward-pair run pending |

For **H1 (#14603)** and **H2 (#14919)** the introducing commit is recorded in the manuscript Table 3 as
the bisection-traced *origin* of the fix-boundary event; the fix-boundary reproduction is the verified
result in the ledger. The forward-cohort rows above would upgrade those two to true forward regressions
once verified in the forward orientation. `fwd-elide-14603` was previously marked "reproduced" on the
strength of the bisection alone; it is demoted here to pending until a forward-pair oracle run is
recorded, so the ledger does not overstate the number of verified forward regressions.

## Procedure (per candidate, to promote into the ledger)
1. Identify the fix PR's changed lines; `git blame` them at the parent to find the prior logic.
2. `git bisect start <buggy_parent> <last-known-good-release-tag>` with a scripted reproduction as the
   bisect test, to confirm the introducing commit `I`.
3. Record `baseline = I^` (last good), `candidate = I`, `event_date = I` timestamp,
   `pair_orientation = forward`, `evaluation_cohort = forward_regression`.
4. Build both revisions from source and re-run the matched oracle to confirm the fault reproduces in the
   **forward** orientation (output oracle blind, matched oracle fires). Only then add it to
   `events.csv` / `events.json`, update `n_events`, and re-run `scripts/validate_ledger.py`.

H4 (#14120) is already a verified forward regression and needs no tracing.
