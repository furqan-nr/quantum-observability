"""Static test manifest builder (METHODOLOGY §0.3 -- ``test_manifest_static``).

Pure metadata, producible before any run. Cost, executed passes, routing, and memory
are NOT here -- they are measured later into ``test_profile_baseline`` (Phase 2).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from cart.manifest.circuits import CIRCUIT_FAMILIES, build
from cart.manifest.backends import BACKENDS

# Default pilot enumeration knobs (kept small for a single-laptop pilot).
DEFAULT_WIDTHS = (5, 8, 12, 18)
DEFAULT_BACKENDS = ("line", "heavy_hex")
DEFAULT_OPT_LEVELS = (1, 3)
DEFAULT_BASIS = ("cx", "rz", "sx", "x")

# Exact-unitary feasible width ceiling and sampled-statevector ceiling (METHODOLOGY §2.2).
UNITARY_MAX_QUBITS = 12
SAMPLED_SV_MAX_QUBITS = 22


@dataclass(frozen=True)
class TestUnit:
    __test__ = False   # not a pytest test class despite the 'Test' prefix
    test_id: str
    circuit_family: str
    n_qubits: int
    backend_id: str
    transpiler_config_id: str
    declared_pass_stages: tuple[str, ...]
    oracle_type: str


def _oracle_type(measured: bool, n: int) -> str:
    """Assign oracle tier from applicability (§2.2): unitary/statevector only for
    unitary-pure circuits; measured/non-unitary circuits use property/structural."""
    if measured:
        return "property" if n <= SAMPLED_SV_MAX_QUBITS else "structural"
    if n <= UNITARY_MAX_QUBITS:
        return "unitary"
    if n <= SAMPLED_SV_MAX_QUBITS:
        return "sampled_sv"
    return "structural"


def _declared_stages(opt_level: int) -> tuple[str, ...]:
    """Declarative (expected) stages for a preset pass manager at this level.
    Validated against executed_pass_stages during baseline profiling (§0.3)."""
    if opt_level <= 0:
        return ("layout", "routing", "translation")
    return ("layout", "routing", "translation", "optimization", "analysis")


def enumerate_test_units(
    *,
    families: tuple[str, ...] = CIRCUIT_FAMILIES,
    widths: tuple[int, ...] = DEFAULT_WIDTHS,
    backends: tuple[str, ...] = DEFAULT_BACKENDS,
    opt_levels: tuple[int, ...] = DEFAULT_OPT_LEVELS,
    measured: bool = False,
) -> list[TestUnit]:
    units: list[TestUnit] = []
    for fam in families:
        for n in widths:
            for backend in backends:
                if backend not in BACKENDS:
                    raise KeyError(f"unknown backend {backend!r}")
                for opt in opt_levels:
                    cfg_id = f"opt{opt}+basis-{'_'.join(DEFAULT_BASIS)}"
                    test_id = f"{fam}-n{n}-{backend}-opt{opt}"
                    units.append(
                        TestUnit(
                            test_id=test_id,
                            circuit_family=fam,
                            n_qubits=n,
                            backend_id=backend,
                            transpiler_config_id=cfg_id,
                            declared_pass_stages=_declared_stages(opt),
                            oracle_type=_oracle_type(measured, n),
                        )
                    )
    return units


def build_static_manifest(out_dir: str | Path, **kwargs: object) -> Path:
    """Build and write test_manifest_static as JSON. Returns the artifact path."""
    units = enumerate_test_units(**kwargs)  # type: ignore[arg-type]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "manifest_static.json"
    payload = {
        "schema": "test_manifest_static/v1",
        "fields": list(TestUnit.__dataclass_fields__.keys()),
        "n_units": len(units),
        "units": [asdict(u) for u in units],
    }
    out_path.write_text(json.dumps(payload, indent=2, default=list))
    return out_path


def validate_circuits_constructible(units: list[TestUnit], *, seed: int = 0) -> int:
    """Sanity check: every (family, n) in the manifest actually constructs. Returns count."""
    seen = set()
    for u in units:
        key = (u.circuit_family, u.n_qubits)
        if key in seen:
            continue
        build(u.circuit_family, u.n_qubits, seed=seed)  # raises on failure
        seen.add(key)
    return len(seen)
