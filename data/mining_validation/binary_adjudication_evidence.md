# Binary adjudication evidence — seed corpus

**Reviewed:** 2026-06-29  
**Scope:** five binary `observable_by_output_oracle` cases reviewed against PR description, release notes, diffs, and regression tests.  
**Rule:** decisions use Codebook v2: compilation crash/rejection -> `compilation_failure/yes`; internal contract or metadata corruption with layout-applied output intact -> `contract_metadata/no`; serialization/deepcopy edge cases remain low confidence unless a functional crash is evidenced.

| PR | Final channel | Observable | Status | Evidence-based reason |
|---|---|---:|---|---|
| [14603](https://github.com/Qiskit/qiskit/pull/14603) | `contract_metadata` | `no` | `ADJUDICATED` | Retained the existing H1/build-from-source adjudication. Although the PR describes incorrect raw output circuits, the study's oracle is layout-applied output equivalence; the recorded H1 result says that oracle passes on the buggy build while virtual_permutation_layout is corrupted. |
| [13833](https://github.com/Qiskit/qiskit/pull/13833/files) | `contract_metadata` | `no` | `ADJUDICATED` | The trigger is a missing entry in the final routing permutation for unused components of a disjoint coupling map. The release note states compilation can appear to succeed, but later final_index_layout can raise KeyError. The added regression test runs the pass successfully and asserts complete layout metadata. This is metadata/contract corruption, not a transpilation failure. |
| [14041](https://github.com/Qiskit/qiskit/pull/14041/files) | `contract_metadata` | `no` | `ADJUDICATED_LOW_CONFIDENCE` | The defect occurs only during deepcopy or unpickling of a DAG with variables: Var output nodes are reconstructed as input nodes. The PR evidence shows representation corruption and equality-preservation tests, not a transpilation crash or a wrong compiled-circuit output. Under Codebook v2's edge-of-scope serialization rule, classify as contract_metadata/no and retain low confidence. |
| [13820](https://github.com/Qiskit/qiskit/pull/13820/files) | `compilation_failure` | `yes` | `ADJUDICATED` | Before the change, direct BasePass.__call__ invoked run directly and skipped required passes. The regression test creates a required analysis pass and a transformation pass that asserts the required property; calling the transformation directly must now run the requirement. Thus the broken path fails functionally, so it is compilation_failure/yes. |
| [14938](https://github.com/Qiskit/qiskit/pull/14938/files) | `contract_metadata` | `no` | `ADJUDICATED` | VF2 omitted completely idle qubits from returned Layout objects. The PR says the mapping does not materially affect the compiled output, while consumers of TranspileLayout can fail after compilation. The fix fills arbitrary layout assignments for idle qubits. Therefore this is contract_metadata/no. |

## Notes

- **14603:** preserved rather than re-labeled. Its current decision relies on the project’s previously recorded built-from-source H1 oracle result, not rater majority.
- **14041:** is settled as `contract_metadata/no` under the frozen edge-of-scope rule, but stays explicitly low confidence. The source evidence establishes representation corruption, not a compilation failure.
- The raw R1, ChatGPT R2, and Mistral R3 columns are preserved verbatim in the updated audit CSV.
