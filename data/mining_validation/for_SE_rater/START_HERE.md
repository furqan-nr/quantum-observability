# Start here — what I need you to do (about 2–4 hours)

Thank you for helping! You do **not** need to know anything about quantum computing. This is a
software-engineering judgement task: read a GitHub bug-fix and put it in a category.

## The 30-second picture
We are studying Qiskit's "transpiler" (think of it as a **compiler** for quantum circuits). Some of
its bugs produce a clearly wrong/erroring output; others quietly corrupt *metadata* while the output
still looks correct. We are measuring how often each kind happens. To make our labels trustworthy, we
need a **second independent person** (you) to categorise the same bug-fixes on your own. Your labels
will be compared to ours to compute an agreement score (Cohen's kappa).

## The one rule that makes this valuable: do it INDEPENDENTLY
- Do **not** ask anyone (or ChatGPT/any AI) to label these for you. We specifically need *your own
  human judgement* — that is the entire point.
- Do **not** look for our labels or anyone else's. You are seeing a blank sheet on purpose.

## What you'll open
1. `codebook.md` — the rulebook. It lists the 7 categories and how to choose. Read the top section
   and the "Version 2 — tightened borderline rules" section once before you start.
2. `to_label.csv` — 25 rows, one per bug-fix. Open it in Excel/Google Sheets. The label columns are
   empty; you fill them.
3. `cheatsheet.md` — a 1-page decision flow if you get stuck.

## For EACH of the 25 rows, do this
1. Click the link in the `pr_url` column. Read the PR title, the description, any linked issue, and
   skim the code diff and the test they added. That tells you what the bug was.
2. Fill these four columns:
   - **manifestation_channel** — pick exactly ONE of the 7 words from the codebook
     (`output_semantic`, `compilation_failure`, `circuit_quality`, `performance`,
     `contract_metadata`, `determinism`, `global_phase`).
   - **observable_by_output_oracle** — type `yes` or `no`. This is the key question: *if you only
     compared the program's output (ignoring re-orderings and a harmless global phase), could you
     catch this bug?* The codebook tells you which categories are `yes` vs `no`.
   - **confidence** — `high`, `medium`, or `low`.
   - **notes** — one short line on why (especially if you marked `low`).
3. Save and move to the next row.

## If you're unsure
Use the `cheatsheet.md` flow. If it's still genuinely borderline, pick your best guess, mark
`confidence = low`, and write what made it hard in `notes`. That's a valid, useful answer — don't
agonise.

## When you're done
Send back the filled `to_label.csv` (just that one file). That's everything.

## What happens next (so you know it matters)
Your labels are compared with ours to report an honest human agreement score in a research paper. You
are credited as a second coder. You are not expected to be right about quantum physics — you are
giving an independent software-engineering reading of each fix.
