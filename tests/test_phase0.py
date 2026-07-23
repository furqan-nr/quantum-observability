"""Phase 0 unit tests: stage mapping, instrumentation, static manifest."""
from cart.features.stage_map import StageMap
from cart.manifest.circuits import build, CIRCUIT_FAMILIES
from cart.manifest.backends import coupling_map_for
from cart.manifest.instrumentation import instrumented_transpile
from cart.manifest.static_manifest import enumerate_test_units, _oracle_type


def test_stage_map_prefixes():
    sm = StageMap.load()
    assert sm.stage_for("qiskit.transpiler.passes.layout.vf2_layout") == "layout"
    assert sm.stage_for("qiskit.transpiler.passes.synthesis.high_level_synthesis") == "translation"
    assert sm.stage_for("qiskit.transpiler.passes.optimization.elide_permutations") == "optimization"
    assert sm.stage_for("qiskit.transpiler.passes.utils.check_map") == "analysis"
    # unknown path -> default broad stage
    assert sm.stage_for("qiskit/transpiler/passes/totally_new/foo") == sm.default_stage
    assert sm.is_broad("shared_utility_unknown")


def test_oracle_type_rule():
    assert _oracle_type(False, 8) == "unitary"
    assert _oracle_type(False, 18) == "sampled_sv"
    assert _oracle_type(False, 30) == "structural"
    assert _oracle_type(True, 8) == "property"      # measured -> never unitary/statevector
    assert _oracle_type(True, 30) == "structural"


def test_circuits_constructible():
    for fam in CIRCUIT_FAMILIES:
        qc = build(fam, 5, seed=1)
        assert qc.num_qubits == 5


def test_instrumentation_captures_executed_stages():
    qc = build("ghz", 6, seed=1)
    cmap = coupling_map_for("line", 6)
    out, res = instrumented_transpile(qc, coupling_map=cmap, optimization_level=2, seed_transpiler=7)
    assert res.transpilation_time_s > 0
    assert res.executed_passes, "no passes captured"
    # executed stages are canonical and non-empty
    assert res.executed_pass_stages
    assert all(s in StageMap.load().canonical_stages for s in res.executed_pass_stages)
    assert "out_op_counts" in res.routing_observations


def test_manifest_enumeration_nonempty_and_fields():
    units = enumerate_test_units()
    assert units
    u = units[0]
    assert u.test_id and u.circuit_family and u.backend_id
    assert u.oracle_type in {"unitary", "sampled_sv", "property", "structural"}
    assert set(u.declared_pass_stages).issubset(set(StageMap.load().canonical_stages))
