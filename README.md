# Oracle Observability of Quantum Transpiler Regressions

Reproducibility package for the paper **"Oracle Observability of Quantum Transpiler Regressions:
What Output-Equivalence Oracles Miss — A Cross-SDK Mining Study and a Fault-Class-Matched Oracle
Family for the Output-Invisible Channels (Qiskit, tket, Cirq)."** (under submission)

- **Repository:** https://github.com/<your-user>/quantum-transpiler-observability  (set on first push)
- **Archive (DOI):** to be minted on release (Zenodo)
- **License:** MIT (see `LICENSE`)

Quantum compilers such as Qiskit's transpiler change constantly, and a single pass modification can
introduce a regression. The field's de-facto correctness check is an **output-equivalence oracle** —
compare the compiled circuit's output map modulo global phase and qubit-layout permutation. This work
shows that criterion is **systematically incomplete**: a substantial minority of real transpiler
regressions corrupt layout/permutation metadata, break fixed-seed determinism, or drop a global phase
while the output map stays correct, so they are invisible to an output oracle by construction. We
quantify the gap by repository mining, replicate it across three compilers, and close it with a
fault-class-matched oracle family, all under a leakage-safe evaluation methodology.

## What's inside
- `src/cart/` — the `cart` research prototype: manifest, events, oracles (layout/permutation contract
  differ, metamorphic MR-1, global-phase tracker), labels, metrics, validity gates, and a CLI.
- `data/mining_validation/` — the repository-mining corpus and coding:
  - `labels_final_68.csv` — the 68-fix corpus (19 output-invisible = 28%, 95% Wilson CI 19–40%).
  - `label_source_validation.csv` — 11 labels validated against source (11/11 match the coded channel).
  - `pr_characterization_raw.csv`, `pr_characterization_summary.csv` — RQ1b metadata (size, latency).
  - human worksheets, adjudication sheets, the frozen codebook, and the tket/Cirq cross-SDK worksheets.
- `data/observability_mining.csv` — the mining dataset.
- `results/` — write-once raw oracle artifacts (source_validation, contract_differ, retro_detect, bisect).
- `SLR/` — the pre-registered, PRISMA-based systematic-review protocol and records.
- `environment/` — pinned harness lockfiles and the per-event from-source Qiskit build recipes.
- `scripts/` — reproduction entry points.
- `paper/` — the manuscript (`PAPER.pdf`) and its build source (`build_paper.js`).
- `diagrams/`, `configs/`, `tests/`.

## Reproduce the headline results
    # 1. Mining headline: 19/68 = 28% output-invisible, with Cohen's kappa
    python scripts/score_worksheet.py \
        data/mining_validation/human_worksheet_44_R1.csv \
        --rater2 data/mining_validation/human_worksheet_44_R2.csv

    # 2. Three source-verified detections (needs a Rust toolchain to build the per-event
    #    Qiskit revisions from source; cached under environment/_builds when present)
    python scripts/verify_h1_isolated.py          # #14603 contract/metadata
    python scripts/verify_14919_routing.py        # #14919 metamorphic MR-1
    python scripts/source_validate_mining.py --only 14956   # #14956 global phase

    # 3. Label source-validation (11 fixes) -> data/mining_validation/label_source_validation.csv

    # 4. RQ1b characterization: pull PR metadata, then read the summary
    #    (set GITHUB_TOKEN to avoid the API rate limit; a no-scope classic token is enough)
    python scripts/pull_pr_metadata.py
    #    -> data/mining_validation/pr_characterization_{raw,summary}.csv

See `REPRODUCE.md` and `METHODOLOGY.md` for the full protocol. Citation metadata is in `CITATION.cff`.
