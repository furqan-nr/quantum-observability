# Methodology: Cost-Aware Regression Testing for Qiskit Transpilation

## Problem Statement

Given a Qiskit transpiler change and a fixed CI budget, select and order circuit–backend tests to
maximize early detection of regressions. Regressions fall into three externally reported groups:

- **Correctness**, functional compilation failure + semantic mismatch
- **Quality**, two-qubit gate count / depth degradation
- **Performance**, runtime / memory degradation

The core claim is that a change-aware selector, conceptually scoring each test by
`expected_value ≈ P(regression | change, circuit, backend) × impact / expected_cost`, finds
regressions earlier than random, cheapest-first, diversity-only, history-only, and
change-stage-heuristic baselines under the same budget.

This `P(regression | …)` is the *conceptual* target. The Phase 4 proposed selector does **not**
estimate a calibrated probability; it uses a transparent, interpretable **`risk_score`** (Phase
4.1) as a stand-in for that quantity. A calibrated `P̂(regression | …)` is introduced only in the
optional Phase 6 ML comparison.

---

## Phase 0, Compatibility and Test Manifest

### 0.1 Version Pinning

Record the exact environment (lock file or container image) for every experiment so results are
reproducible from raw artifacts.

**Two-layer version pinning.** A single pinned Qiskit version cannot coexist with historical
event reproduction, because each historical event must run its own `baseline_sha` and
`candidate_sha`, which are, by definition, *different* Qiskit source revisions. Separate the
two layers:

- **Harness layer (fixed for the whole study):** pin Python, the Benchpress revision, the
  measurement/oracle harness, and all non-Qiskit dependencies. Recorded once in
  `environment/requirements.lock` and `environment/ENV.md` (Python version, OS, CPU core count,
  total RAM).
- **Qiskit-under-test layer (per event):** build Qiskit **from source** separately for each
  event's `baseline_sha` and `candidate_sha`. Qiskit is the system under test and must vary by
  event; it is never globally pinned.

**Initial release window.** Restrict historical events to a **single compatible Qiskit release
window** (one major/minor line whose source builds against the fixed harness) so all events share
one harness. Widening the window is a Phase 6 concern.

**Per-event environment record.** Each event records an `event_environment_id` (or a per-event
lockfile) capturing exactly how its baseline and candidate Qiskit were built. Two events that
build the same way may share an `event_environment_id`.

> **Implementation note (initial study).** All experiments run on a single 16 GB laptop,
> single-process, in a ~3-month window. The harness layer is fixed at the start of Phase 0; any
> change to it starts a new, separately tagged experiment run.

### 0.2 Test Unit Definition

The atomic evaluation unit is a 4-tuple:

```
test_unit = (circuit, backend, transpiler_configuration, oracle)
```

Enumerate test units using pytest collection or a Benchpress adapter. Do not use AST parsing
alone; the actual parameterisation of a test may not be visible statically.

### 0.3 Two Manifests: Static vs Calibrated

`baseline_cost_s` and the *actually executed* pass stages cannot be known statically, cost is a
measurement, and which passes run depends on the circuit, backend, transpiler configuration, **and
the specific baseline Qiskit revision** at run time. Split the manifest into two artifacts.

**`test_manifest_static`**, pure metadata, producible before any run (Phase 0):

| Field | Description |
|---|---|
| `test_id` | Stable unique identifier |
| `circuit_family` | e.g. QFT, QAOA, random Clifford |
| `n_qubits` | Circuit width |
| `backend_id` | Target backend |
| `transpiler_config_id` | Transpiler configuration reference |
| `declared_pass_stages` | Pass stages the configuration is *expected* to cover (declarative) |
| `oracle_type` | `unitary` / `sampled_sv` / `property` / `structural` |

**`test_profile_baseline`**, calibrated by an instrumented baseline transpilation run. Because
costs, executed passes, memory, and routing differ across event baselines, this profile is
**event-specific** and keyed by:

```
(event_id, baseline_sha, test_id, event_environment_id)
```

| Field | Description |
|---|---|
| `event_id`, `baseline_sha`, `test_id`, `event_environment_id` | Composite key (above) |
| `cpu_time_s` | Measured **CPU process time** (`time.process_time`) of transpilation, the **cost-calibration metric** (stable on a shared single laptop) |
| `transpilation_time_s` | Wall-clock seconds, secondary reference only (do not use for calibration) |
| `oracle_cost_s` | Measured oracle-evaluation seconds |
| `executed_pass_stages` | Pass stages **actually executed**, captured via pass-manager instrumentation |
| `routing_observations` | Routing/layout observations (e.g. SWAPs inserted, final layout) |
| `peak_memory_mb` | Peak memory observed during the baseline run |

**When profiling happens.** The static manifest and the **instrumentation capability** (plus a
small smoke profile to prove it works) are produced in Phase 0, *before events are known*. The
**real per-event baseline profile is produced in Phase 2**, once the event set exists, Phase 0
does not profile every test against an event baseline that does not yet exist. (See phase order
below.)

**Pass-stage capture.** Determine `executed_pass_stages` from Qiskit pass-manager
instrumentation / a transpile callback during the baseline run. Do **not** infer executed passes
from filenames or static configuration alone, the declarative `declared_pass_stages` may diverge
from what actually runs.

---

## Phase 1, Micro Event Dataset

### 1.1 Event Definition

The dataset unit is a **change event**, not a commit. Running tests across every historical commit
is expensive and most commits do not contain regressions.

```
event = (baseline_revision, candidate_revision, change_metadata, fault_id)
```

Each event must represent either:
- a **known historical regression** reproducible from the Qiskit issue tracker or release notes, or
- a **controlled mutation** with a single injected fault.

Do not label every difference from a release tag as a regression; quality or runtime differences
may be intentional.

**Event cohorts.** Not every historical event is a true forward regression. Each event declares a
cohort, and the three cohorts are **reported separately** (never pooled in a headline number):

```
event_kind        = forward_regression | fix_boundary_differential | mutation
pair_orientation  = forward | reverse_fix_boundary
evaluation_cohort = forward | fix_boundary | mutation
change_metadata_sha = commit whose diff defines change_metadata
```

- **forward_regression** (`pair_orientation = forward`): `baseline = last known-good parent`,
  `candidate = regression-inducing commit`, `change_metadata_sha = candidate`. This is the only
  cohort that models the real CI question "an incoming change introduces a regression."
- **fix_boundary_differential** (`pair_orientation = reverse_fix_boundary`): used when the
  introducing commit is not traced. `baseline = fix commit (fault absent)`,
  `candidate = fix's parent (fault present)`, `change_metadata_sha = fix commit`. This is a
  *fault-revealing differential at a fix boundary*, **not** a forward regression. **Do not** describe
  fix-boundary results as "CI prediction of an incoming regression."
- **mutation**: a controlled single-fault injection on a base revision.

Release tags are used for environment anchoring only, not as the semantic reference for every commit.

**Event date assignment** (drives the temporal split, §5.1):

```
forward_regression   event_date = candidate (introducing) commit timestamp
fix_boundary_diff.    event_date = fix commit timestamp
mutation             event_date = base revision timestamp   # NOT the authoring day
```

Dating a mutation by its authoring day would place it artificially late and corrupt the temporal
ordering; a mutation inherits the chronological position of the base revision it perturbs.

### 1.2 Event Table Schema

Every event is recorded in a structured table used to enforce the temporal train/test split and
prevent data leakage.

| Field | Type | Notes |
|---|---|---|
| `event_id` | string | Unique |
| `baseline_sha` | string | |
| `candidate_sha` | string | |
| `fault_id` | string | `qiskit-issue-NNNN` or `mut-<name>-NN` |
| `fault_source` | enum | `historical` / `mutation` |
| `fault_type` | enum | `functional` / `semantic` / `quality` / `performance` |
| `event_environment_id` | string | Build recipe for this event's baseline/candidate Qiskit (Phase 0.1) |
| `split_group_id` | string | Leakage group; see §1.6. All events sharing it stay in one split |
| `event_kind` | enum | `forward_regression` / `fix_boundary_differential` / `mutation` (§1.1) |
| `pair_orientation` | enum | `forward` / `reverse_fix_boundary` |
| `evaluation_cohort` | enum | `forward` / `fix_boundary` / `mutation`, reported separately |
| `change_metadata_sha` | string | Commit whose diff defines `change_metadata` |
| `event_date` | date | Determines train/test assignment |
| `train_or_test` | enum | `train` / `test` |

The primary evaluation unit throughout all phases is the `(event_id, test_id)` pair.

### 1.3 Fault ID Requirements

Every fault must have an explicit, unique `fault_id`. Defining a fault as only
`(commit_sha, regression_type)` produces at most three faults per commit and makes APFDc
nearly meaningless.

```
fault_id   — unique string (e.g. "qiskit-issue-9821", "mut-cx-cancel-01")
fault_type — {functional, semantic, quality, performance}
```

A test detects a specific fault, not merely "a regression somewhere."

### 1.4 Target Dataset Size

Micro corpus: **8–12 regression events** for initial validation.
Prefer known historical regressions. Supplement with carefully designed mutations **only** where
history is insufficient or not reproducible, mutations fill gaps in regression-type coverage,
they do not replace historical events.

**Separate reporting.** Historical and mutation events must be tagged via `fault_source`
(Phase 1.2) and reported **separately** in every result table, never pooled into a single
headline number. The two sources have different external validity: historical events test
real-world fidelity, mutations test controlled coverage. All conclusions state which source(s)
they rest on.

**Pilot framing.** The 8–12 event micro corpus is a **feasibility / pilot study**, not final
evidence that the selector universally outperforms baselines. Frame all claims accordingly: report
**individual-event outcomes alongside averages** (a single aggregate over so few events hides
high variance), and treat strong general claims as deferred to the Phase 6 expansion, where a
larger corpus makes them credible.

### 1.5 Mutation Guidelines

Permitted mutation types:

- Omit a cancel/merge optimisation pass
- Insert a redundant gate pair (e.g. CX–CX)
- Corrupt a routing heuristic parameter
- Disable a peephole reduction

**Do not** use "remove Barrier before measurement" as a semantic mutation. Barriers do not
change circuit semantics; they constrain optimisation/transformation order. Removing them
produces at most an ordering or quality change, not a semantic regression.

### 1.6 Split-Group Leakage Control

Mutation events derived from the same operator or the same base revision are **not independent**:
placing close variants on opposite sides of the temporal split leaks structure across train/test.
Assign every event a `split_group_id`:

```
split_group_id = base_revision + mutation_family
```

(Historical events use their `base_revision` alone as the group; each is typically its own group.)
**All events sharing a `split_group_id` must fall entirely within train or entirely within test**,
the temporal split (Phase 5.1) is applied at the group level, never splitting a group. Where a
group straddles the cutoff date, assign the whole group to test (the more conservative choice).

---

## Phase 2, Ground-Truth Execution

Phase 2 runs once the events from Phase 1 exist. It produces, per event: (a) the **per-event
baseline profile** (`test_profile_baseline`, keyed by `(event_id, baseline_sha, test_id,
event_environment_id)`, see §0.3) by running the instrumented baseline transpilation, and (b) the
**candidate ground-truth labels** by running the candidate and applying the oracles below. The
Phase 0 smoke profile only verified the instrumentation works; the authoritative baseline profile
is built here against each event's actual baseline revision.

### 2.1 Internal Regression Labels

Use **four internal labels** collapsed to three for reporting:

| Internal label | Reported group | Notes |
|---|---|---|
| Functional (compilation failure) | Correctness | Crash, exception, invalid output circuit |
| Semantic mismatch | Correctness | Circuit computes different unitary/output |
| Circuit-quality degradation | Quality | 2Q gate count or depth worsens |
| Compilation-performance degradation | Performance | Runtime or memory worsens |

A transpilation crash is **not** necessarily a semantic regression. Label them separately.

### 2.2 Semantic Oracle Tiers

Direct statevector comparison at 30 qubits is unsafe on a 16 GB machine: a complex float64
statevector at 30 qubits is approximately 16 GB before overhead, and unitary matrices become
infeasible much earlier. Use tiered oracles:

| Circuit size | Oracle method |
|---|---|
| ≤ 10–12 qubits | Unitary equivalence, modulo global phase |
| ≤ 20–22 qubits | Sampled statevector equivalence on several input states, modulo global phase |
| Larger circuits | Structural validity + metamorphic / property checks + sampled observable checks where feasible |

**Oracle applicability (not just size).** Unitary and pure-statevector equivalence are only valid
for circuits with **no measurement, reset, or classical control flow**, these operations are
non-unitary and break the unitary/statevector model. The width tiers above apply *only* to such
unitary-pure circuits. For circuits containing measurement, reset, or classical control, use,
regardless of width:

- output-distribution equivalence (e.g. total-variation / statistical distance over sampled
  outcomes), or
- expectation-value / observable equivalence on a declared observable set, or
- metamorphic relations, or
- structural validity checks.

Record which applicability class a test falls in so oracle choice is auditable.

**No global circuit-width cap.** The width limits above restrict only which *semantic* oracle
tier applies. Larger Benchpress circuits are **retained** in the corpus and exercised for
structural/property checks, circuit-quality evaluation (Phase 2.3), and performance evaluation
(Phase 2.5). Only exact unitary/statevector equivalence is width-bounded; larger circuits simply
fall to property/structural oracles rather than being excluded.

**Layout normalisation:** A transpiled circuit may permute physical qubits. Direct statevector
comparison must normalise the final qubit layout/permutation before comparison to avoid false
alarms.

Each `(event_id, test_id)` pair must record:

```
oracle_strength              ∈ {exact, sampled, property, structural}
oracle_cost_s                — wall-clock seconds for oracle evaluation
layout_normalization_applied — boolean
```

The total CI cost of a test includes oracle cost:

```
total_cost_s = cpu_time_s + oracle_cost_s      # cost calibration uses CPU process time
```

**Cost calibration uses CPU process time, not wall-clock.** On a shared single laptop, wall-clock is
noisy (descheduling, background load). All cost calibration, `baseline_cost_s`, `expected_cost`,
and the cost axis of the detection-vs-budget metrics, uses `time.process_time`. Wall-clock is
recorded only as a secondary reference. (Where Qiskit parallelizes in Rust, process time sums across
threads; this is stable and acceptable as a relative cost proxy for selection.)

### 2.3 Quality Regression Definition

A 10% increase in two-qubit (2Q) gates is not always a regression if depth drops substantially.
Use a **Pareto-style rule**:

**Pre-declared thresholds.** "Materially" must be quantified by explicit thresholds chosen
**before** the held-out evaluation, derived from training events only, or pre-registered in
`configs/thresholds.yaml` with a justification, and never tuned after seeing held-out results.
Define at minimum:

```
τ_2q            — relative 2Q-count degradation threshold (e.g. +10%)
τ_depth_improve — relative depth-improvement threshold that offsets 2Q degradation
τ_depth         — relative depth-degradation threshold
τ_2q_improve    — relative 2Q-improvement threshold that offsets depth degradation
```

**Quality regression if either of the following holds:**

1. `Δ2Q ≥ τ_2q` **and** `depth improvement < τ_depth_improve`, or
2. `Δdepth ≥ τ_depth` **and** `2Q improvement < τ_2q_improve`.

> **Pilot scope.** The earlier optional rule 3 (a *weighted quality utility score*) is **dropped
> for the pilot**: rules 1–2 with pre-declared threshold grids are sufficient and more defensible,
> and a utility score would require committing to exact weights now. A utility-based rule may be
> reintroduced in Phase 6 only with its formula and weights pre-declared.

Report both metrics (Δ 2Q count, Δ depth) separately in all result tables; do not collapse them
to a single threshold without justification. Run **sensitivity analysis across the pre-declared
threshold grid** and report how labels move with the threshold. Final thresholds are fixed before
held-out evaluation; the held-out set is never used to choose them.

### 2.4 Topology Feature

Replace:

```
topology_mismatch = n_qubits / backend_n_qubits   ← remove this
```

with a circuit-interaction vs coupling-map feature. Options in increasing fidelity:

- Connectivity pressure, number of circuit interaction edges that are non-adjacent in the
  coupling graph
- Estimated interaction-edge distance, mean shortest-path distance over circuit CX pairs
- Embedding difficulty score, ratio of required to available coupling edges in the subgraph

Pick one metric, motivate the choice, and use it consistently.

> **Implementation note (initial study).** The initial study uses **connectivity pressure**,
> the count of circuit interaction edges that are non-adjacent in the backend coupling graph.
> Rationale: it is computed directly from the circuit's two-qubit interaction graph and the
> coupling map without any shortest-path or subgraph-embedding search, so it is the cheapest of
> the three options on a single laptop while still capturing layout difficulty. The richer
> distance/embedding metrics are recorded as candidates for the Phase 6 scale-up.

> **Interpretation constraint.** `connectivity_pressure` is a **pre-layout risk proxy**, not a
> measurement of actual routing difficulty: it estimates how hard placement *may* be before any
> layout pass runs. Its computation must declare the assumed placement rule (e.g. trivial/identity
> layout, or the configuration's default layout pass *as declared*, computed without running it)
> and whether coupling-map edge **direction** is considered. Actual routing difficulty (SWAPs
> inserted, final layout) is observed post-hoc and recorded in `test_profile_baseline`
> (`routing_observations`), it is an evaluation observation, never a selection-time input.

### 2.5 Performance Regression Statistics

> **Scope note (initial study).** During the micro-corpus phase, performance regression
> detection is treated as **exploratory**: single-laptop runtime/memory measurements are noisy
> and require Stage-2 confirmation before any claim. Performance remains a **reported research
> dimension**, it is not dropped, but micro-corpus performance findings are presented as
> preliminary, with the full two-stage screening/confirmation protocol below applied and the
> firmer performance conclusions deferred to the Phase 6 scale-up on more controlled hardware.

**Timing metric.** Performance comparisons use **CPU process time** (`time.process_time`) as the
primary, more stable measurement on a shared single laptop; wall-clock is recorded as a secondary
reference. Memory uses peak allocation.

Three candidate runs vs three reference runs cannot reliably support a two-sided Mann–Whitney
U test at p < 0.05; that requirement is effectively unachievable at that sample size. Use a
**two-stage process**:

**Stage 1, Screening (3 runs):**

- Compare medians against a pre-defined slowdown threshold (e.g. 20% slowdown, justified by
  expected noise floor).
- Flag events that exceed the threshold as suspected regressions.

**Stage 2, Confirmation (7–10 runs, suspected regressions only):**

- Bootstrap confidence interval or robust effect-size test (e.g. Hodges–Lehmann estimator).
- Report effect size alongside the confidence interval.

For deterministic semantic and quality checks, one run per baseline/candidate is sufficient.
Repetitions are reserved for runtime and memory claims.

**System load normalisation:**

```
normalized_load = load_average / CPU_core_count
```

Use this in place of a raw system load threshold. Runs with `normalized_load > 0.3` should be
flagged for exclusion or rerun.

### 2.6 Ground-Truth Label Record

For every `(event_id, test_id)` pair record:

| Field | Values |
|---|---|
| `fault_id_detected` | `fault_id` string, or `null` |
| `oracle_strength` | `exact / sampled / property / structural` |
| `oracle_artifact` | Path or content hash of raw evidence |
| `label` | `pass / functional_fail / semantic_fail / quality_regression / performance_regression` |
| `confirmed` | boolean, warning upheld by independent confirmation (see below) |

**Empirical oracle false-positive rate.** The oracle FP rate (reported in Phase 5.2) must be
**empirical, not circular**. A regression warning may not be counted as a false positive merely
because some check fired, the oracle that produced the label cannot also adjudicate it. A warning
is a false positive **only if** it fails independent confirmation: it is contradicted by a
*stronger* oracle (e.g. a sampled warning overturned by exact unitary equivalence on a feasible
subcase), or it does not reproduce under an independent re-run / metamorphic cross-check. Record
the confirmation outcome in `confirmed`; the FP rate is computed over confirmed-vs-unconfirmed
warnings, not over raw oracle firings.

---

## Phase 3, Baselines

Implement and evaluate five baselines. All observe the same declared CI budget per event.

| Baseline | Strategy |
|---|---|
| Random | Uniform random sample up to budget |
| Cheapest-first | Sort by `baseline_cost_s` ascending |
| Diversity-only | Maximise coverage across circuit families and topologies |
| History-only | Rank by historical failure rate across all prior change events |
| Change-stage heuristic | Prefer tests that exercise the modified transpiler pass stage |

---

## Phase 4, Proposed Transparent Selector

### 4.1 Risk Score

The first proposed selector is **transparent and interpretable**, a heuristic, not a calibrated
probability model. Its output is therefore named `risk_score`, not a probability; the calibrated
`P̂(regression | …)` is reserved for the optional Phase 6 ML comparison.

```
risk_score(test | event) =
    (ε + change_stage_match(test, change))
  × circuit_backend_sensitivity(test, change)
  × impact_prior(test)
  × oracle_confidence(test)
  ÷ expected_cost(test)
  × novelty_multiplier(test, already_selected)
```

Component definitions:

| Component | Definition |
|---|---|
| `change_stage_match` | 1.0 if test exercises a modified pass stage; scaled by overlap degree otherwise. Mapped via `configs/stage_map.yaml` (§4.4) |
| `ε` | Small positive floor so a test never scores zero from stage mismatch alone (see exploration reserve below) |
| `circuit_backend_sensitivity` | Function of circuit family, n_qubits, 2Q density, topology feature, diff size/type |
| `impact_prior` | Pre-execution **severity** prior, how bad a fault here *would* be, independent of detectability |
| `oracle_confidence` | **Detection confidence**: how decisively this test's oracle could expose a fault (stronger oracle ⇒ higher) |
| `expected_cost` | `baseline_cost_s + oracle_cost_s` |
| `novelty_multiplier` | Diversity term: down-weights overlap with already-selected tests on circuit family and topology |

**Impact and oracle strength are separate factors.** Oracle strength is *detection confidence*
(how reliably a fault would be caught), **not** fault severity. Conflating them double-counts the
oracle and undervalues high-impact tests that happen to use weaker oracles. They enter as distinct
multiplicands: `impact_prior` (severity) and `oracle_confidence` (detectability).

**No label leakage.** None of these components uses the candidate's `fault_type`, runtime, quality
metrics, or outcome (§4.3). `impact_prior` is built only from pre-execution signals: circuit
criticality (family/role importance), backend/topology stress (`connectivity_pressure`-based), and
`historical_stage_conditioned_impact`, the severity of past faults on the modified stage, computed
from events strictly before `event_date` (with the cold-start fallback of §4.3). The true
`fault_type` and observed severity are used **only post-hoc** to weight reporting (e.g.
severity-weighted recall), never to rank.

**Exploration reserve.** A wrong or incomplete pass-stage mapping must not zero out otherwise
valuable tests. Guard against this two ways: the `ε` floor above, **and** reserving **10–20% of
each event's budget for stage-independent diversity**, tests selected by sensitivity/novelty
regardless of `change_stage_match`. Unknown or global changes (`passmanager_global`,
`shared_utility_unknown` in §4.4) route into this reserve rather than being scored against a single
assumed stage.

### 4.2 Budgeted Selection

1. Split the budget: reserve **10–20% for stage-independent exploration**; the remainder is the
   `risk_score`-ranked main allocation.
2. Score all candidate tests with `risk_score` (§4.1).
3. Fill the main allocation greedily in descending `risk_score` order until that sub-budget is
   exhausted.
4. Fill the exploration reserve by sensitivity/novelty alone (ignoring `change_stage_match`),
   covering circuit families/topologies under-represented so far and any `passmanager_global` /
   `shared_utility_unknown` changes.
5. Apply a diversity constraint: ensure at least one representative per circuit family present in
   the full test suite, budget permitting.
6. The selector must never exceed the declared budget (reserve + main ≤ budget).
7. Given the same random seed, the selector must produce identical rankings. Record seeds per
   event.

### 4.3 Data Leakage Prevention

At selection time the selector may use **only**:

- Candidate change metadata (modified modules, pass stages, diff size, diff type)
- Test metadata from the manifest (circuit family, n_qubits, backend, pass stage coverage)
- Baseline-version test costs
- Historical data strictly **before** `event_date`

The selector must **never** use:

- Candidate transpilation runtime
- Candidate quality metrics
- Candidate output labels

**Cold-start fallback.** With only 8–12 events, many events will have no prior qualifying
historical events on the modified stage. When that happens:

```
historical_stage_conditioned_impact = 1.0   # neutral
```

This neutral fallback is fixed **before** evaluation and never tuned afterwards. It ensures a
test is neither rewarded nor penalised for an empty history, so early events are not silently
down-ranked.

### 4.4 Pass-Stage Mapping Artifact

`change_stage_match` requires mapping a change's modified Qiskit files/modules to canonical
transpiler stages. This mapping is an explicit, version-controlled artifact:

```
configs/stage_map.yaml
```

It maps modules/paths to a fixed set of canonical stages:

```
layout
routing
translation
optimization
scheduling
analysis
passmanager_global        # changes affecting the pass-manager framework itself
shared_utility_unknown    # shared utilities / unmapped or ambiguous paths
```

**Handling global/unknown changes.** For `passmanager_global` or `shared_utility_unknown`, the
selector must **not** assume a single specific stage. Such changes are treated as broad-coverage:
they route into the §4.2 exploration reserve rather than concentrating `change_stage_match` on one
stage. The mapping is validated against the actual `executed_pass_stages` captured during baseline
profiling (§0.3).

**Freeze before held-out evaluation.** `configs/stage_map.yaml` carries a `frozen: true` marker and
a `version`. It must be **frozen before any held-out (test-split) evaluation**. Any refinement may
use **training-split events only**, must bump the version and be committed, and may **never** use
observations from test-split events. This prevents the stage mapping from quietly absorbing
information from held-out events.

---

## Phase 5, Held-Out Evaluation

### 5.1 Temporal Split

```
training set: events where event_date <  cutoff_date
test set:     events where event_date >= cutoff_date
```

No label, cost, or outcome from a test-split event may appear in any training feature or
historical aggregation.

The split is applied at the **`split_group_id`** level (Phase 1.6), never at the individual-event
level: all events sharing a `split_group_id` go to the same side. A group that straddles
`cutoff_date` is assigned wholly to the test split. This prevents mutation variants from the same
operator or base revision leaking across the boundary.

### 5.1.1 Test provenance and two evaluations (no post-fix leakage)

A test extracted from a fix PR often **did not exist when the buggy candidate was introduced**, so
counting it as a test the selector "could have run in CI" to catch that regression is leakage. Every
test unit therefore declares provenance:

```
test_provenance          = pre_existing | extracted_from_fix | synthesized
test_available_sha       = first commit at which the test existed
available_before_candidate = true | false   (test_available_sha is an ancestor of candidate_sha)
```

Generic Benchpress units are `pre_existing` (available before any candidate). Targeted regression
triggers taken from a fix are `extracted_from_fix` with `available_before_candidate = false`.

Two evaluations, reported separately and never conflated:

- **Primary CI evaluation**, the headline "given a new change, select existing CI tests" claim.
  Candidate test pool is restricted to units with `available_before_candidate = true`. Post-fix
  targeted triggers are **excluded**.
- **Secondary retrospective fault-revealing evaluation**, generic Benchpress distractors **plus**
  targeted triggers extracted from a later fix. This shows the fault is real and that a strong
  trigger is detectable, but it is **not** evidence the selector would have caught the fault in real
  CI. Label it retrospective.

A targeted trigger may verify a historical fault exists; it must never enter the Primary CI metric.

### 5.2 Metrics

Because each change event typically has **one `fault_id` and its own per-event ranking**, APFDc,
which assumes multiple faults exposed by a *single common ordering*, is not meaningful merely
because a split contains three faults across different events. The primary and secondary metrics
are therefore detection-curve based, computed per event and averaged across events.

| Metric | When to report | Notes |
|---|---|---|
| Recall@budget | Always, primary | Fraction of faults found within budget |
| TTFR / normalized TTFR | Always, primary | Wall-clock time to first detected fault; normalized TTFR divides by full-suite time for cross-event comparability |
| Detection rate @ {5, 10, 20, 40}% budget | Always, primary | Fraction of faults detected at fixed budget fractions |
| Area under detection-vs-budget curve | Always, primary | Per-event AUC of detection rate vs budget fraction; averaged across events |
| Selection overhead (seconds) | Always | Time taken by the selector itself |
| Oracle false-positive rate | Always | Empirical: warnings not upheld by independent confirmation (Phase 2.6), not raw oracle firings |
| Diversity coverage | Secondary | Fraction of circuit families represented in the selected set |
| NAPFDc / APFDc | Only for an event with **multiple independent faults exposed by one ordered suite** | Not applicable to single-fault-per-event ranking; do not report just because a split has ≥3 faults |

### 5.3 Implementation-Validity Gates

These gates must pass before any result is reported. They are **not** outcome thresholds,
they verify implementation correctness.

| Gate | Check |
|---|---|
| Budget compliance | Selector never exceeds declared budget on any event |
| Reproducibility | Same seed → same ranking on every event |
| Leakage absence | No future-event data appears in training features |
| Label reproducibility | Labels reproduce from raw oracle artifacts |
| Metric correctness | Metric code matches hand-computed examples on ≥ 2 small cases |
| Oracle coverage | Every `(event_id, test_id)` pair has `oracle_strength` and `oracle_artifact` recorded |

Whether the proposed selector outperforms baselines is the **empirical result** of the study,
not a prerequisite for proceeding or publishing. Acceptance gates must not be framed as
outcome guarantees (e.g. "proposed must beat all baselines on 70% of commits" is not valid).

### 5.4 Claim-Scope Rule (pilot)

A small corpus supports feasibility evidence, not general superiority, and only the
**forward_regression** cohort models real CI. Therefore:

```
If fewer than THREE independently verified historical forward_regression events exist in the
held-out cohort, do NOT make a headline comparative-effectiveness claim for temporal
generalization. Report per-event outcomes and classify the result as PILOT EVIDENCE.
```

This is binding here because the current historical set is dominated by **fix_boundary_differential**
events (H1–H3, H5), which are not forward regressions; the only forward_regression is H4. Until ≥3
forward-regression events are verified in the test split, comparative claims are pilot-scoped, per
cohort, and per event.

---

## Phase 6, Scale-Up and Optional ML Comparison

> **Scope note.** Phase 6 is the **planned scale-up phase** of this research and remains part of
> the methodology. It is **deferred beyond the initial ~3-month, single-laptop study**, which
> concludes at the end of Phase 5 (micro-corpus, validity gates passed). Phase 6 is executed once
> the transparent selector is validated on the micro corpus and more compute is available.

### 6.1 Scale-Up

After the transparent selector is validated on the micro corpus:

- Expand the event dataset and the Benchpress test suite.
- Re-run all baselines and the transparent selector on the expanded corpus.
- Re-verify all implementation-validity gates on the expanded run.

### 6.2 ML Comparison (optional)

Introduce logistic regression or gradient-boosted tree comparison **only if**:

- The transparent heuristic is stable and validated on the micro corpus.
- The expanded corpus has sufficient events to train without overfitting and evaluate on a
  held-out test split.

ML models must obey the same leakage rules. They are evaluated as a comparison to the
transparent selector, not as the primary proposed method.

---

## CI Tier Definitions

| Tier | Typical budget | Scope |
|---|---|---|
| PR | Tight (minutes) | Top-scored tests per change, high `change_stage_match` |
| Nightly | Moderate (hours) | Broader set; includes performance screening runs |
| Release | Full suite | All oracle tiers; full confirmation runs for performance |

---

## Reporting Summary

| Reported group | Internal labels | Metrics |
|---|---|---|
| Correctness | functional + semantic | Recall, TTFR, oracle FP rate |
| Quality | circuit-quality degradation | Recall, TTFR, Δ 2Q count, Δ depth (both reported) |
| Performance | compilation-performance degradation | Recall, TTFR, effect size, CI from stage-2 runs |

---

## Appendix A, Initial-Study Scope Decisions

These decisions constrain the **initial ~3-month, single-laptop (16 GB) study** only. They
narrow execution scope; they do **not** alter the research question, regression definitions,
oracle rules, evaluation design, or phase order. Each is recorded here for reproducibility.

| # | Decision | Status of underlying methodology |
|---|---|---|
| 1 | Run all initial experiments on one 16 GB laptop, single-process. Pin the **harness** (Python, Benchpress, oracle harness, deps) for the whole study; build **Qiskit per event** from its baseline/candidate source; restrict historical events to one compatible Qiskit release window. | Phase 0.1, two-layer pinning. |
| 2 | Prefer reproducible historical regressions; use mutations only to fill missing regression-type coverage; report historical vs mutation results **separately**. | Phase 1.4 emphasis preserved; separate-reporting added. |
| 3 | No global circuit-width cap. Exact semantic oracles stay width-bounded as specified; larger circuits retained for structural/property, quality, and performance evaluation. | Phase 2.2 tier rules unchanged. |
| 4 | Topology feature = **connectivity pressure** (cheapest option), used as a pre-layout risk proxy. | Phase 2.4 ("pick one metric") satisfied. |
| 5 | Performance treated as **exploratory** during the micro corpus (noisy single-laptop timing); two-stage protocol still applied; performance retained as a reported dimension. | Phase 2.5 protocol unchanged. |
| 6 | Phase 6 (scale-up + optional ML) **deferred** beyond the initial study but retained in full as the planned scale-up phase. | Phase 6 retained; phase order unchanged. |

## Appendix B, Pre-Implementation Correctness Fixes

Correctness fixes applied before implementation. These resolve internal contradictions and
leakage risks; they refine *how* the methodology's principles are realised without changing the
research question or phase order.

| # | Fix | Sections |
|---|---|---|
| 1 | **Versioning contradiction resolved.** Two-layer pinning: fixed harness + per-event Qiskit builds + `event_environment_id`; historical events confined to one release window. | §0.1, §1.2 |
| 2 | **Manifest split.** `test_manifest_static` (metadata) vs `test_profile_baseline` (measured cost, oracle cost, executed pass stages, routing, memory). Executed pass stages via pass-manager instrumentation, not filenames. | §0.3 |
| 3 | **`expected_impact` de-leaked.** Replaced `fault_type`-severity weighting (unknown pre-execution) with oracle strength × circuit criticality × backend/topology stress × historical stage-conditioned impact. `fault_type` used post-hoc only. | §4.1, §4.3 |
| 4 | **Metric suite corrected.** Primary: Recall@budget, (normalized) TTFR, detection rate @ 5/10/20/40% budget, AUC of detection-vs-budget. APFDc restricted to true multi-fault-per-ordering events. | §5.2 |
| 5 | **Quality thresholds pre-declared.** `τ_2q`, `τ_depth`, `τ_depth_improve`, `τ_2q_improve` fixed from training/pre-registration before held-out evaluation; sensitivity over the pre-declared grid. | §2.3 |
| 6 | **Oracle rules tightened.** Unitary/statevector only for circuits without measurement/reset/classical control; non-unitary → distribution/observable/metamorphic/structural; empirical (non-circular) oracle FP rate via independent confirmation; `connectivity_pressure` = pre-layout proxy with declared placement rule and edge-direction handling. | §2.2, §2.4, §2.6, §5.2 |
| 7 | **Mutation-leakage prevented.** `split_group_id = base_revision + mutation_family`; all same-group events stay entirely in train or test; group-level temporal split. | §1.6, §5.1 |

## Appendix C, Pilot-Hardening Refinements

A second round of refinements after Appendix B, hardening the pilot against implementation
confusion and over-claiming. No change to the research question or phase order.

| # | Refinement | Sections |
|---|---|---|
| 1 | **Event-specific baseline profile.** `test_profile_baseline` keyed by `(event_id, baseline_sha, test_id, event_environment_id)`, cost/passes/memory/routing differ per event baseline. | §0.3, §2 |
| 2 | **Phase order clarified.** Phase 0 builds the static manifest + instrumentation capability + small smoke profile; the authoritative per-event baseline profile is built in Phase 2, after events exist. | §0.3, §2 |
| 3 | **Phase-4 score is `risk_score`, not a probability.** `P̂(regression\|…)` reserved for optional Phase 6 ML. `impact_prior` (severity) and `oracle_confidence` (detectability) separated. | Problem Statement, §4.1 |
| 4 | **Exploration reserve + ε floor.** 10–20% of budget for stage-independent diversity; small ε so stage-mismatch alone never zeroes a test; unknown/global changes route to the reserve. | §4.1, §4.2 |
| 5 | **Stage-map artifact.** `configs/stage_map.yaml` maps modules to canonical stages incl. `passmanager_global` and `shared_utility_unknown`. | §4.4 |
| 6 | **Event-date rules.** Historical = candidate commit timestamp; mutation = base revision timestamp (not authoring day). | §1.1 |
| 7 | **Cold-start fallback.** `historical_stage_conditioned_impact = 1.0` (neutral, fixed pre-eval) when no prior qualifying events. | §4.3 |
| 8 | **Quality rule 3 dropped for pilot.** Keep Pareto rules 1–2 with pre-declared grids; utility-score rule deferred to Phase 6 with pre-declared weights. | §2.3 |
| 9 | **Pilot framing.** 8–12 event corpus is a feasibility study; report per-event outcomes alongside averages; defer general claims to Phase 6. | §1.4 |

## Appendix D, Targeted Regression-Trigger Units (clarification)

Narrow clarification, not a change to the research question or evaluation design. **Targeted
regression-trigger units** (`test_origin = "targeted_regression_trigger"`) are small, deterministic
circuits, drawn from each fix PR's own regression test, that exercise a specific historical
fault's bug path so the fault is *observable*. They **complement** the generic Benchpress circuit
families for fault observability; they do **not** replace them and are **not** the sole evaluation
corpus. They are kept in a separate category and never pooled with generic units in data or
reporting (`data/manifest_static/targeted_triggers.json`, `src/cart/manifest/targeted.py`). The
selector and oracle pipeline are identical to the generic path. Because several historical faults
existed only in dev commits between releases (never shipped in a release wheel), a targeted unit is
only deemed to *verify* an event after it triggers the buggy candidate build and **not** the fixed
baseline build (the local from-source step).

## Appendix E, External-Review Validity Fixes

Changes from an external methodology review, strengthening validity. No change to the research
question or phase order.

| # | Fix | Sections |
|---|---|---|
| R1 | **Fix-boundary cohort made explicit.** `event_kind` / `pair_orientation` / `evaluation_cohort` / `change_metadata_sha` defined; forward vs fix-boundary vs mutation reported separately; fix-boundary results are NOT described as CI prediction of an incoming regression. | §1.1, §1.2 |
| R2 | **Targeted-trigger leakage closed.** `test_provenance` / `test_available_sha` / `available_before_candidate`; Primary CI evaluation restricted to tests available before `candidate_sha`; post-fix targeted triggers used only in a Secondary retrospective evaluation. | §5.1.1 |
| R3 | **stage_map frozen before held-out.** `frozen: true` + version; refinement on training events only, versioned, never on test-split observations. | §4.4 |
| R4 | **Pilot claim-scope rule.** < 3 verified historical forward_regression events in the held-out cohort ⇒ no headline comparative-effectiveness claim; report per-event, classify as pilot evidence. | §5.4 |

## Appendix F, Cost Measurement Stability

External-review fix: cost calibration on a shared single laptop must not rely on wall-clock time.

| # | Fix | Sections |
|---|---|---|
| F1 | **CPU process time for cost calibration.** `cpu_time_s` (`time.process_time`) is the cost-calibration metric for `baseline_cost_s`, `expected_cost`, `total_cost_s`, and the cost axis of the detection-vs-budget metrics; wall-clock (`transpilation_time_s`) is recorded only as a secondary reference. Performance screening (§2.5) also uses process time. | §0.3, §2.2, §2.5, §4.1 |
