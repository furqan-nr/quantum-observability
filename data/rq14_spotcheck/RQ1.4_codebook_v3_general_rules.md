# RQ1.4 mechanism-category codebook — v3 revision (specificity-ordering fix)

**Status: FROZEN (2026-09-19).** Written after Round 2 (codebook v2) came back with a diagnosable
ordering flaw. Round 1 (κ=0.590) and Round 2 (κ=0.572, invisible-subset κ=0.741, observable-subset
κ=0.481) results are both preserved unchanged. The decision order below was independently applied
by both coders (Furqan and Atif) to the 26 fixes disputed across Rounds 1-2: 23 of 26 (88.5%)
converged without either seeing the other's answer, and the remaining 3 were resolved by joint
discussion of the underlying diff (§"Final joint-review additions" below). Both coders confirmed the
result and asked to freeze rather than continue revising individual labels. No further changes to
this codebook are expected; any future fresh-coder reliability round (see the main project memory)
applies v3 as written here, unchanged.

## What Round 2 showed

Round 2's overall kappa did not improve (0.590 → 0.572), but the two subsets moved in opposite
directions: the invisible subset (n=19, the fixes central to this paper's headline-adjacent claim)
improved from κ=0.620 to κ=0.741; the observable subset (n=49) fell from κ=0.549 to κ=0.481. Six
Round-1 agreements became Round-2 disagreements. Two of those six (PRs coded `commutation_checker_defect`
and `global_phase_bookkeeping` under diff-verified evidence) were re-coded in Round 2 as
`cross_representation_conversion`.

## The mechanism-level problem (not a coder-specific one)

Codebook v2's decision order tested `cross_representation_conversion` (a general, shape-based
category: "does a value cross between two representations or index spaces?") before it tested the
domain-named categories `commutation_checker_defect` and `global_phase_bookkeeping` (categories
defined by WHICH subsystem or property is defective, not by the shape of the code change).

This ordering has a structural weakness independent of any specific fix. Domain-named categories
are logically narrower: they require the defect to be *about* a specific, identifiable subsystem
(commutation analysis, global-phase tracking) or property (iteration order, cached state). Shape-
based categories are logically broader: they describe *how the code changed* (a value now crosses a
boundary it didn't cross before, or is copied/propagated somewhere) without reference to which
subsystem is involved. Almost any fix that touches a domain-specific subsystem will, incidentally,
also involve some value being read, copied, or propagated — which is enough surface similarity to
satisfy a shape-based category's test even when the domain-named category is the fix's true subject.
When a broader, shape-based test is checked before a narrower, subsystem-named one, the broader
category will systematically out-compete the narrower one on exactly the fixes the narrower category
exists to catch. This is a property of the categories' relative specificity, not of any individual
PR, and it would recur on a fresh corpus regardless of which coders apply the rules.

The same reasoning applies, to a lesser extent, to `nondeterministic_ordering` and
`stateful_reuse_or_global_cache`, both of which were positioned late in the v2 order (immediately
before the `logic_error_pass_specific` last resort). One Round-1 agreement on
`stateful_reuse_or_global_cache` regressed to `logic_error_pass_specific` in Round 2 — the more
general catch-all was reached before the specific, order/state-named rule was properly considered.

## The fix: order by specificity, domain-named categories first

Categories are re-ordered from most specific (named for a single, identifiable subsystem or
property) to most general (a catch-all for pass-specific logic errors that fit nothing else). At
each step, the question is whether *this* fix's defect is literally, primarily about the named
subsystem or property — not whether that subsystem or property is merely touched somewhere in the
diff.

**Revised decision order:**

1. Is the defect specifically inside commutation-analysis logic (whether two gates commute)? →
   `commutation_checker_defect`.
2. Is the defect specifically about tracking, accumulating, or propagating the circuit's global
   phase? → `global_phase_bookkeeping`.
3. Is the defect specifically that a Rust port of a previously-Python pass dropped bookkeeping the
   Python version kept, with positive historical confirmation (e.g. git blame) that a port commit
   introduced the loss? → `rust_port_metadata_loss`. Without that historical confirmation, fall
   through to step 6.
4. Is the defect specifically that iteration/traversal order is unstable across runs (hash order,
   set/dict order, graph-edge order, time-budgeted search)? → `nondeterministic_ordering`. Is it
   instead an incorrectly reused mutable value or state (not merely order)? →
   `stateful_reuse_or_global_cache`.
5. Does the diff ADD a new guard, branch, or early-return for an input configuration that was
   previously simply unhandled (absent, not wrong)? → `missing_validation_or_contract_check`. This
   includes structural preconditions (index, shape, type, state) even when the symptom was a crash.
6. Does the fault involve a value, index, name, or metadata crossing between two different
   representations, coordinate systems, or index spaces, and is NOT already claimed by steps 1-3
   above? → `cross_representation_conversion`. This still applies even when the surface diff is
   small or the crossing occurs inside control-flow-handling code (see step 8) — but a crossing that
   is fundamentally a commutation, phase, or confirmed-port defect is claimed by steps 1-3 first.
7. Is the fault a genuinely arithmetic edge case (overflow, underflow, division, rounding, sign)? →
   `unchecked_numeric_edge_case`. Reserve this for arithmetic; index/shape/type/structural validation
   that happens to manifest as a panic is step 5, not this step.
8. Is control-flow-construct handling itself the mechanism being fixed (not recursing into or
   routing through a block), as opposed to control flow merely being the location of an unrelated
   bug? → `control_flow_gap`. If the actual defect is a representation/index-space crossing that
   happens to sit inside control-flow code, prefer step 6.
9. Was a value or argument never connected between two points that already both existed, with the
   fix being a wiring/pass-through/initialization change and no new conditional logic? →
   `api_plumbing_or_serialization`. Contrast with step 5 (a new check is added, not a new
   connection) and with step 10 (an existing CONDITION or comparison was wrong, not a wrong VALUE
   passed into an otherwise-correct call).
10. None of the above cleanly fits, because an existing computation, comparison, or condition (not
    a passed-through value, not a missing check) was wrong → `logic_error_pass_specific`. Explicit
    last resort.

## What changed from v2, and why, stated generally

- Steps 1, 2, 4 (commutation, global-phase, ordering/state) moved from the end of the order to the
  front. Justification: these are the categories most narrowly defined by subsystem or property, so
  by the specificity-ordering principle above they must be checked before any broader, shape-based
  category can claim the same fix.
- Step 3 (rust-port) also moved earlier, but its evidentiary bar (historical confirmation) is
  unchanged from v2 — this category cannot be over-claimed merely by being checked earlier, because
  it still requires positive evidence beyond the diff.
- Steps 5-7 (missing-validation, representation-crossing, numeric-edge-case) keep their v2 relative
  order and definitions, since the Round 2 evidence showed this part of the hierarchy working as
  intended (the boundary tests correctly separated structural validation from arithmetic, and from
  wiring gaps).
- Step 9 (api-plumbing) gains an explicit contrast with step 10: a wrong VALUE or argument passed
  into an otherwise-correct call is plumbing; a wrong CONDITION or comparison controlling behavior is
  a logic error. This was applied consistently by the coder in both rounds but was never written
  down as an explicit rule in v2.
- Step 10 (logic-error) remains the last resort, unchanged in substance.

No category's definition changed in what it means; only the order in which categories are tested,
and the api-plumbing/logic-error contrast, changed. This is deliberately a minimal, targeted fix
aimed at the specific structural weakness the Round 2 data revealed, not a general rewrite.

## Final joint-review additions (from resolving the last 3 of 26)

Furqan and Atif independently applied the order above to all 26 disputed fixes without seeing each
other's answer or any proposed resolution: 23 of 26 (88.5%) converged immediately. The remaining 3
were resolved by joint discussion of the diff, which surfaced two further general points, now part
of the frozen codebook:

- **Step 6 (representation-crossing) requires the value's meaning or indexing convention to differ
  across the crossing, not merely that a new object instance is constructed.** A field that is
  copied unchanged into a freshly-built object of the same kind (e.g. a metadata string carried
  into a rebuilt DAG) is step 9 (plumbing), because nothing about the value's shape or meaning
  changes — only its container does. Step 6 is reserved for cases where the value itself means
  something different on each side of the crossing (a local index versus a global one, a positional
  identity versus an actual qubit identity, one iteration-order convention versus another). This
  resolved PR #13910 as `api_plumbing_or_serialization`, not `cross_representation_conversion`.
- **When a single fix combines a new guard and a change to the arithmetic operation itself,
  classify by which change is the primary fault mechanism, not by mechanically stopping at whichever
  step is tested first.** If the underlying arithmetic operation's own unsafety is the root cause,
  and an accompanying guard is part of implementing that correction rather than a separate,
  free-standing check, the fix is step 7 (arithmetic), even though the decision order tests step 5
  (missing-validation) first. This resolved PR #15781 as `unchecked_numeric_edge_case`.
- The step 5 vs. step 10 boundary (a new branch added vs. an existing branch's body corrected) needs
  no rule change; PR #14998 was resolved by reading the actual diff, which confirmed the handling
  path already existed and its logic, not its presence, was the defect.

These two additions are stated generally, apply to any future fix, and were not written to reproduce
either coder's preferred label — in the case of #13910, the added rule overturned the reasoning
Furqan had used to independently pick `cross_representation_conversion` in the first pass, and both
coders agreed the plumbing reading was correct on reflection.

## Status of the broader plan

1. Joint, independent adjudication of the 26 Round 2 disagreements — DONE (23/26 converged
   independently, 3 resolved by discussion, both coders confirmed and asked to freeze).
2. This v3 codebook, with the two additions above — FROZEN.
3. A fresh, genuinely independent reliability assessment with new coders (not Atif or Furqan), blind
   to all prior labels and adjudication decisions, applying the frozen v3 definitions to all 68
   cases from scratch, reported as a separate agreement/kappa figure with confidence intervals — NOT
   done. Disclosed as open future work in the paper (§8) rather than blocking submission on it,
   given RQ1.4 is explicitly exploratory and the reconciliation process already exceeds typical
   practice for an exploratory result.
4. Paper text (Table 6, §5.2, §5.5, §6, §8) updated to the final reconciled labels — DONE.
5. A theoretically motivated coarser grouping of the 11 categories — NOT started; remains contingent
   on a conceptual justification independent of kappa, disclosed in §8 as a possible future direction
   only.
