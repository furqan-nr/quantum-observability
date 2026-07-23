"""Scaffold smoke tests. Real phase tests are added per PROJECT_PLAN.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cli_importable():
    from cart.cli import build_parser
    assert build_parser().prog == "cart"


def test_configs_present():
    cfg = ROOT / "configs"
    for name in ["stage_map.yaml", "thresholds.yaml", "budgets.yaml", "seeds.yaml", "cutoff.yaml"]:
        assert (cfg / name).exists(), f"missing config: {name}"


def test_data_dirs_present():
    data = ROOT / "data"
    for name in ["manifest_static", "profile_baseline", "events", "raw", "derived"]:
        assert (data / name).is_dir(), f"missing data dir: {name}"
