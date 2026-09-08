# Oracle Observability of Quantum Transpiler Regressions

Reproducibility package for **"An Empirical Study of Equivalence-Invisible Bug Fixes in Quantum
Transpilers (Qiskit, tket, Cirq)"** (Nasir, Shah, Alam; submitted to the *Journal of Systems and
Software*, Elsevier), and for the `cart` research prototype used by a companion, in-preparation
paper on a fault-class-matched oracle family for the same channels.

- **Repository:** https://github.com/furqan-nr/quantum-observability
- **Archive (DOI):** [10.5281/zenodo.22484774](https://doi.org/10.5281/zenodo.22484774) (Zenodo, archiving GitHub release `v1.0.0`)
- **License:** MIT (see `LICENSE`)

Quantum compilers such as Qiskit's transpiler change constantly, and a single pass modification can
introduce a defect. The field's de-facto correctness check is an **output-equivalence oracle** —
compare the compiled circuit's output map modulo global phase and qubit-layout permutation. The mining
study in this archive shows that criterion is **systematically incomplete**: 19 of 68 merged Qiskit
transpiler bug-fixes (28%, 95% Wilson CI 19-40%), and 29 of 104 in a secondary wider-window check
(27.9%, CI 20-37%), corrupt layout/permutation metadata, break fixed-seed determinism, or drop a
global phase while the output map stays correct, so they are invisible to an output-equivalence
oracle by construction. The same gap replicates in tket (7/21, 33%) and, on a smaller exploratory
sample, in Cirq (2/10, 20%). Equivalence-invisible fixes show no detectable difference from
observable ones on five cheap PR-level surface signals, so they cannot be triaged away by a size or
latency heuristic. `cart` is a separate, leakage-safe evaluation framework that additionally provides
a fault-manifestation taxonomy and a family of fault-class-matched oracles targeting these channels,
built for the companion paper.

## What's inside
- `src/cart/` — the `cart` research prototype: manifest, events, oracles (layout/permutation contract
  differ, metamorphic MR-1, global-phase tracker), labels, metrics, validity gates, and a CLI.
- `data/mining_validation/` — the repository-mining corpus and coding:
  - `labels_final_68.csv` — the 68-fix corpus (19 equivalence-invisible = 28%, 95% Wilson CI 19–40%).
  - `labels_final_104.csv` — secondary robustness check: the 68-fix corpus plus a wider-window,
    independently dual-coded third round of 36 further fixes (29/104 = 27.9% equivalence-invisible, 95%
    Wilson CI 20–37%; see `BATCH_002_CODING_COMPLETE.md`).
  - `rater3_sheet.csv` — a fully independent third coder's labels for all 68 fixes (not pooled into
    the headline R1/R2 kappa); see `scripts/r3_sensitivity_check.py` below.
  - `label_source_validation.csv` — 16 labels source-checked in both directions: 11 primary source validations plus a 5-case symmetric false-negative audit; all 16 agreed with the coded channel.
  - `pr_characterization_raw.csv`, `pr_characterization_summary.csv` — RQ1.3 surface-characteristic
    metadata (size, latency) for the 19 vs 49 comparison; see `scripts/table5_stats.py` below.
  - `tket_worksheet_R1.csv` / `_R2.csv` (n=21, κ=0.77, 7/21=33% equivalence-invisible) and
    `cirq_worksheet_R1.csv` / `_R2.csv` (n=10, κ=0.52, 2/10=20%, exploratory) — cross-SDK replication.
  - human worksheets, adjudication sheets, the frozen codebook, the rater sheets, and signed coder declarations.
- `data/rq14_spotcheck/` and `data/rq14_invisible19_recode/` — RQ1.4 fault-mechanism-category coding
  reliability checks. The first is an earlier, title-level spot-check on a mixed 19-item sample
  (κ=0.41, moderate). The second is a full, diff-level independent recoding of all 19
  equivalence-invisible fixes specifically (κ=0.87, almost-perfect); see `RECODE_RESULTS.md` inside
  it for the adjudicated disagreements.
- `data/events/` — the audited 14-event change-event ledger (`events.csv`/`events.json`, kept in sync and checked by `scripts/validate_ledger.py`); bisection-traced forward-regression candidates pending verification live in `PROVENANCE_BACKLOG.md`.
- `results/` — write-once raw oracle artifacts (source_validation, contract_differ, retro_detect, bisect).
- `environment/` — pinned harness lockfiles and the per-event from-source Qiskit build recipes.
- `scripts/` — reproduction entry points.
- `configs/`, `tests/` — frozen pre-declared configs and the automated test suite.

## Reproduce the headline results
    # 1a. Mining headline: 19/68 = 28% equivalence-invisible (primary 68-fix corpus)
    python -c "import csv; r=list(csv.DictReader(open('data/mining_validation/labels_final_68.csv'))); inv=sum(x['observable']=='no' for x in r); print(f'{inv}/{len(r)} = {round(100*inv/len(r))}% equivalence-invisible')"

    # 1a-confirm. Secondary robustness check: 29/104 = 27.9% equivalence-invisible (68-fix corpus + 36-fix third round)
    python -c "import csv; r=list(csv.DictReader(open('data/mining_validation/labels_final_104.csv'))); inv=sum(x['observable']=='no' for x in r); print(f'{inv}/{len(r)} = {round(100*inv/len(r),1)}% equivalence-invisible')"

    # 1b. Inter-rater agreement (Cohen's kappa) on the 44-fix expansion  (prints kappa; that subset is 8/44)
    python scripts/score_worksheet.py \
        data/mining_validation/human_worksheet_44_R1.csv \
        --rater2 data/mining_validation/human_worksheet_44_R2.csv

    # 1c. Cross-SDK replication: tket (n=21, κ=0.77) and Cirq (n=10, κ=0.52, exploratory)
    python scripts/score_worksheet.py data/mining_validation/tket_worksheet_R1.csv --rater2 data/mining_validation/tket_worksheet_R2.csv
    python scripts/score_worksheet.py data/mining_validation/cirq_worksheet_R1.csv --rater2 data/mining_validation/cirq_worksheet_R2.csv

    # 1d. R1/R2-vs-R3 sensitivity check on the headline rate (94.1% agreement, κ=0.86; R3-alone rate 23/68=33.8%)
    python scripts/r3_sensitivity_check.py

    # 1e. RQ1.3 surface-characteristic comparison (Table 5): Mann-Whitney U, Cliff's delta, bootstrap 95% CI
    python scripts/table5_stats.py

    # 2. Three source-evidenced detections (needs a Rust toolchain to build the per-event
    #    Qiskit revisions from source; cached under environment/_builds when present)
    python scripts/verify_h1_isolated.py          # #14603 contract/metadata
    python scripts/verify_14919_routing.py        # #14919 metamorphic MR-1
    python scripts/source_validate_mining.py --only 14956   # #14956 global phase

    # 3. Label source-validation (16 fixes, both directions) -> data/mining_validation/label_source_validation.csv

    # 4. RQ1.3 characterization: pull PR metadata, then read the summary
    #    (set GITHUB_TOKEN to avoid the API rate limit; a no-scope classic token is enough)
    python scripts/pull_pr_metadata.py
    #    -> data/mining_validation/pr_characterization_{raw,summary}.csv

    # 5. RQ1.4 fault-mechanism-category reliability: title-level spot-check (κ=0.41) is documented in
    #    data/rq14_spotcheck/SPOTCHECK_RESULTS.md; the diff-level recheck on all 19 equivalence-invisible
    #    fixes (κ=0.87) is documented in data/rq14_invisible19_recode/RECODE_RESULTS.md. Both are
    #    human-coding reliability studies, not re-runnable scripts — the worksheets and adjudication are
    #    the artifact.

See `REPRODUCE.md` for the full protocol. Citation metadata is in `CITATION.cff`.
