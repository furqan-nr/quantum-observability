"""Tests for the minimal per-event from-source venv runner.

Validates the runner MECHANICS (subprocess worker + QPY round-trip + oracle/label) using the
current interpreter as a stand-in for both per-event venvs. Real historical validation requires the
actual from-source builds on the laptop.
"""
import sys

from cart.events.table import load_events
from cart.manifest.static_manifest import enumerate_test_units
from cart.labels.historical_runner import run_historical_event


def _event(eid):
    return {e.event_id: e for e in load_events()}[eid]


def _units(k):
    return enumerate_test_units()[:k]


def test_runner_standin_same_version_no_correctness_fault(tmp_path):
    # Same interpreter on both sides => identical transpile => no correctness/quality fault.
    ev = _event("hist-vf2postlayout-noop")
    s = run_historical_event(ev, _units(2), tmp_path,
                             baseline_python=sys.executable, candidate_python=sys.executable)
    assert s["n_records"] == 2
    # Only pass or (noisy, exploratory) performance_regression are acceptable here.
    assert set(s["label_counts"]) <= {"pass", "performance_regression"}


def test_runner_functional_path_incomplete_basis(tmp_path):
    # Functional fixture: candidate uses an incomplete basis -> natural TranspilerError -> functional_fail.
    ev = _event("hist-vf2layout-panic-1p0")   # fault_type = functional
    s = run_historical_event(ev, _units(2), tmp_path,
                             baseline_python=sys.executable, candidate_python=sys.executable,
                             candidate_basis=["cx"])
    assert s["label_counts"].get("functional_fail", 0) >= 1


def test_runner_missing_venv_raises_with_instructions(tmp_path):
    import pytest
    from dataclasses import replace
    # Point at a guaranteed-absent event_environment_id so the result is deterministic regardless of
    # which per-event venvs the user has actually built locally.
    ev = replace(_event("hist-elide-permutations-mapping"),
                 event_environment_id="zzz-unbuilt-env-does-not-exist")
    with pytest.raises(FileNotFoundError):
        run_historical_event(ev, _units(1), tmp_path)  # no python overrides, venvs absent
