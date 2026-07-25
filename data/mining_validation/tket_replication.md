# N3 — cross-SDK replication (tket and Cirq), final human-coded

**Question:** does the output-invisible rate found for Qiskit (19/68 ≈ 28% [19–40%]) replicate on other
quantum compilers? **Answer: yes, qualitatively, on small samples — dominated by the same channel.**

## Provenance (read this first)
The final, reported cross-SDK labels are **human dual-coded** against the same frozen seven-channel
codebook used for Qiskit (`CODEBOOK_v2_FROZEN.md`), by two independent coders, then adjudicated against
the codebook. Raw per-coder labels: `tket_worksheet_R1.csv` / `tket_worksheet_R2.csv` and
`cirq_worksheet_R1.csv` / `cirq_worksheet_R2.csv` (blinded second-pass copies: `*_worksheet_BLINDED.csv`);
adjudication in `cross_sdk_adjudication.csv`. The reported labels are human-coded throughout; see `../../PROVENANCE.md`.

## Method
`scripts/mine_sdk.py` blobless-cloned CQCL/tket and quantumlib/Cirq and harvested merged bug-fix commits
touching the compilation-pass directories; out-of-scope changes (housekeeping, serialisation, I/O
plumbing, simulation) were screened out; the in-scope fixes were then human dual-coded and adjudicated.

## Result (human-coded, adjudicated)
| SDK    | invisible / in-scope | rate | Wilson 95% CI | pairwise Cohen's κ (binary) |
|--------|----------------------|------|---------------|------------------------------|
| Qiskit | 19/68 | ~28% | 19–40% | 0.86 (44) · 0.67 (seed) |
| tket   |  7/21 | ~33% | 17–55% | 0.77 |
| Cirq   |  2/10 | ~20% | 6–51%  | 0.52 |

- The output-invisible faults are **dominated by the permutation / contract-metadata channel** on both
  other compilers — the same channel that dominates in Qiskit.
- tket analogues of the Qiskit faults include GreedyPauliSimp ignoring an implicit qubit permutation
  (#2072) and missing wire-swap handling in phase-polynomial synthesis (#146).

## Honest caveats
- The tket and Cirq samples are small (n = 21, n = 10) with wide, overlapping Wilson intervals, and
  Cirq's agreement is only moderate (κ = 0.52). We therefore read this as a **qualitative replication of
  the channel across compilers**, not a precise cross-compiler rate ordering.
- Cirq's leaner moment-based model exposes fewer layout/permutation-metadata contracts, and its
  transformer history is dominated by non-behavioural housekeeping (excluded by the scope gate); the
  lower, noisier estimate is consistent with the channel being architecture-dependent.

## Significance
The observability gap is **not Qiskit-specific**: it appears on two structurally different compilers,
dominated everywhere by the permutation/contract-metadata channel. See Table 7 and §6.5 of the manuscript.
