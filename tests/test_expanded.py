"""Tests for the EMSE expansion: new mutation operators + statistical helpers.

Operator tests need Qiskit (run on the harness/anchor venv). Stats tests are dependency-free.
"""
from cart.metrics.curves import (cliffs_delta, cliffs_magnitude, vargha_delaney_a12, bootstrap_ci)


# ---- statistical helpers (no Qiskit) ----

def test_cliffs_delta_handcomputed():
    assert cliffs_delta([2, 2, 2], [1, 1, 1]) == 1.0
    assert cliffs_delta([1, 1, 1], [2, 2, 2]) == -1.0
    assert cliffs_delta([1, 2, 3], [1, 2, 3]) == 0.0


def test_vargha_delaney_a12_handcomputed():
    assert vargha_delaney_a12([2, 2], [1, 1]) == 1.0
    assert vargha_delaney_a12([1, 1], [1, 1]) == 0.5
    assert vargha_delaney_a12([1, 1], [2, 2]) == 0.0


def test_cliffs_magnitude_thresholds():
    assert cliffs_magnitude(0.0) == "negligible"
    assert cliffs_magnitude(0.2) == "small"
    assert cliffs_magnitude(0.4) == "medium"
    assert cliffs_magnitude(0.8) == "large"


def test_bootstrap_ci_bounds():
    ci = bootstrap_ci([0.5] * 10)
    assert ci == {"mean": 0.5, "lo": 0.5, "hi": 0.5}
    ci2 = bootstrap_ci([0.0, 1.0, 0.0, 1.0], seed=1)
    assert 0.0 <= ci2["lo"] <= ci2["mean"] <= ci2["hi"] <= 1.0


# ---- new mutation operators (need Qiskit) ----

NEW_OPERATORS = ["drop_optimization_stage", "force_opt_level_1", "force_opt_level_0",
                 "downgrade_layout_trivial", "insert_redundant_x_pair"]


def _cfg():
    from qiskit.transpiler import CouplingMap
    return dict(optimization_level=3, coupling_map=CouplingMap.from_line(5),
                basis_gates=["cx", "rz", "sx", "x"], seed_transpiler=1234)


def _circ():
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(5)
    qc.h(0)
    for i in range(4):
        qc.cx(i, i + 1)
    return qc


def test_new_operators_registered():
    from cart.events.mutations import MUTATION_OPERATORS
    for fam in NEW_OPERATORS:
        assert fam in MUTATION_OPERATORS, fam


def test_new_quality_operators_run():
    from cart.events.mutations import get_operator
    c = _circ()
    for fam in NEW_OPERATORS:
        out = get_operator(fam).transpiler(_cfg())(c)
        assert out is not None and out.num_qubits == 5


def test_insert_x_pair_adds_two_x_gates():
    from cart.events.mutations import baseline_transpiler, get_operator
    cfg = _cfg()
    c = _circ()
    base = baseline_transpiler(cfg)(c)
    mut = get_operator("insert_redundant_x_pair").transpiler(cfg)(c)
    bx = sum(1 for i in base.data if i.operation.name == "x")
    mx = sum(1 for i in mut.data if i.operation.name == "x")
    assert mx == bx + 2
