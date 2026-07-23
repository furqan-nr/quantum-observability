========================================================================
PASTE THIS INTO THE **TITLE** FIELD:
========================================================================

Add transpiler layout/permutation contract assertions to CI (catch metadata regressions that output-equivalence checks miss)


========================================================================
PASTE EVERYTHING BELOW THIS LINE INTO THE **DESCRIPTION** BOX:
========================================================================

### Summary

A number of past transpiler regressions corrupted the recorded layout and permutation metadata (`TranspileLayout`, `final_index_layout`, `routing_permutation`, and the per-pass `virtual_permutation_layout`), or the tracked `global_phase`, while the layout-applied output unitary stayed correct. The usual correctness check is output-equivalence modulo global phase and qubit permutation, so it cannot see this kind of fault. The compiled program is right, but any downstream consumer that trusts the recorded metadata is misled. We would like to propose a small set of contract assertions that run in CI and catch this class directly, and we are happy to contribute them.

### Motivating examples (already fixed)

- **#14603**: `ElidePermutations`, in the presence of `PermutationGate`s, corrupted the recorded permutation while the applied output stayed correct.
- **#14919**: the composition of `final_layout` across multiple routing passes was applied backwards. Appending the recorded `routing_permutation` to the routed output no longer recovered the input.

Both were merged with a fix and a regression test. Neither would have been caught by an output-equivalence oracle on its own. Only an assertion on the metadata contract catches them.

### Proposed contract assertions (metadata-internal, cheap, no full unitary needed)

For a transpiled circuit, assert:

1. **Permutation validity.** `initial_index_layout` and `final_index_layout` are valid permutations of `range(num_qubits)` in the ancilla-free case, and `routing_permutation` is a valid permutation.
2. **Composition consistency.** `final_index_layout` equals `initial_index_layout` composed with `routing_permutation`. This is the invariant that #14919 restored.
3. **Permutation consistency (metamorphic).** Appending `PermutationGate(routing_permutation)` to the routed output recovers the input unitary. This is checkable directly at small width, or through sampled statevectors at larger width, with no `2^n × 2^n` operator required.
4. **Global-phase tracking.** For a phase-relevant pass, the tracked `global_phase` is preserved end to end. This is the complement of the modulo-global-phase output check.
5. **Fixed-seed metadata idempotence.** With a fixed `seed_transpiler`, repeated transpilation yields identical recorded layout metadata.

Checks 1 to 3 are pure metadata invariants and add negligible cost. Checks 3 and 4 can be gated by width and circuit purity. We already have a reference implementation of all five, layout-aware and width-tiered so that it avoids forming full unitaries at scale. If there is interest, we can open a draft PR that wires them into the transpiler test suite, or into an `assert_transpile_contract(...)` helper.

### Why it is worth having in CI

Because this fault class is output-invisible by construction, catching it today depends on someone remembering to write a targeted metadata test for each fix. A standing contract assertion over the existing test corpus would catch regressions across the whole channel automatically. In a repository-mining study of merged `mod: transpiler` bug-fixes, we found that a substantial minority, somewhere between one in four and one in three, fall in exactly these output-invisible channels. The same pattern shows up in other quantum compilers, for instance tket #2072 (an implicit qubit permutation dropped) and #146 (missing wire-swap handling in phase-polynomial synthesis), so the check is broadly applicable.

We are happy to contribute the implementation and to discuss scope and placement.
