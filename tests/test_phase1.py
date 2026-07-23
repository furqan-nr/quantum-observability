"""Phase 1 tests: event schema/table, split groups, validation, mutation engine."""
import copy

from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap

from cart.events.schema import Event, FaultSource, FaultType, TrainOrTest
from cart.events.table import compute_split_group_id, load_events, save_events, assign_splits_group_level
from cart.events.validate import validate_events
from cart.events.mutations import MUTATION_OPERATORS, baseline_transpiler, get_operator

BASE_CFG = dict(optimization_level=2, coupling_map=CouplingMap.from_line(6),
                basis_gates=["cx", "rz", "sx", "x"], seed_transpiler=1)


def _circuit():
    qc = QuantumCircuit(6)
    qc.h(range(6))
    for i in range(5):
        qc.cx(i, i + 1)
    return qc


def test_compute_split_group_id():
    assert compute_split_group_id("abcdef0123456789", "downgrade_routing") == "abcdef012345+downgrade_routing"
    assert compute_split_group_id("abcdef0123456789", None) == "abcdef012345"


def test_seed_table_validates():
    events = load_events()
    assert events, "seed events.json missing"
    rep = validate_events(events, require_ready=False)
    assert rep.ok, f"seed table invalid: {rep.errors}"
    assert rep.counts["historical"] == 5
    assert rep.counts["mutation"] == 9    # expanded mutation corpus (EMSE): 4 original + 5 new
    assert rep.counts["distinct_fault_ids"] == len(events)


def test_split_group_integrity_detected():
    events = load_events()
    # Force two mutation events into the SAME group but opposite splits -> leakage error.
    bad = copy.deepcopy([e.to_dict() for e in events])
    g = bad[0]["split_group_id"]
    bad[1]["split_group_id"] = g
    bad[1]["baseline_sha"] = bad[0]["baseline_sha"]
    bad[1]["mutation_family"] = bad[0]["mutation_family"]
    bad[0]["train_or_test"] = "train"
    bad[1]["train_or_test"] = "test"
    evs = [Event.from_dict(d) for d in bad]
    rep = validate_events(evs)
    assert any("spans both train and test" in e for e in rep.errors)


def test_duplicate_fault_id_detected():
    events = load_events()
    d = [e.to_dict() for e in events]
    d[1]["fault_id"] = d[0]["fault_id"]
    rep = validate_events([Event.from_dict(x) for x in d])
    assert any("duplicate fault_id" in e for e in rep.errors)


def test_require_ready_passes_with_real_shas():
    events = load_events()
    rep = validate_events(events, require_ready=True)
    # historical events now carry real git SHAs -> no SHA-format errors
    assert not any("not a real SHA" in e for e in rep.errors)
    assert rep.ok, rep.errors


def test_event_roundtrip():
    e = load_events()[0]
    assert Event.from_dict(e.to_dict()).to_dict() == e.to_dict()


def test_group_level_split_no_straddle():
    events = load_events()
    out = assign_splits_group_level(events, "2026-01-01")
    rep = validate_events(out)
    assert not any("spans both" in e for e in rep.errors)


def test_mutation_operators_callable_and_change_output():
    import pytest
    from cart.events.schema import FaultType
    qc = _circuit()
    base_out = baseline_transpiler(BASE_CFG)(qc)
    base_2q = sum(1 for d in base_out.data if d.operation.num_qubits == 2 and d.operation.name != "barrier")
    # quality operators build a working transpiler; functional operators trigger a natural
    # transpilation failure by design.
    for fam, op in MUTATION_OPERATORS.items():
        if op.fault_type == FaultType.functional:
            with pytest.raises(Exception):
                op.transpiler(BASE_CFG)(qc)
            continue
        out = op.transpiler(BASE_CFG)(qc)
        assert out.num_qubits >= qc.num_qubits, f"{fam} produced invalid circuit"
    # insert_redundant_cx_pair deterministically adds 2 two-qubit gates
    ins = get_operator("insert_redundant_cx_pair").transpiler(BASE_CFG)(qc)
    ins_2q = sum(1 for d in ins.data if d.operation.num_qubits == 2 and d.operation.name != "barrier")
    assert ins_2q == base_2q + 2
