"""Phase 3 tests: baseline selectors — budget compliance, leakage, determinism."""
from cart.events.schema import Event, FaultSource, FaultType, TrainOrTest
from cart.manifest.static_manifest import TestUnit
from cart.selectors.context import SelectionContext
from cart.selectors.cost_model import expected_cost
from cart.selectors.baselines import BASELINES, run_baseline, _change_stage_match


def _unit(tid, fam, backend, stages, oracle="unitary", n=5):
    return TestUnit(test_id=tid, circuit_family=fam, n_qubits=n, backend_id=backend,
                    transpiler_config_id="opt1+basis", declared_pass_stages=tuple(stages),
                    oracle_type=oracle)


def _event(eid, date, modified_stages, fault_type=FaultType.quality):
    return Event(event_id=eid, baseline_sha="b" * 12, candidate_sha="b" * 12, fault_id=f"f-{eid}",
                 fault_source=FaultSource.mutation, fault_type=fault_type,
                 event_environment_id="env", split_group_id="b" * 12 + "+x",
                 event_date=date, train_or_test=TrainOrTest.test,
                 change_metadata={"modified_pass_stages": modified_stages}, mutation_family="x")


def _ctx():
    units = {
        "t_layout": _unit("t_layout", "ghz", "line", ["layout"]),
        "t_opt": _unit("t_opt", "qft", "line", ["optimization"]),
        "t_route": _unit("t_route", "qaoa_linear", "heavy_hex", ["routing"], oracle="structural"),
    }
    events = {
        "e_now": _event("e_now", "2026-06-12", ["optimization"]),
        "e_old": _event("e_old", "2025-01-01", ["layout"]),
    }
    baseline_costs = {
        ("e_now", "t_layout"): 0.30, ("e_now", "t_opt"): 0.10, ("e_now", "t_route"): 0.20,
        ("e_old", "t_layout"): 0.30, ("e_old", "t_opt"): 0.10, ("e_old", "t_route"): 0.20,
    }
    # history: in the OLD event, t_opt detected a fault; t_layout did not.
    history = [
        {"event_id": "e_old", "test_id": "t_opt", "label": "quality_regression", "event_date": "2025-01-01"},
        {"event_id": "e_old", "test_id": "t_layout", "label": "pass", "event_date": "2025-01-01"},
        # a FUTURE/current-event outcome that must be ignored for e_now:
        {"event_id": "e_now", "test_id": "t_layout", "label": "quality_regression", "event_date": "2026-06-12"},
    ]
    return SelectionContext(units=units, events=events, baseline_costs=baseline_costs, history=history)


def test_all_baselines_within_budget():
    ctx = _ctx()
    budget = 0.40
    for name in BASELINES:
        sel = run_baseline(name, ctx, "e_now", budget)
        spent = sum(expected_cost(ctx, "e_now", t) for t in sel)
        assert spent <= budget + 1e-9, f"{name} exceeded budget: {spent}"


def test_cheapest_first_orders_by_cost():
    ctx = _ctx()
    sel = run_baseline("cheapest_first", ctx, "e_now", budget_s=10.0)
    # t_opt (0.10) cheapest, then t_route (0.20), then t_layout (0.30)
    assert sel[0] == "t_opt"


def test_change_stage_prefers_modified_stage():
    ctx = _ctx()
    # e_now modified 'optimization' -> t_opt should rank first
    assert _change_stage_match(ctx, "e_now", "t_opt") == 1.0
    assert _change_stage_match(ctx, "e_now", "t_layout") == 0.0
    sel = run_baseline("change_stage", ctx, "e_now", budget_s=0.30)
    assert sel[0] == "t_opt"


def test_history_only_excludes_current_and_future():
    ctx = _ctx()
    # For e_now (2026), only e_old (2025) history counts; e_now's own outcome must be ignored.
    r_opt = ctx.prior_failure_rate("t_opt", "2026-06-12", exclude_event="e_now")
    r_layout = ctx.prior_failure_rate("t_layout", "2026-06-12", exclude_event="e_now")
    assert r_opt == 1.0          # detected in e_old
    assert r_layout == 0.0       # passed in e_old; the e_now 'fail' is excluded (leakage)
    # budget 0.20 fits only t_opt (expected_cost = 0.10 cost + 0.05 oracle = 0.15)
    sel = run_baseline("history_only", ctx, "e_now", budget_s=0.20)
    assert sel == ["t_opt"]


def test_random_deterministic_with_seed():
    ctx = _ctx()
    a = run_baseline("random", ctx, "e_now", 10.0, seed=42)
    b = run_baseline("random", ctx, "e_now", 10.0, seed=42)
    assert a == b
