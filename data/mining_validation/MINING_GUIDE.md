# Mining guide — expanding the transpiler-fix corpus to >=100

Goal: grow `corpus.csv` from 26 to **>=100** real Qiskit transpiler bug-fixes (stretch 150-250),
each independently double-coded, so the output-invisible fraction (RQ1) and Cohen's kappa get a tight
confidence interval. Release window: **Qiskit 2.x** (band 2.1 -> latest stable, anchor 2.4.2) — same
window as the historical events, so Phase-D reproduction stays in one harness.

## Where to mine (exact GitHub queries)
Run these on github.com/Qiskit/qiskit and add every qualifying merged PR as a row in `corpus.csv`.

1. Transpiler bugfixes (primary):
   `is:pr is:merged label:"mod: transpiler" label:"Changelog: Bugfix"`
   https://github.com/Qiskit/qiskit/pulls?q=is%3Apr+is%3Amerged+label%3A%22mod%3A+transpiler%22+label%3A%22Changelog%3A+Bugfix%22

2. Transpiler bugfixes (broader, catches unlabeled-changelog fixes):
   `is:pr is:merged label:"mod: transpiler" label:bug`

3. Release-note "Fixed" entries: read each 2.x release note's *Transpiler* "Fixed" section and add any
   fix not already captured by (1)-(2).

4. Pass-specific sweep (catches fixes mislabeled): search merged PRs touching
   `qiskit/transpiler/passes/{layout,routing,basis,optimization,scheduling}` with "fix" in the title.

Deduplicate by `fix_pr`. Stop when you have >=100 (keep going to 150-250 if time allows).

## How to fill each column in corpus.csv
| Column | How to fill |
|---|---|
| `fix_pr`, `pr_url`, `title` | PR number; URL auto = pull/<n>; PR title |
| `issue_url` | linked issue (the "Fixes #NNNN"), if any |
| `fix_commit` | the merge/squash commit SHA of the fix |
| `introducing_commit` | the commit that introduced the bug, if `git blame`/discussion identifies it (else blank) |
| `modules` | files/dirs touched (e.g. `transpiler/passes/routing/sabre_swap.py`) |
| `stage` | one of: layout, routing, translation, optimization, scheduling, analysis, passmanager_global, shared_utility_unknown |
| `fix_date` | merge date (YYYY-MM-DD) |
| `r1_channel`, `r1_observable`, `r1_confidence` | Rater 1's labels per CODEBOOK.md |
| `r2_channel`, `r2_observable` | Rater 2's INDEPENDENT labels (must not see r1) |
| `channel_final`, `observable_final` | leave blank if r1!=r2 (adjudicate later); auto-filled when r1==r2 |
| `developer_confirmed` | yes if the issue/PR discussion confirms the channel, else no |
| `discussion_url` | link to the confirming comment, if any |
| `notes` | reasoning, especially for low-confidence / borderline calls |

## Coding protocol (per batch of new PRs)
1. Rater 1 fills r1_* using only PR title/description/linked issue (CODEBOOK.md).
2. Rater 2 fills r2_* **independently**, without seeing r1 (use a copy with r1 columns hidden).
3. Run `python3 data/mining_validation/compute_kappa.py` (point it at the expanded file) -> kappa + CI.
4. Adjudicate every disagreement; record the decision + reason in `adjudication_log.md`; set
   `channel_final`/`observable_final`.
5. Borderline focus: the quality vs contract_metadata vs output_semantic boundary drives most
   disagreements (PRs 15258, 14938, 14667, 14041, 13874, 13820, 14603). Tighten CODEBOOK.md borderline
   rules there BEFORE the next batch, then freeze the codebook.

## Done when
- corpus.csv has >=100 dual-coded rows; kappa reported with a tight CI; codebook frozen;
  labels + codebook released; output-invisible fraction reported with CI.
