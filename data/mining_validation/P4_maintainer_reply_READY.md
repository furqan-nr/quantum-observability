========================================================================
POST THIS AS A COMMENT ON https://github.com/Qiskit/qiskit/issues/16631
(gracious, specific, accepts the critique — no re-arguing)
========================================================================

Thank you, this is genuinely helpful and I take all of it.

A few things I am taking away. You are right that the equivalence-based checks (3 and 4) do not scale. I was thinking of the small-to-medium circuits typical of metadata-focused tests, but transpile tests routinely run well past the point where building an operator or a statevector is feasible, so those two only really apply at small width. That is a real limitation. Point 2 is also fair: composition consistency is enforced by construction in `TranspileLayout`, so a pass cannot violate it on its own. And 1 and 5 are already covered at the unit-test level where they matter. Noted as well that 5 is reproducibility rather than idempotence.

The most useful part for me is the framing. These belong as targeted, per-fix metadata tests, which is what you already do, rather than as a standing suite-wide assertion, and any broader change would need evidence of widespread latent violations rather than a handful of already-fixed cases. That is a fair bar. If I run into specific unfixed instances, I will file them as bug reports as you suggest.

Thanks again for taking the time to write such a detailed response. It has sharpened how I am thinking about this.
