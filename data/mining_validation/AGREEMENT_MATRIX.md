# Inter-rater agreement (human coders)

Two independent human coders (R1, R2) coded every fix against the frozen codebook.
Cohen's kappa is a pairwise statistic between the two coders.

| Corpus | n | Binary kappa | Channel kappa | Raw agreement |
|---|---|---|---|---|
| 24-fix adjudicated seed (R1 vs R2) | 24 | 0.667 | 0.619 | 83.3% / 70.8% |
| 44-fix expansion (R1 vs R2, blinded) | 44 | 0.861 | — | 95.5% |

Disagreements were adjudicated against the codebook; final labels in `labels_final_68.csv`.

Reproduce the 44-fix agreement:

```
python ../../scripts/score_worksheet.py human_worksheet_44_R1.csv --rater2 human_worksheet_44_R2.csv
```
