# Channel adjudication evidence — seed corpus

**Scope:** five channel decisions reviewed after the binary adjudication.

**Protocol:** Codebook v2 is applied top-to-bottom. A documented crash, exception, panic, or rejected input takes precedence over a potential output-quality interpretation. Raw R1, ChatGPT R2, and Mistral R3 labels are unchanged.

| PR | Final channel | Observable | Corpus disposition | Status | Evidence-based decision |
|---|---|---:|---|---|---|
| [15875](https://github.com/Qiskit/qiskit/issues/13162) | `compilation_failure` | `yes` | `include` | `ADJUDICATED` | Nested ControlFlowOp blocks could skip required basis transformations, leaving an unsupported instruction (for example rccx) in the emitted circuit. The linked reproducer then fails at execution with AerError: unknown instruction. Under the codebook's functional-failure rule, this is compilation_failure/yes, not output_semantic. |
| [14667](https://github.com/Qiskit/qiskit/pull/14667/files) | `compilation_failure` | `yes` | `include` | `ADJUDICATED_MULTI_TRIGGER` | This PR has two trigger paths: max_trials=None incorrectly causes an unbounded search (performance), while max_trials<0 incorrectly raises an error despite being documented as the unbounded-search setting. Codebook v2 applies the crash/rejection rule first, so the single required label is compilation_failure/yes. This avoids calling it circuit_quality without evidence that the emitted circuit is worse. |
| [13874](https://github.com/Qiskit/qiskit/issues/13547) | `output_semantic` | `yes` | `include` | `ADJUDICATED` | The linked bug reports a concrete non-equivalence: with a small RY angle, optimization levels 2/3 produce a circuit for which Operator(qc).equiv(tqc) is False. The commutation-checker tolerance therefore causes a changed unitary, not merely a different gate count or depth. Classify output_semantic/yes. |
| [15258](https://github.com/Qiskit/qiskit/issues/15255) | `compilation_failure` | `yes` | `include` | `ADJUDICATED` | Reusing the PassManager across circuits of different sizes raises a Rust PanicException (index out of bounds). Although the release note also allows for invalid output in another path, Codebook v2 gives priority to an evidenced panic: compilation_failure/yes. |
| [14120](https://github.com/Qiskit/qiskit/issues/14100) | `performance` | `yes` | `exclude_not_bugfix` | `EXCLUDED_NOT_BUGFIX` | Diagnostic classification only. PR 14120 implemented a feature request rather than fixing a bug, so it is excluded from the analytic corpus. The feature description says the extra VF2PostLayout pass is not guaranteed to improve output quality, and the later reported regression was substantial runtime overhead (with explicit initial_layout the computed alternative layout was discarded). There is no evidence in this PR of an emitted circuit becoming worse; if retained solely for an engineering audit, classify performance/yes. |

## Important scope correction: PR 14120

PR 14120 is linked to an issue marked as a feature request, and the pull request itself was marked as a changelog addition. It is not a qualifying bug-fix observation for a corpus defined as merged transpiler bug fixes. The audit retains it for traceability and gives its diagnostic category, but analytic results must exclude it.

## Analytic impact

- Source audit rows: 26
- Excluded as not a bug-fix: PR 14120
- Analytic seed corpus after this scope correction: 25 rows
- All 25 included rows now have a current final channel and observable label.
