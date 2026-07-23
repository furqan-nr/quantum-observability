# Agreement matrix — humans vs LLMs (seed corpus, 2026-06-29)

Four label sets: **author (human R1)**, **friend (human R2)**, **ChatGPT (LLM)**, **Mistral (LLM)**.
Reproduce with the pairwise script; raw labels preserved in `dual_rater_labels.csv` (author + ChatGPT),
`three_rater_audit.csv` (Mistral), `human_r2_friend_raw.csv` (friend).

## Cohen's kappa — pairwise
| Pair | n | Binary κ | Channel κ | Type |
|---|---|---|---|---|
| author vs friend | 24 | **0.667** | **0.619** | HUMAN-HUMAN (headline reliability) |
| author vs ChatGPT | 26 | 0.675 | 0.665 | human-LLM (auxiliary) |
| author vs Mistral | 26 | 0.586 | 0.664 | human-LLM (auxiliary) |
| friend vs ChatGPT | 24 | 0.833 | 0.832 | human-LLM (auxiliary) |
| friend vs Mistral | 24 | 0.750 | 0.618 | human-LLM (auxiliary) |
| ChatGPT vs Mistral | 26 | **0.917** | 0.712 | LLM-LLM (interest only) |

## How to report each (binding rules)
1. **Headline reliability = author vs friend (human-human) only.** Everything else is auxiliary.
2. **LLM labels are reported as an LLM-as-annotator cross-check**, in a clearly separate table.
   Never pooled into the human κ; never used as a deciding vote for the human reliability.
3. **Full reproducibility for the LLM passes:** model name + version, date, exact prompt, temperature
   (or "default"), and that each pass was blinded to prior labels.

## The cautionary finding (report it — it strengthens rigor)
The two LLMs agree with each other (binary κ=0.92) more than the two humans agree with each other
(κ=0.67), and more than humans agree with LLMs. High LLM-LLM agreement reflects shared model priors,
not codebook reproducibility, so LLM agreement must not be presented as inter-rater reliability. This
is exactly why the human double-coding is the reliability evidence.

## Adjudication note
On the binary disagreements the author (R1) is often the minority vs {friend, ChatGPT, Mistral}
(e.g. 14998, 14938, 13820). Use this only to inform discussion during adjudication — not to auto-flip
labels. The human author + human friend resolve disagreements together against PR evidence.
