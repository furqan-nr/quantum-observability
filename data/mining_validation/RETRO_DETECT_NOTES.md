# Retro-detection feasibility — build-free vs from-source

Checked (2026-07-04) whether the mined output-invisible fixes can be retro-detected from pip WHEELS
(build-free) by diffing the release that shipped the bug against the release that shipped the fix.

**Result: none of the 6 sampled invisible-channel fixes are wheel-retro-detectable.** For each, the
fix commit AND its parent first appear in the SAME release (Qiskit fixes these fast, within one release
cycle), so the buggy state was never released:

| PR | channel | fix_release | parent_release | wheel-retro-detectable? |
|----|---------|-------------|----------------|--------------------------|
| 14956 | global_phase | 2.2.0 | 2.2.0 | no |
| 15040 | determinism | 2.3.0 | 2.3.0 | no |
| 15024 | contract_metadata | 2.3.0 | 2.3.0 | no |
| 16215 | global_phase | 2.5.0 | 2.5.0 | no |
| 16237 | determinism | 2.5.0 | 2.5.0 | no |
| 16201 | global_phase | 2.5.0 | 2.5.0 | no |

**Implication:** retro-detection of these fixes REQUIRES from-source builds of the parent (buggy) and
fix commits — i.e., it goes through `scripts/source_validate_mining.py` (P3), which needs the Rust
build. There is no build-free shortcut for within-release fixes. `scripts/retro_detect_release.py`
remains useful only for the subset of mined fixes (if any) where the bug PERSISTED across a release
boundary (parent_release < fix_release); none of the current invisible sample qualifies.

**Canonical trigger source:** each fix PR adds its own regression test (e.g. #16201 ->
test/python/transpiler/test_unroll_forloops.py, +37 lines). Extract the circuit from that added test
to author the exact bug-exercising trigger, rather than guessing.
