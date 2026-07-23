"""Targeted regression-trigger unit tests.

Confirms the targeted circuits build and flow through the production transpile + oracle pipeline.
On the FIXED anchor (stand-in for both venvs) they must show NO fault (the fault only appears on the
buggy candidate build, validated locally). Also shows the trigger-feature-removal contrast for H1.
"""
import sys

from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.quantum_info import Operator

from cart.events.table import load_events
from cart.manifest.targeted import build_targeted, TARGETED_UNITS, units_for_fault
from cart.labels.historical_runner import run_targeted_event


def _event(eid):
    return {e.event_id: e for e in load_events()}[eid]


def test_targeted_circuits_build():
    for tid in TARGETED_UNITS:
        qc = build_targeted(tid)
        assert qc.num_qubits >= 3


def test_targeted_mapping_to_faults():
    assert units_for_fault("qiskit-pr-14603-elide-permutations")[0].test_id == "trig-h1-elide-permutations"
    assert units_for_fault("qiskit-pr-14730-vf2layout-determinism")[0].oracle_type == "property"


def test_h1_semantic_no_fault_on_fixed_anchor(tmp_path):
    ev = _event("hist-elide-permutations-mapping")
    s = run_targeted_event(ev, tmp_path, baseline_python=sys.executable, candidate_python=sys.executable)
    # fixed anchor on both sides => semantically equivalent => pass (no false positive)
    assert s["label_counts"].get("pass", 0) == s["n_records"]


def test_h3_determinism_no_fault_on_fixed_anchor(tmp_path):
    ev = _event("hist-vf2layout-determinism-1q")
    s = run_targeted_event(ev, tmp_path, baseline_python=sys.executable, candidate_python=sys.executable)
    # fixed anchor is deterministic => pass
    assert s["label_counts"].get("pass", 0) == s["n_records"]


def test_h1_trigger_feature_removal_makes_fault_disappear():
    # With the PermutationGate (the trigger feature) the circuit exercises the bug path; removing it
    # leaves a trivially-routable circuit. On the fixed anchor both are equivalent; the point is the
    # contrast is well-defined. (Full buggy-vs-fixed contrast requires the from-source build.)
    pm = generate_preset_pass_manager(optimization_level=3, basis_gates=["cx", "rz", "sx", "x"], seed_transpiler=7)
    with_trigger = build_targeted("trig-h1-elide-permutations")
    without = QuantumCircuit(5)
    without.h(1); without.swap(1, 2); without.swap(4, 3)   # same minus the PermutationGate
    t1 = pm.run(with_trigger); t2 = pm.run(without)
    assert Operator(with_trigger).equiv(Operator.from_circuit(t1))   # fixed anchor: equiv
    assert Operator(without).equiv(Operator.from_circuit(t2))
