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

An initial, exploratory large-language-model pass was run early in codebook
development to help surface candidate channels. Those labels were **not** used in any
reported statistic and have been removed from this package to avoid confusion; every
reported agreement value is human-only and pairwise.
