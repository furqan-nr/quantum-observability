# P4 — upstream issue draft (Qiskit; tket variant below)

> **FILED 2026-07-21 → CLOSED (declined) 2026-07-22** — https://github.com/Qiskit/qiskit/issues/16631
> Maintainer response: confirmed metadata-channel testing gaps are real and are handled reactively
> (a targeted metadata test is added per fix), but declined a standing suite-wide assertion. Reasons:
> equivalence-based checks (assertions 3-4) are impractical at the 100s-of-qubit widths transpile tests
> use; the layout-composition invariant (assertion 2) is enforced by construction in TranspileLayout;
> assertions 1 and 5 are already covered at unit-test level; and they want evidence of widespread latent
> violations before large-scale CI changes. Terminology nit: assertion 5 is "reproducibility", not "idempotence".
>
> STATUS (supervisor greenlit 2026-07-22, "still Q1, keep working"): manuscript edits APPLIED — §6.8 now
> reports the maintainer response honestly (problem confirmed, standing assertion declined), oracle family
> repositioned as targeted per-fix / cross-version checks, "first-class CI checks" removed,
> idempotence->reproducibility fixed. A positive reply to the maintainer is drafted in
> `P4_maintainer_reply_READY.md` (to be posted by the author). The BASR proposal (already submitted to
> committee) is UNCHANGED; all four objectives O1-O4 remain achieved/on-track. tket variant not posted.


Post as a GitHub issue on Qiskit/qiskit (label: `type: feature request`, `mod: transpiler`). Keep the
tone collaborative — we are proposing a CI-level invariant and offering to contribute it, not reporting
a live bug. Trim to taste before posting.

---

## Title
Add transpiler layout/permutation **contract assertions** to CI (catch metadata regressions that output-equivalence checks miss)

## Body

### Summary
Several past transpiler regressions corrupted the recorded layout/permutation metadata
(`TranspileLayout`, `final_index_layout`, `routing_permutation`, per-pass `virtual_permutation_layout`)
or the tracked `global_phase`, while leaving the **layout-applied output unitary correct**. Because the
usual correctness check is output-equivalence *modulo global phase and qubit permutation*, this class of
fault is invisible to it — the compiled program is "right", but a downstream consumer that trusts the
recorded metadata is misled. We'd like to propose (and are happy to contribute) a lightweight set of
**contract assertions** that run in CI and catch this class directly.

### Motivating examples (already fixed here)
- **#14603** — `ElidePermutations` in the presence of `PermutationGate`s: corrupted the recorded
  permutation while the applied output stayed correct.
- **#14919** — composition of `final_layout` across multiple routing passes was applied backwards;
  appending the recorded `routing_permutation` to the routed output no longer recovered the input.

Both merged with a fix + a regression test, but neither would have been caught by an output-equivalence
oracle alone — only by an assertion on the *metadata contract*.

### Proposed contract assertions (metadata-internal, cheap, no full unitary needed)
For a transpiled circuit, assert:
1. **Permutation validity** — `initial_index_layout` and `final_index_layout` are valid permutations of
   `range(num_qubits)` (ancilla-free case); `routing_permutation` is a valid permutation.
2. **Composition consistency** — `final_index_layout` equals `initial_index_layout` composed with
   `routing_permutation` (the invariant #14919 restored).
3. **Permutation consistency (metamorphic)** — appending `PermutationGate(routing_permutation)` to the
   routed output recovers the input unitary (checkable at small width, or via sampled statevectors at
   larger width — no `2^n × 2^n` operator required).
4. **Global-phase tracking** — for a phase-relevant pass, the tracked `global_phase` is preserved
   end-to-end (complement of the modulo-global-phase output check).
5. **Fixed-seed metadata idempotence** — with a fixed `seed_transpiler`, repeated transpilation yields
   identical recorded layout metadata.

Checks 1–3 are pure metadata invariants and add negligible cost; 3–4 can be gated by width and circuit
purity. We have a reference implementation of all five (layout-aware, width-tiered