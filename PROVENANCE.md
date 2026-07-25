# Coding provenance & inter-rater reliability

Every classification in this study was produced by **independent human coders** against a frozen
seven-channel codebook (`data/mining_validation/CODEBOOK_v2_FROZEN.md`). The reported pairwise Cohen's κ
is computed between the **two coders (R1, R2)** who coded every round; a **third coder (R3)** independently
coded the Qiskit seed and expansion as an additional check, and those labels are **not pooled** into the
reported κ. This document records who coded what and which files produce each κ.

## Coders
- **R1 — Author 1** (quantum-software background). Coded every round: Qiskit seed + expansion, tket, Cirq.
- **R2 — Muhammad Atif Saeed** (external volunteer; PhD scholar / lecturer, FAST-NUCES). Not an author,
  blinded to R1's labels. Coded every round. Signed declaration: `declarations/Coder_Declaration_Atif.pdf`.
- **R3 — Muhammad Sajjad Saleem** (external volunteer; MS Data Science, Thal University Bhakkar). Not an
  author, blinded. Independently coded the **Qiskit seed + expansion only** (`rater3_sheet.csv`), as an
  additional check not pooled into the reported κ. Signed declaration: `declarations/Coder_Declaration_Sajjad.pdf`.

Each coder independently classified every fix in the corpus assigned to them, from the pull-request description, linked
issues, diffs, release notes and regression tests, using only the frozen codebook. Disagreements between
R1 and R2 were adjudicated against the codebook (`adjudication_44.csv`, `adjudication_decisions.csv`);
adjudication did not overwrite the raw per-coder labels.

## Which files produce which κ (all reproducible)
| Corpus | n | Coder-R1 labels | Coder-R2 labels | pairwise Cohen's κ (binary) |
|--------|---|-----------------|-----------------|------------------------------|
| Qiskit seed      | 24 | `human_dual_rater.csv` (r1) | `human_dual_rater.csv` (r2) · `human_r2_friend_raw.csv` | 0.67 (0.62 channel) |
| Qiskit expansion | 44 | `human_worksheet_44_R1.csv` | `human_worksheet_44_R2.csv` | 0.86 |
| tket             | 21 | `tket_worksheet_R1.csv`     | `tket_worksheet_R2.csv`     | 0.77 |
| Cirq             | 10 | `cirq_worksheet_R1.csv`     | `cirq_worksheet_R2.csv`     | 0.52 |

The initial 70-fix Qiskit harvest was independently coded by all three coders — `rater1_sheet.csv` (R1),
`rater2_sheet.csv` (R2), `rater3_sheet.csv` (R3). The reported seed and expansion κ above use the two
coders (R1, R2) who continued through every round; R3's harvest labels are kept for transparency and are
not pooled into the reported κ. Reproduce (example):
`python scripts/score_worksheet.py data/mining_validation/human_worksheet_44_R1.csv --rater2 data/mining_validation/human_worksheet_44_R2.csv`.
Final adjudicated labels: `data/mining_validation/labels_final_68.csv` (Qiskit) and
`data/mining_validation/cross_sdk_adjudication.csv` (tket/Cirq).

## Note on AI assistance
An AI-assisted pass informed early candidate scoping only. It is not part of the reported coding, no
AI-generated label enters any reported statistic, and its label files are not included in this artifact;
the reported reliability rests solely on the human coding above. (Use of AI tools is disclosed in the
manuscript.)

## Signed declarations
The signed coder declarations (role, dates, independence, blinding, and the worksheet files holding each
coder's raw labels) are deposited in `declarations/`: `Coder_Declaration_Atif.pdf` (R2) and
`Coder_Declaration_Sajjad.pdf` (R3). Coder R1 is Author 1 of the manuscript.
