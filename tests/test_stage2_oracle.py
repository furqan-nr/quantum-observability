"""Pure unit tests for the Stage-2 performance oracle and the property/layout comparison.

Dependency-free (no Qiskit). Run on the anchor venv:
    python -m pytest -q tests/test_stage2_oracle.py
"""
from cart.oracles.performance_stage2 import confirm_performance
from cart.oracles.property_layout import compare_layout_props


# ---- Stage-2 performance oracle -------------------------------------------------------------

def test_perf_confirms_clear_slowdown():
    base = [1.00, 1.02, 0.98, 1.01, 0.99, 1.00, 1.03]
    cand = [1.40, 1.42, 1.38, 1.41, 1.39, 1.40, 1.43]   # ~40% slower, cleanly separable
    r = confirm_performance(base, cand, slowdown_threshold=0.20, min_magnitude="small")
    assert r.suspected_regression is True
    assert r.slowdown_ratio > 0.20
    assert r.ratio_ci_lo > 0
    assert r.cliffs_delta > 0.9
    assert r.a12_candidate_slower > 0.9


def test_perf_rejects_overlapping_noise():
    base = [1.00, 1.05, 0.95, 1.02, 0.98, 1.01, 0.99]
    cand = [1.01, 0.96, 1.04, 0.99, 1.03, 0.97, 1.00]   # overlapping; no real slowdown
    r = confirm_performance(base, cand, slowdown_threshold=0.20, min_magnitude="small")
    assert r.suspected_regression is False


def test_perf_rejects_consistent_overhead_below_threshold():
    # A real but small (5%) overhead below the pre-declared 20% screen must NOT be confirmed —
    # this is the honest "genuinely below detection at commodity scale" outcome.
    r = confirm_performance([1.00] * 7, [1.05] * 7, slowdown_threshold=0.20, min_magnitude="small")
    assert r.suspected_regression is False
    assert "threshold" in r.decision_reason


def test_perf_insufficient_samples():
    r = confirm_performance([1.0], [1.5], slowdown_threshold=0.20)
    assert r.suspected_regression is False
    assert "insufficient" in r.decision_reason


# ---- property/layout oracle (pure comparison) -----------------------------------------------

def test_property_divergent_detects_fault():
    base = {"virtual_permutation_layout": [(0, 1), (1, 0)], "final_index_layout": [0, 1, 2]}
    cand = {"virtual_permutation_layout": [(0, 0), (1, 1)], "final_index_layout": [0, 1, 2]}
    res = compare_layout_props(base, cand)
    assert res.equivalent is False
    assert "virtual_permutation_layout" in res.divergent_fields
    assert "final_index_layout" not in res.divergent_fields


def test_property_identical_is_equivalent():
    props = {"final_index_layout": [0, 1, 2], "routing_permutation": [0, 1, 2]}
    res = compare_layout_props(dict(props), dict(props))
    assert res.equivalent is True
    assert res.divergent_fields == []


def test_property_no_contract_returns_none():
    res = compare_layout_props({}, {})
    assert res.equivalent is None
