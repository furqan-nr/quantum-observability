# Coding the 44 — turning the study into a full three-rater 68-fix seed

Goal: get the remaining **44** transpiler bug-fixes independently human-coded by two raters,
adjudicate, and merge with the existing **24-seed** → a genuine **68-fix, three-rater** study.
After that the abstract can say "three-rater study of 68" with no "preliminary" hedge.

Two raters code **independently and blind** (neither sees the other's labels, nor the LLM
provisional labels, nor the 24-seed labels). You are **R1**; your friend is **R2**.

---

## Files

| File | Who | What |
|---|---|---|
| `human_worksheet_44_R1.csv` | **You (R1)** | fill the 4 label columns for all 44 rows |
| `human_worksheet_44_R2.csv` | **Friend (R2)** | same 44 rows, coded independently |
| `CODEBOOK_v2_FROZEN.md` | both | the rules — do not deviate |

Each row already has `pr, title, pr_url, linked_issue, linked_issue_url`. You fill the last four:
`manifestation_channel, observable_by_output_oracle, confidence, notes`.

---

## Step by step (each rater, ~2–4 hours for 44 rows)

1. Open your worksheet (`human_worksheet_44_R1.csv` for you) in Excel or any editor.
2. For each row, open `pr_url` (and `linked_issue_url` if present). Read the **title, description,
   and linked issue only** — do not read the code diff unless the text is ambiguous.
3. **Scope gate first.** Include only a real *transpiler bug-fix*. If the PR is a feature,
   enhancement, docs-only, refactor, or pure test/maintenance change, put `exclude` in
   `manifestation_channel`, leave `observable` blank, and note why. (These drop out of the count.)
4. If it is a bug-fix, assign exactly one **`manifestation_channel`** from the cheat-sheet below.
5. Fill **`observable_by_output_oracle`** = `yes` or `no` (the channel decides it — see cheat-sheet;
   filling it yourself is a consistency check).
6. Fill **`confidence`** = `high` / `medium` / `low`.
7. Fill **`notes`** with one line of reasoning — required whenever confidence is `low` or you excluded.
8. Save. Do not compare with R2 until both are finished.

---

## Channel cheat-sheet (assign exactly one)

Observable by a black-box output oracle → **yes**:
- **output_semantic** — compiled circuit computes a *different* unitary / measured output.
- **compilation_failure** — crash / exception / panic / rejected input during transpile.
- **circuit_quality** — output correct but *worse* (more 2q gates, more depth, worse layout).
- **performance** — only *compile-time* cost changes (slower / more memory); circuit identical.

Invisible to a black-box output oracle → **no** (the study's key set):
- **contract_metadata** — corrupts an internal contract/metadata property (`TranspileLayout`,
  `final_layout`, `virtual_permutation_layout`, `routing_permutation`, circuit `name`) while the
  layout-applied output unitary stays correct.
- **determinism** — output non-deterministic across fixed-seed runs (no single run is "wrong").
- **global_phase** — drops/alters the global phase (invisible to equivalence modulo global phase).

Ordered tie-breakers (first match wins):
1. Crash/panic/rejection on the trigger → `compilation_failure` (even if it *would* be wrong output).
2. Output circuit worse → `circuit_quality`; identical circuit, only time/memory → `performance`.
3. Would an output-equivalence oracle (mod global phase + qubit permutation) see any difference?
   Yes → `circuit_quality`/`output_semantic`; No (only an internal property wrong) → `contract_metadata`.
4. Output correct but a layout/permutation property corrupted → `contract_metadata` / no.
5. Edge-of-scope plumbing (serialization, pickle, dunder): crash → `compilation_failure`;
   property-only → `contract_metadata`; mark `low` confidence.

---

## After both raters finish — send me both files, or run these yourself

Reliability (κ) and disagreement list over the 44:
```
python scripts\score_worksheet.py data\mining_validation\human_worksheet_44_R1.csv ^
    --rater2 data\mining_validation\human_worksheet_44_R2.csv
```
This prints the invisible rate on each rater's coding, raw agreement, and **Cohen's κ** (binary
observability). Note any rows where R1 and R2 differ.

## Adjudicate
For each disagreement, you and R2 discuss against `CODEBOOK_v2_FROZEN.md` and agree one label.
Record the agreed label + a one-line reason (append to `adjudication_log.md`).

## Then hand back to me
Send the two coded sheets (and the adjudicated calls). I will:
- merge the 44 adjudicated labels with the 24-seed → a 68-row final labels file,
- recompute the output-invisible rate + Wilson CI + κ over the full 68,
- and update the abstract/contribution to a final "three-rater study of 68" (dropping "preliminary").

---

**Do not** paste the LLM provisional labels (`provisional_llm_labels_44.csv`) into these sheets —
that would break the independent-human-coding claim (the exact point your supervisor raised).
