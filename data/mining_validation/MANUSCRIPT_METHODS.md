# Manuscript wording — classification & inter-rater reliability (HUMAN raters)

## Methods paragraph (use this as the headline)
Each pull request was independently classified by two human annotators with quantum-software
experience, using a frozen seven-channel codebook. The second annotator was blinded to the first
annotator's labels, the adjudication history, and all prior agreement statistics, and classified
each fix using only the pull-request description, linked issues, diffs, release notes, and regression
tests. Each annotator assigned one manifestation channel and a binary output-oracle observability
judgment. We report raw agreement and Cohen's kappa with bootstrap 95% confidence intervals on the
unadjudicated labels. Disagreements were resolved afterward by discussion against the same evidence;
adjudication did not overwrite the raw per-annotator records.

## Reported reliability (seed, n=24 double-coded)
Binary output-oracle observability: 83.3% raw agreement, kappa = 0.667 (95% CI [0.338, 0.917]).
Seven-class manifestation channel: 70.8% raw agreement, kappa = 0.619 (95% CI [0.360, 0.835]).
Both "substantial." Confidence intervals will tighten on the full n>=100 corpus.

## Optional auxiliary disclosure (only if you choose to report the LLM passes)
As an exploratory cross-check, an LLM-assisted pass was run against the same codebook; it is reported
separately and is NOT used as the human inter-rater reliability. If you do not need it, omit it
entirely — the human double-coding above is the reliability evidence.

## Honesty rule (binding)
Report the two human annotators as the inter-rater reliability. Do NOT present any LLM pass as a human
annotator. Do NOT pool LLM labels into the human kappa.

## Auxiliary LLM cross-check paragraph (concrete wording, optional)
As a transparency cross-check we additionally classified the seed corpus with two LLM-assisted passes
(ChatGPT and Mistral) using the same frozen codebook, each blinded to prior labels (model versions,
dates, and prompts in the replication package). We report these only as an auxiliary comparison, not
as human inter-rater reliability. Notably, the two LLMs agreed with each other (binary κ=0.92) more
than the two human annotators agreed with each other (κ=0.67), indicating shared model priors rather
than codebook reproducibility; we therefore base reliability solely on the human double-coding.
