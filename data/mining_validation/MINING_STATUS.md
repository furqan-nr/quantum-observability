# Mining study — current honest status (2026-06-29)

The core of the pivoted paper (oracle-observability of Qiskit transpiler regressions). This records
exactly where the empirical mining study stands today, computed from real artifacts.

## What already exists
- `../observability_mining.csv` — Rater 1 labels for **26** merged Qiskit transpiler fixes.
- `dual_rater_labels.csv` — **complete two-rater double-coding** of all 26 (r1 + r2 channel/observable).
- `CODEBOOK.md` — 7-channel codebook + borderline rules (Phase B substantially done; needs freeze marker).
- `compute_kappa.py` — agreement script (now fixed; see below).

## Current agreement (n = 26, full double-coding)
| Judgment | Raw agreement | Cohen's κ | 95% CI (bootstrap) | Interpretation |
|---|---|---|---|---|
| `observable_by_output_oracle` (binary, headline) | 84.6% | **0.675** | [0.350, 0.922] | substantial |
| `manifestation_channel` (7-class) | 73.1% | **0.665** | [0.426, 0.856] | substantial |

Output-invisible fraction (R1 'no'): **10/26 = 38%**. Confidence: high=13, medium=9, low=4.

## Important correction
The previous `compute_kappa.py` read `rater2_sheet.csv`, which is only partially filled (n=9), and
reported κ=1.000 — **inflated**. The fixed script uses `dual_rater_labels.csv` (all 26) and reports
the honest κ above. `rater2_sheet.csv` is retained only as the original independent rater-2 worksheet.

## What this means for Q1
- κ ≈ 0.67 is "substantial" and publishable, **but** the 95% CI lower bound (0.350 = "fair") is weak
  because n=26. **Scaling to ≥100 fixes is the main lever** to tighten the CI.
- Channel disagreements cluster on the same borderline trio the codebook already flags:
  quality vs metadata vs semantic (PRs 15258, 14938, 14667, 13874, 13820, 14603). Tightening those
  borderline rules before the next coding round should raise channel κ.
- 38% output-invisible on 26 is a strong preliminary signal for RQ1; needs the larger n for a
  defensible headline number + CI.

## Next actions (mining track)
1. Freeze `CODEBOOK.md` after tightening the quality/metadata/semantic borderline rules.
2. Expand corpus 26 → ≥100 (stretch 150–250); keep dual-coding new items.
3. Re-run `compute_kappa.py`; target tighter CI and channel κ ≥ 0.7.
4. Add developer-confirmation links + per-item confidence to the released labels.

---

## UPDATE 2026-06-29 — genuine HUMAN second rater obtained
A human SE colleague independently coded the 25-PR seed (blinded; no R1 labels), excluding PR 13884
as a non-bugfix. Authoritative human–human agreement (`human_dual_rater.csv`, n=24 matched):

| Judgment | Raw agreement | Cohen's κ | 95% CI | Interpretation |
|---|---|---|---|---|
| `observable_by_output_oracle` (binary, headline) | 83.3% | **0.667** | [0.338, 0.917] | substantial |
| `manifestation_channel` (7-class) | 70.8% | **0.619** | [0.360, 0.835] | substantial |

Output-invisible fraction: R1 = 42%, human R2 = 50% (headline ~40–50%, both raters agree it is large).
Human disagreements to adjudicate: binary {14998, 14938, 14041, 13820}; channel adds {15258, 14667, 13874}.

**This replaces LLM-rater agreement as the headline reliability.** ChatGPT/Mistral passes are no longer
needed for the reliability claim; if kept at all, disclose them only as an auxiliary automated
cross-check in supplementary material — never as the human IRR.

---

## UPDATE 2026-06-29 (later) — adjudicated FINAL labels (n=24)
Authoritative dataset: `labels_final.csv` (7 disagreements adjudicated via frozen codebook v2 +
`adjudication_decisions.csv`; 17 consensus rows unchanged).

- **Output-invisible fraction (RQ1): 12/24 = 50%** [Wilson 95% CI **31–69%**].
- Channels: contract_metadata 9, compilation_failure 7, output_semantic 5, determinism 2, global_phase 1
  (invisible channels = contract_metadata + determinism + global_phase = 12).
- **Reliability to report = PRE-adjudication κ** (binary 0.667, channel 0.619). Post-adjudication
  agreement is 1.0 by construction and must NOT be reported as IRR.

**Verify before trusting the 50%:** two adjudication calls drive/soften it and went against the
initial majority — (1) **14998** finalized contract_metadata/no though author + both LLMs first said
compilation_failure/yes (if the PR actually raised, it flips to VISIBLE); (2) **14667** finalized
compilation_failure though no rater saw a crash (basis note still says "Rule2-check-PR"). Confirm both
against the PRs. n=24 → CI is wide; scale to ~100 before the 50% is a headline.

---

## CORRECTION 2026-06-30 — verified 14998 against the PR
Qiskit release notes / PR #14998 state it fixes **crashes** when VF2PostLayout hits uncoupled qubits
with strict_direction=True. By Rule 1 (crash → compilation_failure = VISIBLE), the adjudicated
contract_metadata/no was wrong; corrected to **compilation_failure / yes**. Author's original + both
LLMs had it right; the friend-sided adjudication over-thought it (likely conflated with the separate
final_layout-corruption issue #10457).

- **Corrected output-invisible fraction: 11/24 = 46%** [Wilson 95% CI 28–65%].
- Channels: compilation_failure 8, contract_metadata 8, output_semantic 5, determinism 2, global_phase 1.
- Still-to-verify: **14041** (low-confidence contract_metadata/no, author-minority; confirm no crash
  and that it's in transpiler scope, else exclude) and 14667 (channel only; does not move the fraction).

---

## UPDATE 2026-07-04 — reconciled toward n=70; manuscript numbers propagated
Decision (supervisor-approved): expand the manuscript corpus to the 70-candidate set. See
`RECONCILIATION_70.md` for the full audit. Key points:
- Roadmap's "70 / 34% / 15-4-5" was a **projection, not data** — not backed by any artifact.
- 44 new screened-in PRs coded provisionally (`provisional_llm_labels_44.csv`, auxiliary LLM_R4,
  NOT headline IRR). Blinded human worksheet prepared: `human_worksheet_44_BLINDED.csv`.
- **Preliminary combined: 19/68 = ~28% output-invisible [Wilson 95% CI 19–40%]** (channels:
  contract_metadata 10, global_phase 5, determinism 4). Headline moved DOWN from 38%/46% because the
  new batch is crash/panic-dominated (19 compilation_failure, all visible).
- Numbers propagated into `paper/PAPER_DRAFT.md`, `paper/build_paper.js`, rebuilt `paper/PAPER.docx`
  and `paper/PAPER.pdf`. Every stale 26/38% removed; roadmap 34%/15-4-5 not cited.
- **Still open:** independent human coding of the 44 (Raters 2 & 3) → recompute κ + Wilson CI →
  finalize the single number. Priority review: the 8 `FLAG` rows, esp. #14765.
