# 1-page decision cheat-sheet

Read the PR, then go top to bottom. **The first rule that matches wins.**

1. Does the bug make transpilation **crash / throw / panic / reject valid input**?
   -> `compilation_failure`  (observable = **yes**)

2. Does the fix change the **actual computed result** of the circuit (different output / different
   math), not just a re-ordering?  (PRs often say "wrong result", "incorrect unitary", "not
   equivalent", a test using `Operator(...).equiv(...)` that was failing)
   -> `output_semantic`  (observable = **yes**)

3. Is the output correct but the circuit is **worse** — more 2-qubit gates, more depth, worse layout?
   -> `circuit_quality`  (observable = **yes**)

4. Is the output **identical** and only **compile time / memory** changed (slower, redundant work)?
   -> `performance`  (observable = **yes**)

5. Is the output correct, but some **metadata / bookkeeping** is wrong — layout, qubit mapping,
   `final_layout`, `final_index_layout`, `routing_permutation`, circuit `name`, `TranspileLayout`?
   -> `contract_metadata`  (observable = **no**)

6. Does the same input give **different results on different runs** with the same settings (random,
   not reproducible)?
   -> `determinism`  (observable = **no**)

7. Is only the **global phase** dropped/changed (a harmless-looking overall factor)?
   -> `global_phase`  (observable = **no**)

## The `yes` / `no` rule in one line
- **yes** (output oracle could catch it): output_semantic, compilation_failure, circuit_quality, performance
- **no**  (invisible to an output-only check): contract_metadata, determinism, global_phase

## Tip for the tricky "quality vs metadata" case (rule 3 vs 5)
Ask: *would comparing the actual output (ignoring qubit re-ordering + global phase) show any
difference?*
- Yes, the applied circuit is measurably worse -> `circuit_quality` / yes
- No, the output is fine and only an internal field is wrong -> `contract_metadata` / no
