# Rater provenance — inter-rater coding of the transpiler-fix corpus

Two independent human coders labelled every fix against the frozen codebook
(`CODEBOOK_v2_FROZEN.md`). All reported inter-rater agreement is computed from their
labels only:

- **24-fix adjudicated seed** — coders R1 and R2; raw human labels in
  `human_dual_rater.csv` (and `human_r2_friend_raw.csv`). Pairwise Cohen's kappa
  0.67 (binary), 0.62 (seven-class channel); raw agreement 83.3% / 70.8%.
- **44-fix expansion** — coders R1 and R2, blind to each other, in
  `human_worksheet_44_R1.csv` / `human_worksheet_44_R2.csv`. Pairwise Cohen's kappa
  0.86 (binary), 95.5% raw agreement.

Disagreements were adjudicated against the codebook (`adjudication_*`); the final,
adjudicated labels are in `labels_final_68.csv`.

- **Confirmatory third round (batch-002), n = 36** — a wider mining window (older and more recent
  history), coded by the same R1/R2 pair as every other round (`batch_002_r1_completed.csv`,
  `batch_002_r2_completed.csv`); R3 did not take part in this round. Pairwise Cohen's kappa 0.929
  (binary), 0.962 (seven-class channel), 97.2% raw agreement — the highest of any round. One
  disagreement (PR #11351), adjudicated from the fix's own diff (`adjudication_002.csv`,
  `adjudication_log_002.md`). Merged with the 68-fix corpus into `labels_final_104.csv`: 29/104 =
  27.9% output-invisible (Wilson 95% CI 20-37%; point estimate unchanged from 19/68, interval
  tightened). See `BATCH_002_CODING_COMPLETE.md` for the full summary.

An initial, exploratory large-language-model pass was run early in codebook
development to help surface candidate channels. Those labels were **not** used in any
reported statistic and have been removed from this package to avoid confusion; every
reported agreement value is human-only and pairwise. One adjudication decision in the batch-002
round (PR #11351) used AI assistance to retrieve and summarize the fix's source diff; the human
coders reviewed that evidence and made the final call themselves — see `adjudication_log_002.md`
for the full disclosure.
