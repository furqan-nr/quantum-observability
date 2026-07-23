"""Phase 2 tests: tiered oracles + ground-truth labels."""
from pathlib import Path

from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager, CouplingMap

from cart.events.table import load_events
from cart.manifest.static_manifest import enumerate_test_units
from cart.oracles.semantic import check_semantic, is_unitary_pure
from cart.oracles.quality import evaluate_quality
from cart.labels.ground_truth import run_event_test, run_ground_truth


def _line_unit():
    for u in enumerate_test_units():
        if u.backend_id == "line" and u.circuit_family == "ghz" and u.n_qubits == 5 and u.transpiler_config_id.startswith("opt1"):
            return u
    raise AssertionError("expected ghz-n5-line-opt1 unit")


def _event(fault_id_sub):
    for e in load_events():
        if fault_id_sub in e.event_id:
            return e
    raise AssertionError(f"event {fault_id_sub} not found")


def test_semantic_oracle_exact_and_corruption():
    qc = QuantumCircuit(4); qc.h(0); qc.cx(0, 1); qc.cx(1, 2); qc.cx(2, 3); qc.t(3)
    cmap = CouplingMap.from_line(4)
    tqc = generate_preset_pass_manager(optimization_level=3, coupling_map=cmap,
                                       basis_gates=["cx", "rz", "sx", "x"], seed_transpiler=7).run(qc)
    ok = check_semantic(qc, tqc, coupling_map=cmap, basis_gates=["cx", "rz", "sx", "x"])
    assert ok.strength == "exact" and ok.equivalent is True and ok.layout_normalization_applied
    bad = tqc.copy(); bad.x(0)
    assert check_semantic(qc, bad, coupling_map=cmap).equivalent is False


def test_quality_identical_not_regression():
    qc = QuantumCircuit(5); qc.h(0)
    for i in range(4): qc.cx(i, i + 1)
    out = generate_preset_pass_manager(optimization_level=1, coupling_map=CouplingMap.from_line(5),
                                       basis_gates=["cx", "rz", "sx", "x"], seed_transpiler=1).run(qc)
    res = evaluate_quality(out, out)
    assert res.is_regression is False and res.delta_2q == 0


def test_semantic_oracle_memory_safe_on_large_circuit():
    # Regression guard: must NOT build a full 2^n operator for large circuits (would be 512 GiB at
    # 18 qubits). Large unitary-pure circuits fall to the structural tier.
    from qiskit import QuantumCircuit
    from qiskit.transpiler import generate_preset_pass_manager, CouplingMap
    qc = QuantumCircuit(18)
    qc.h(range(18))
    for i in range(17):
        qc.cx(i, i + 1)
    cmap = CouplingMap.from_line(18)
    tqc = generate_preset_pass_manager(optimization_level=1, coupling_map=cmap,
                                       basis_gates=["cx", "rz", "sx", "x"], seed_transpiler=1).run(qc)
    res = check_semantic(qc, tqc, coupling_map=cmap, basis_gates=["cx", "rz", "sx", "x"])
    assert res.strength == "structural"          # not exact/sampled -> no full operator built
    assert res.equivalent is None


def test_is_unitary_pure():
    qc = QuantumCircuit(2); qc.h(0); qc.cx(0, 1)
    assert is_unitary_pure(qc)
    qc.measure_all()
    assert not is_unitary_pure(qc)


def test_insert_redundant_cx_labeled_quality_regression(tmp_path):
    ev = _event("insert-redundant-cx")
    unit = _line_unit()
    rec, prof = run_event_test(ev, unit, tmp_path)
    assert rec.label == "quality_regression", rec.label
    assert rec.oracle_equivalent is True          # semantics preserved (CX-CX = I)
    assert rec.delta_2q == 2
    assert rec.fault_id_detected == ev.fault_id
    assert prof["test_id"] == unit.test_id and prof["event_id"] == ev.event_id


def test_label_reproducible_and_raw_write_once(tmp_path):
    ev = _event("insert-redundant-cx")
    unit = _line_unit()
    r1, _ = run_event_test(ev, unit, tmp_path)
    r2, _ = run_event_test(ev, unit, tmp_path)
    assert r1.label == r2.label
    assert r1.raw_sha256 == r2.raw_sha256          # deterministic evidence
    assert Path(r1.raw_artifact).exists()


def test_run_ground_truth_skips_historical(tmp_path):
    events = load_events()
    units = enumerate_test_units()
    summary = run_ground_truth(events, units, tmp_path, unit_limit=2)
    assert summary["n_events_skipped"] == 5        # 5 historical events skipped (need source builds)
    assert summary["n_records"] == 9 * 2           # 9 mutation events (expanded corpus) x 2 units
    assert Path(summary["labels_path"]).exists()
    assert Path(summary["profiles_path"]).exists()
