# Human adjudication sheet — 7 seed disagreements (author R1 + friend R2)

**How to use:** you (author) and your friend (R2) decide each FINAL together, using the PR/issue/diff
as evidence and the frozen codebook v2 rule shown. ChatGPT/Mistral votes are **information only** —
they do NOT decide. Write the agreed answer on the FINAL line and the reason. Record decisions in
`adjudication_decisions.csv`. Do not change the raw per-rater labels.

Legend: channel/observable. (H)=human, [LLM]=info only. ★ = the author's raw label is the minority.

---

### PR 14667 — Restore correct max_trials behaviour for VF2Layout pass
- author(H): circuit_quality / yes   ·   friend(H): compilation_failure / yes
- ChatGPT[LLM]: performance / yes   ·   Mistral[LLM]: circuit_quality / yes
- **Rule 2 (quality vs performance):** worse *output circuit* → circuit_quality; identical circuit,
  only compile time/effort → performance. A crash would override (Rule 1) — check there is none.
- **Proposed:** circuit_quality / yes. *Reason:* "restore correct behaviour" implies the chosen layout
  changed, not just timing. **Check PR:** if the output circuit is identical and only #trials/time
  changed → performance instead. observable = yes either way.
- **FINAL:** __________ / ______   reason: ______________________________

### PR 14998 — Fix VF2PostLayout with uncoupled qubits in strict_direction=True
- author(H): compilation_failure / yes   ·   friend(H)★friend-minority: contract_metadata / no
- ChatGPT[LLM]: compilation_failure / yes   ·   Mistral[LLM]: compilation_failure / yes
- **Rule 1 (crash vs wrong-output):** if transpilation raises/rejects on the trigger → compilation_failure,
  regardless of any metadata issue.
- **Proposed:** compilation_failure / yes. *Reason:* uncoupled qubits in strict_direction is an error
  path. **Check PR:** confirm it actually raised (vs silently emitting wrong metadata → then
  contract_metadata/no).
- **FINAL:** __________ / ______   reason: ______________________________

### PR 14938 — Fix VF2 layout allocation with idle qubits  ★(author minority)
- author(H): circuit_quality / yes   ·   friend(H): contract_metadata / no
- ChatGPT[LLM]: contract_metadata / no   ·   Mistral[LLM]: contract_metadata / no
- **Rule 3 (quality vs metadata):** would an output-equivalence oracle (modulo phase + permutation) see
  a difference? yes → circuit_quality; no (applied output correct, only internal allocation/metadata
  wrong) → contract_metadata/no.
- **Proposed:** contract_metadata / no. *Reason:* friend + both LLMs and the "correct applied behaviour"
  note point to an internal idle-qubit allocation/metadata fault. **This ADDS an output-invisible case.**
- **FINAL:** __________ / ______   reason: ______________________________

### PR 15258 — Fix reuse of ConsolidateBlocks instances
- author(H): output_semantic / yes   ·   friend(H): compilation_failure / yes
- ChatGPT[LLM]: compilation_failure / yes   ·   Mistral[LLM]: output_semantic / yes
- **Rule 1 (crash vs wrong-output):** if instance reuse triggers a panic/exception → compilation_failure.
- **Proposed:** compilation_failure / yes. *Reason:* friend reports a panic ("transpilation fails instead
  of returning a circuit"); a crash is decisive under Rule 1. **Check PR:** if it returns a wrong circuit
  without crashing → output_semantic. observable = yes either way.
- **FINAL:** __________ / ______   reason: ______________________________

### PR 13874 — Use average gate fidelity in the commutation checker
- author(H): circuit_quality / yes   ·   friend(H): output_semantic / yes
- ChatGPT[LLM]: output_semantic / yes   ·   Mistral[LLM]: circuit_quality / yes
- **Rule 3 + correctness:** if a wrong commutation enables an *unsafe* cancellation → wrong unitary =
  output_semantic. If it only changes how *aggressively* it optimizes (output still correct, just
  better/worse) → circuit_quality.
- **Proposed:** output_semantic / yes (lean conservative = correctness). *Reason:* commutation errors can
  reorder/cancel gates unsafely. **Check PR/issue #13547:** confirm whether the output unitary actually
  changed (semantic) or only optimization quality. observable = yes either way. *(low confidence)*
- **FINAL:** __________ / ______   reason: ______________________________

### PR 14041 — Fix deepcopy/pickle of DAGCircuit variable IO nodes  ★(author minority)
- author(H): compilation_failure / yes   ·   friend(H): contract_metadata / no
- ChatGPT[LLM]: contract_metadata / no   ·   Mistral[LLM]: contract_metadata / no
- **Rule 5 (edge plumbing / serialization):** crash → compilation_failure; only property corruption →
  contract_metadata; mark low confidence. **Also decide scope:** is deepcopy/pickle of DAGCircuit even a
  *transpiler* bug, or `exclude_out_of_scope`?
- **Proposed:** contract_metadata / no *(low confidence)* OR exclude_out_of_scope — **author's call.**
  *Reason:* friend + both LLMs see structural/metadata corruption with no crash evidence.
- **FINAL:** __________ / ______   reason: ______________________________

### PR 13820 — Delegate BasePass.__call__ to PassManager.run  ★(author minority)
- author(H): contract_metadata / no   ·   friend(H): compilation_failure / yes
- ChatGPT[LLM]: compilation_failure / yes   ·   Mistral[LLM]: compilation_failure / yes
- **Rule 1 (crash vs wrong-output):** calling a pass directly raised ("ALAPScheduleAnalysis directly on a
  circuit failed") → compilation_failure.
- **Proposed:** compilation_failure / yes. *Reason:* a direct-call exception is a functional failure; this
  is well-supported. **This REMOVES one case from the output-invisible set** (author had it as 'no').
- **FINAL:** __________ / ______   reason: ______________________________

---

## Net effect on the headline (recompute after you finalize)
Proposed changes to the output-invisible ('observable = no') set vs the author's raw labels:
**+14938, +14041 (newly invisible), −13820 (now visible).** Re-run the agreement script on the
finalized human labels to get the updated κ and output-invisible fraction with CI.

## Note on the pattern
On 14938, 14041, 13820 the author's raw label is the minority vs {friend, ChatGPT, Mistral}. That's not
proof you're wrong — you're the domain expert — but those three deserve the hardest look together.
