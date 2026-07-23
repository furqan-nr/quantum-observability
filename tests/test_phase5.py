"""Phase 5 tests: metric correctness (hand-computed) + gate helpers."""
from cart.metrics.curves import (event_metrics, recall_at_budget, win_tie_loss,
                                 detection_curve, aggregate_seeds, CURVE_GRID)
from cart.metrics.evaluate import oracle_false_positive_rate
from cart.gates.validity import gate_metric_correctness


def test_event_metrics_handcomputed_detect_second():
    rank = [f"t{i}" for i in range(10)]
    cost = {t: 1.0 for t in rank}
    em = event_metrics(rank, cost, {"t1": True})        # 2nd test detects; full cost = 10
    assert em.detected
    assert abs(em.normalized_ttfr - 0.2) < 1e-9          # ttfr = 2 / 10
    assert abs(em.auc_detection_vs_budget - 0.8) < 1e-9  # 1 - 0.2
    assert em.detection_at_fraction[0.05] == 0
    assert em.detection_at_fraction[0.10] == 0
    assert em.detection_at_fraction[0.20] == 1
    assert em.detection_at_fraction[0.40] == 1


def test_event_metrics_never_detected():
    rank = [f"t{i}" for i in range(10)]
    cost = {t: 1.0 for t in rank}
    em = event_metrics(rank, cost, {})
    assert not em.detected
    assert abs(em.normalized_ttfr - 1.0) < 1e-9
    assert em.auc_detection_vs_budget == 0.0
    assert all(v == 0 for v in em.detection_at_fraction.values())


def test_recall_at_budget():
    rank = ["a", "b", "c"]
    cost = {"a": 1.0, "b": 1.0, "c": 1.0}
    assert recall_at_budget(rank, cost, {"c": True}, budget_s=3.0) == 1
    assert recall_at_budget(rank, cost, {"c": True}, budget_s=2.0) == 0   # c not reached within 2.0
    assert recall_at_budget(rank, cost, {"a": True}, budget_s=1.0) == 1


def test_oracle_fp_rate():
    labels = [
        {"label": "pass", "confirmed": True},
        {"label": "quality_regression", "confirmed": True},
        {"label": "performance_regression", "confirmed": False},
    ]
    assert oracle_false_positive_rate(labels) == 0.5   # 1 unconfirmed of 2 warnings


def test_gate_metric_correctness_passes():
    g = gate_metric_correctness()
    assert g.passed, g.detail


def test_win_tie_loss_counts():
    # lower normalized_TTFR is better for `proposed`
    proposed = {"e1": 0.1, "e2": 0.5, "e3": 0.3}
    baseline = {"e1": 0.2, "e2": 0.5, "e3": 0.1}   # win, tie, loss
    wtl = win_tie_loss(proposed, baseline)
    assert wtl == {"win": 1, "tie": 1, "loss": 1}
    assert wtl["win"] + wtl["tie"] + wtl["loss"] == len(proposed)


def test_detection_curve_monotonic_and_bounded():
    # two events: one detected at 0.2, one never detected
    per_event = [(True, 0.2), (False, 1.0)]
    curve = detection_curve(per_event)
    assert len(curve) == len(CURVE_GRID)
    assert all(0.0 <= v <= 1.0 for v in curve)
    assert all(b >= a - 1e-12 for a, b in zip(curve, curve[1:]))   # non-decreasing
    assert curve[0] == 0.0
    assert abs(curve[-1] - 0.5) < 1e-9                              # only 1 of 2 ever detected


def test_aggregate_seeds():
    agg = aggregate_seeds([0.2, 0.4, 0.6])
    assert agg == {"median": 0.4, "min": 0.2, "max": 0.6}
    assert aggregate_seeds([]) == {"median": None, "min": None, "max": None}
