# Reproducibility package — `cart`

This archive accompanies the manuscript **"An Empirical Study of Equivalence-Invisible Bug Fixes in
Quantum Transpilers (Qiskit, tket, Cirq)"** (Nasir, Shah, Alam; submitted to the *Journal of Systems
and Software*, Elsevier), and the `cart` research prototype used by a companion, in-preparation paper
on a fault-class-matched oracle family for the same channels.

- Repository: https://github.com/furqan-nr/quantum-observability
- Archive (DOI): [10.5281/zenodo.22484774](https://doi.org/10.5281/zenodo.22484774) (Zenodo, archiving GitHub release `v1.0.0`)
- License: MIT (see `LICENSE`)

This repository is the reproduction artifact only; the manuscript and its figures are maintained
separately.

## What is here

```
src/cart/            the cart prototype (CLI + manifest, events, oracles, labels,
                     metrics, validity gates)
scripts/             verification and mining tooling (see the commands below)
tests/               automated test suite (incl. the six validity gates)
configs/             frozen, pre-declared config: stage_map, thresholds, budgets,
                     cutoff, seeds
data/
  events/            audited change-event ledger with exact candidate/baseline SHAs
  manifest_static/   static test-unit manifest + targeted triggers
  raw/               write-once raw oracle evidence (per event)
  derived/           labels regenerated from raw evidence
  mining_validation/labels_final_68.csv  canonical 68-fix mining labels (28% equivalence-invisible)
  mining_validation/             final 68-fix labels, the 104-fix secondary check, human
                                 worksheets, the frozen codebook, adjudication trail,
                                 source-validation, R3's independent labels, surface-
                                 characteristic data, and the tket/Cirq cross-SDK worksheets
  rq14_spotcheck/                RQ1.4 mechanism-coding: title-level spot-check (kappa=0.41)
  rq14_invisible19_recode/       RQ1.4 mechanism-coding: diff-level recheck of all 19
                                 equivalence-invisible fixes (kappa=0.87)
results/             generated evaluation outputs and write-once oracle result JSONs
environment/         two-layer env recipes; pinned requirements; per-event
                     from-source build scripts (the built Qiskit trees are NOT shipped)
```

## Install

```bash
python -m pip install -e .            # Python 3.11 (or set PYTHONPATH=src)
```

The harness layer is pinned in `environment/requirements.lock` (`requirements.lock.sha256`
records its hash).

## 1. Oracle-observability mining study (the headline finding)

```bash
# authoritative headline over the final, human-adjudicated 68-fix corpus:
python -c "import csv; r=list(csv.DictReader(open('data/mining_validation/labels_final_68.csv'))); inv=sum(x['observable']=='no' for x in r); print(f'{inv}/{len(r)} = {round(100*inv/len(r))}% equivalence-invisible')"
python scripts/score_worksheet.py data/mining_validation/human_worksheet_44_R1.csv --rater2 data/mining_validation/human_worksheet_44_R2.csv   # pairwise kappa on the 44
```

Expected: of 68 in-scope merged Qiskit transpiler bug-fixes, **19/68 = 28%** lie in channels a
black-box output-equivalence oracle cannot observe (contract/metadata 10, non-determinism 4, dropped
global phase 5), Wilson 95% CI **[19%, 40%]**. The 44 newly coded fixes reached pairwise Cohen's
**kappa = 0.86** (95.5% agreement) and the 24-fix seed **kappa = 0.67**. Final labels:
`data/mining_validation/labels_final_68.csv`; the codebook and adjudication trail are alongside it.

A secondary, wider-window robustness check (36 further fixes, same frozen codebook) merges into
`data/mining_validation/labels_final_104.csv`: **29/104 = 27.9%**, Wilson 95% CI **[20%, 37%]**
(`BATCH_002_CODING_COMPLETE.md`). A fully independent third coder (R3) also labelled all 68 fixes;
`scripts/r3_sensitivity_check.py` compares R3 against the adjudicated R1/R2 labels (94.1% raw
agreement, Cohen's kappa = 0.86; taking R3 alone would raise the rate to 23/68 = 33.8%, not lower it).

## 1a. Cross-SDK replication — RQ1.2

```bash
python scripts/score_worksheet.py data/mining_validation/tket_worksheet_R1.csv --rater2 data/mining_validation/tket_worksheet_R2.csv
python scripts/score_worksheet.py data/mining_validation/cirq_worksheet_R1.csv --rater2 data/mining_validation/cirq_worksheet_R2.csv
```

Expected: tket **7/21 = 33%**, Wilson 95% CI [17%, 55%], Cohen's kappa = 0.77 (substantial) —
independently dual-coded replication evidence, comparable in scale to Qiskit. Cirq **2/10 = 20%**,
CI [6%, 51%], kappa = 0.52 (moderate) — reported as exploratory rather than replication evidence,
since Cirq's transformer bug-fix history has too few remaining eligible cases at this scope to grow
the sample responsibly (see `data/mining_validation/tket_replication.md`).

## 2. Source-verified detections in all three output-invisible channels

```bash
python scripts/verify_h1_isolated.py                     # #14603 contract/metadata (isolated-pass differ)
python scripts/verify_14919_routing.py                   # #14919 metamorphic MR-1
python scripts/source_validate_mining.py --only 14956    # #14956 global phase
python scripts/determinism_eval.py                       # #14730 determinism (5 hash seeds, 50 runs)
python scripts/verify_16201.py                           # #16201 global phase (UnrollForLoops)
python scripts/verify_16237.py                           # #16237 determinism (ConsolidateBlocks)
python scripts/channel_matched_eval.py                   # channel-matched global-phase family
python scripts/heldout_oracle_eval.py                    # held-out specificity (0 FP over 54 runs)
```

Expected: an output-equivalence oracle cannot distinguish the buggy build from its fix, yet the
fault-class-matched oracle (or a dedicated runner) detects it. At least two real source-evidenced faults
per channel: contract/metadata (#14603, #14919), global phase (#14956, #16201), determinism (#14730,
#16237). Result JSONs are written to `results/`.

## 3. Anchor cases requiring from-source Qiskit builds

```bash
python scripts/verify_h1_property.py    # H1 (ElidePermutations, PR #14603): property/layout oracle
python scripts/verify_h4_perf.py        # H4 (VF2PostLayout no-op, PR #14120): Stage-2 perf protocol
```

Expected: the output-equivalence oracle cannot distinguish the buggy **H1** build from its fix, while
the fault-class-matched property/isolated-pass oracle detects it. **H4** is confirmed as the study's one
prospective forward regression, with a candidate slowdown that grows with width from about 1.9x (16
qubits) to more than 300x (27 qubits) on symmetric circuits over a large heavy-hex map (Cliff's delta = 1.0).

Building the per-event Qiskit revisions from source needs a Rust toolchain; the recipe is in
`environment/setup/` (`SETUP.md`, `SETUP_WINDOWS.md`, `build_qiskit_event.*`) and the recorded
`baseline_sha` / `candidate_sha` in the event ledger pin exactly what to build. Built trees are cached
under `environment/_builds/` when present and are NOT shipped.

## RQ1.3 — are equivalence-invisible fixes distinguishable by surface characteristics?

```bash
python scripts/pull_pr_metadata.py      # set GITHUB_TOKEN to avoid the API rate limit (no scope needed)
#   -> data/mining_validation/pr_characterization_{raw,summary}.csv
python scripts/table5_stats.py          # Table 5: medians, Mann-Whitney U, Cliff's delta, bootstrap 95% CI
```

Expected: a two-sided Mann–Whitney U over the 19 invisible vs 49 observable fixes finds no dimension
distinguishing the groups (all p ≥ 0.12, all Cliff's |delta| ≤ 0.22, every bootstrap 95% CI on delta
brackets zero) — equivalence-invisible fixes are ordinary-looking on these five cheap signals, so they
cannot be triaged by a surface heuristic. The comparison is underpowered (19 vs 49) rather than proof
of no true difference.

## RQ1.4 — recurring fault-mechanism categories (exploratory)

Single-coder, diff-verified mechanism-category coding of all 68 fixes is in
`data/rq14_spotcheck/rq14_mechanism_coding_EVIDENCE_VERIFIED.csv` (see `RQ14_MECHANISM_CODING_STATUS.md`
for how this superseded two earlier, less reliable passes). Two independent-coder reliability checks
sit alongside it, both human-coding studies rather than re-runnable scripts:

- `data/rq14_spotcheck/` — an earlier title-level spot-check on a mixed 19-item sample (10
  contract/metadata fixes + 9 random draws): Cohen's kappa = 0.41 (moderate). Superseded as the basis
  for any reported reliability figure, but kept for the methodological record
  (`SPOTCHECK_RESULTS.md`).
- `data/rq14_invisible19_recode/` — a full, diff-level independent recoding of all 19
  equivalence-invisible fixes specifically (the subset the manuscript's Discussion depends on):
  17/19 raw agreement (89.5%), Cohen's kappa = 0.87 (almost-perfect). Both disagreements were
  adjudicated against each PR's own GitHub diff; both resolved in favor of the original label, so no
  category count changes (`RECODE_RESULTS.md`).

## Notes

- Raw oracle evidence in `data/raw/` is write-once; labels in `data/derived/` regenerate from it.
- The reported inter-rater agreement is a pairwise Cohen's kappa between the two independent human
  coders; disagreements were adjudicated against the frozen codebook.
- Claim scope: with fewer than three verified forward-regression events, comparative claims are reported
  per event rather than as a temporal-generalization claim.
