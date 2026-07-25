# Coding provenance & inter-rater reliability

Every classification reported in this study was produced by **two independent human coders** against a
frozen seven-channel codebook (`data/mining_validation/CODEBOOK_v2_FROZEN.md`). This document records who
coded what and which files produce each κ.

## Coders
- **Coder R1 (Author 1)** — quantum-software background; see the signed declaration in `declarations/`.
- **Coder R2 (independent)** — software-engineering background, not an author of the manuscript, blinded to
  R1's labels; see `declarations/`. The blinded second-pass materials and
  the external-rater instruction package are in `data/mining_validation/for_SE_rater/` and the
  `*_worksheet_BLINDED.csv` files.

Each in-scope fix was classified independently by R1 and R2 from the pull-request description, linked
issues, diffs, release notes and regression tests, using only the frozen codebook. Disagreements were
adjudicated against the codebook (`adjudication_44.csv`, `adjudication_decisions.csv`); adjudication did not overwrite
the raw per-coder labels.

## Which files produce which κ (all reproducible)
| Corpus | n | Coder-R1 labels | Coder-R2 labels | pairwise Cohen's κ (binary) |
|--------|---|-----------------|-----------------|------------------------------|
| Qiskit seed      | 24 | `human_dual_rater.csv` (r1) | `human_dual_rater.csv` (r2) · `human_r2_friend_raw.csv` | 0.67 (0.62 channel) |
| Qiskit expansion | 44 | `human_worksheet_44_R1.csv` | `human_worksheet_44_R2.csv` | 0.86 |
| tket             | 21 | `tket_worksheet_R1.csv`     | `tket_worksheet_R2.csv`     | 0.77 |
| Cirq             | 10 | `cirq_worksheet_R1.csv`     | `cirq_worksheet_R2.csv`     | 0.52 |

Reproduce (example): `python scripts/score_worksheet.py data/mining_validation/human_worksheet_44_R1.csv --rater2 data/mining_validation/human_worksheet_44_R2.csv`.
Final adjudicated labels: `data/mining_validation/labels_final_68.csv` (Qiskit) and
`data/mining_validation/cross_sdk_adjudication.csv` (tket/Cirq).

## Note on AI assistance
An AI-assisted pass informed early candidate scoping only. It is not part of the reported coding, no
AI-generated label enters any reported statistic, and its label files are not included in this artifact;
the reported reliability rests solely on the human double-coding above. (Use of AI tools is disclosed in
the manuscript.)

## Signed declarations
Each coder's signed declaration (role, dates, independence, blinding, and the worksheet file holding their
raw labels) is in `declarations/`.
