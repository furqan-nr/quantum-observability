"""Phase 4 tests: connectivity feature + proposed risk_score selector."""
from qiskit.transpiler import CouplingMap

from cart.events.schema import Event, FaultSource, FaultType, TrainOrTest
from cart.manifest.static_manifest import TestUnit
from cart.manifest.circuits import build
from cart.features.connectivity import connectivity_pressure, interaction_edges
from cart.selectors.context import SelectionContext
from cart.selectors.cost_model import expected_cost
from cart.selectors.proposed import proposed_selector


def test_connectivity_pressure_line_vs_allpairs():
    ghz = build("ghz", 5, measured=False)        # chain interactions -> adjacent on a line
    assert connectivity_pressure(ghz, CouplingMap.from_line(5)) == 0
    qft = build("qft", 5, measured=False)         # long-range interactions -> pressure on a line
    assert connectivity_pressure(qft, CouplingMap.from_line(5)) > 0
    assert len(interaction_edges(ghz)) >= 4


def _unit(tid, fam, backend, stages, oracle="unitary", n=5):
    return TestUnit(test_id=tid, circuit_family=fam, n_qubits=n, backend_id=backend,
                    transpiler_config_id="opt1+basis", declared_pass_stages=tuple(stages), oracle_type=oracle)


def _ctx():
    units = {
        "ghz-line": _unit("ghz-line", "ghz", "line", ["layout"]),
        "qft-line": _unit("qft-line", "qft", "line", ["optimization"]),
        "qaoa-line": _unit("qaoa-line", "qaoa_linear", "line", ["routing"]),
    }
    events = {"e": Event(event_id="e", baseline_sha="b" * 12, candidate_sha="b" * 12, fault_id="f",
                         fault_source=FaultSource.mutation, fault_type=FaultType.quality,
                         event_environment_id="env", split_group_id="b" * 12 + "+x",
                         event_date="2026-06-12", train_or_test=TrainOrTest.test,
                         change_metadata={"modified_pass_stages": ["optimization"]}, mutation_family="x")}
    costs = {("e", "ghz-line"): 0.10, ("e", "qft-line"): 0.10, ("e", "qaoa-line"): 0.10}
    return SelectionContext(units=units, events=events, baseline_costs=costs, history=[])


def test_proposed_within_budget():
    ctx = _ctx()
    budget = 0.30
    sel = proposed_selector(ctx, "e", budget)
    spent = sum(expected_cost(ctx, "e", t) for t in sel)
    assert spent <= budget + 1e-9


def test_proposed_deterministic():
    ctx = _ctx()
    assert proposed_selector(ctx, "e", 0.40) == proposed_selector(ctx, "e", 0.40)


def test_proposed_prefers_modified_stage_first():
    ctx = _ctx()
    # event modified 'optimization' -> qft-line (stages=[optimization]) should be picked first
    sel = proposed_selector(ctx, "e", budget_s=0.20)
    assert sel and sel[0] == "qft-line"


def test_proposed_diversity_covers_families_when_budget_allows():
    ctx = _ctx()
    sel = proposed_selector(ctx, "e", budget_s=10.0)
    fams = {ctx.test_meta(t).circuit_family for t in sel}
    assert {"ghz", "qft", "qaoa_linear"} <= fams


def test_proposed_uses_no_candidate_labels():
    # context has empty history (no labels at all) -> selector must still work (no leakage dependency)
    ctx = _ctx()
    assert proposed_selector(ctx, "e", 0.30)
