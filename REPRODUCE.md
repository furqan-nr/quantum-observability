# Reproducibility package, `cart`

This archive accompanies the manuscript **"Oracle Observability of Quantum Transpiler Regressions:
What Output-Equivalence Oracles Miss in Qiskit, and a Leakage-Safe, Cost-Aware Regression-Testing
Pilot"** (submitted to *Quantum Information Processing*, Quantum Software Engineering collection).

DOI: https://doi.org/10.5281/zenodo.21020113 · Repository:
https://github.com/furqan-nr/quantum-transpiler-regression-testing · License: MIT (see `LICENSE`).

## What is here

```
src/cart/            the cart prototype (CLI + manifest, events, oracles, selectors,
                     metrics, validity gates, labels)
scripts/             verification and scale-up tooling (see the commands below)
tests/               automated test suite (64 tests, incl. the six validity gates)
configs/             frozen, pre-declared config: stage_map, thresholds, budgets,
                     cutoff, seeds
data/
  events/            audited change-event ledger with exact candidate/baseline SHAs
  manifest_static/   static test-unit manifest + targeted triggers
  profile_baseline/  calibrated per-unit cost profiles
  raw/               write-once raw oracle evidence (per event)
  derived/           labels regenerated from raw evidence
  observability_mining.csv   26 classified Qiskit transpiler bug-fixes
  mining_validation/         multi-rater labels, codebook, adjudication trail,
                             blinded rater package (for_SE_rater/)
results/             generated evaluation outputs (evaluation.json, analyze runs)
environment/         two-layer env recipes; pinned requirements; per-event
                     from-source build scripts (the built Qiskit trees are NOT shipped)
paper/               manuscript (PAPER.docx), cover letter, figures, Response_to_Reviewers
METHODOLOGY.md       authoritative research specification (read first)
FORWARD_REGRESSION_PLAN.md, SCALEUP_PROTOCOLS.md, REVISION_TODO.md
```

## Install

```bash
python -m pip install -e .            # Python 3.11 (or set PYTHONPATH=src)
```

The harness layer is pinned in `environment/requirements.lock` (`requirements.lock.sha256`
records its hash).

## 1. Selection pilot (mutation cohort), no Rust needed

```bash
python -m cart.cli ground-truth --unit-limit 64            # label the 9-operator cohort
python -m cart.cli evaluate --split all --random-seeds 20  # detection curves, metrics, 6 gates
python -m cart.cli analyze                                 # ablation + sensitivity
```

Expected (9 mutations x 32 units = 288 labels, Qiskit 2.4.2): a documented null. Mean
detection-vs-budget AUC diversity-only **0.886**, cost/history/change-stage **0.877**, random
median **0.783**, proposed `risk_score` **0.692**. Removing the severity term `impact_prior` raises
the proposed AUC to **0.716** (ablation). All six validity gates pass; 64 automated tests pass.

## 2. Oracle-observability mining study (the headline finding)

```bash
# authoritative headline over the final, human-adjudicated 68-fix corpus:
python -c "import csv; r=list(csv.DictReader(open('data/mining_validation/labels_final_68.csv'))); inv=sum(x['observable']=='no' for x in r); print(f'{inv}/{len(r)} = {round(100*inv/len(r))}% output-invisible')"
python scripts/score_worksheet.py data/mining_validation/human_worksheet_44_R1.csv --rater2 data/mining_validation/human_worksheet_44_R2.csv   # kappa on the 44
```

Expected: of 68 in-scope merged Qiskit transpiler bug-fixes, **19/68 = 28%** lie in channels a black-box
output-equivalence oracle cannot observe (contract/metadata 10, non-determinism 4, dropped global phase 5),
Wilson 95% CI **[19%, 40%]**. The 44 newly coded fixes reached Cohen's **kappa = 0.86** (95.5% agreement)
and the 24-fix seed **kappa = 0.67**. Final labels: `data/mining_validation/labels_final_68.csv`; the
codebook and adjudication trail are in `data/mining_validation/`. (The older `scripts/mining_stats.py`
reads a superseded provisional rater sheet and is retained only for provenance.)

## 3. Anchor cases (require a Rust toolchain and per-event from-source Qiskit builds)

```bash
python scripts/verify_h1_property.py    # H1 (ElidePermutations, PR #14603): property/layout oracle
python scripts/verify_h1_isolated.py    # H1 in isolation: the fault the full pipeline masks
python scripts/verify_h4_perf.py        # H4 (VF2PostLayout no-op, PR #14120): Stage-2 perf protocol
```

Expected: an output-equivalence oracle cannot distinguish the buggy **H1** build from its fix, yet
the fault-class-matched property/isolated-pass oracle detects it. **H4** is confirmed as a verified
forward regression, with a candidate slowdown that grows with width from about 1.9x (16 qubits) to
more than 300x (27 qubits) on symmetric circuits over a large heavy-hex map (Cliff's delta = 1.0).

Building the per-event Qiskit revisions from source is covered in `environment/setup/SETUP_WINDOWS.md`
and `FORWARD_REGRESSION_PLAN.md`; the recorded `baseline_sha` / `candidate_sha` in the event ledger
pin exactly what to build.

## Notes

- All comparative selection results are reported as a feasibility pilot; the proposed `risk_score`
  selector is an explicit baseline, not a claimed method, and does not beat the simple baselines at
  this scale (a documented null). See the claim-scope rule in `METHODOLOGY.md`.
- Raw oracle evidence in `data/raw/` is write-once; labels in `data/derived/` regenerate from it.
- The mining study is now a 68-fix multi-rater result, the fault-class-matched oracles are built and
  source-validated, and forward regressions are verified (contract/metadata, global-phase, and
  performance H4). The remaining scale-up (a powered, cost-heterogeneous selection study on controlled
  hardware) is documented in `SCALEUP_PROTOCOLS.md` and `REVISION_TODO.md`.
