"""Contract tests for the legacy top-level import surface.

README.md and tests/MAINTENANCE.md both document the pre-`pulseengine/` module
paths (`src.*`, `app.*`, `config.settings`, `storage.storage`, `dashboard.*`) as
still functional. Nothing enforced that: the existing suite imports from
`pulseengine.core` directly, and test_web_surface.py only greps source text, so
a shim could break without a single test turning red.

These tests import each documented path and assert the re-exported names are the
same objects as their canonical counterparts.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

# Every legacy module path documented as supported.
LEGACY_MODULES = [
    "app.analysis",
    "app.backtest",
    "app.scan",
    "config.settings",
    "dashboard.components",
    "dashboard.data",
    "dashboard.styles",
    "src.context",
    "src.engine",
    "src.errors",
    "src.explanation",
    "src.news",
    "src.price",
    "src.sentiment",
    "src.signals",
    "storage.storage",
]

# Legacy path -> canonical path, for the shims that alias via sys.modules or
# re-export a specific name.
SHIM_TO_CANONICAL = [
    ("app.analysis", "analyse_asset", "pulseengine.core", "analyse_asset"),
    ("app.backtest", "evaluate_signal_accuracy", "pulseengine.core.backtest",
     "evaluate_signal_accuracy"),
    ("app.scan", "run_scan", "pulseengine.local.scan", "run_scan"),
    ("config.settings", "TRACKED_ASSETS", "pulseengine.core.config", "TRACKED_ASSETS"),
    ("src.engine", "analyse_asset", "pulseengine.core.app", "analyse_asset"),
    ("src.price", "compute_price_metrics", "pulseengine.core.price", "compute_price_metrics"),
    ("src.errors", "DataFetchError", "pulseengine.core.errors", "DataFetchError"),
    ("storage.storage", "save_snapshot", "pulseengine.core.storage", "save_snapshot"),
    ("storage.storage", "load_snapshots", "pulseengine.core.storage", "load_snapshots"),
]


@pytest.mark.parametrize("module_path", LEGACY_MODULES)
def test_legacy_module_imports(module_path):
    """Each documented legacy module path still imports."""
    assert importlib.import_module(module_path) is not None


@pytest.mark.parametrize(
    ("legacy_mod", "legacy_name", "canonical_mod", "canonical_name"), SHIM_TO_CANONICAL
)
def test_shim_reexports_same_object(legacy_mod, legacy_name, canonical_mod, canonical_name):
    """A shim must hand back the canonical object, not a copy or a stale rebind."""
    legacy = getattr(importlib.import_module(legacy_mod), legacy_name)
    canonical = getattr(importlib.import_module(canonical_mod), canonical_name)
    assert legacy is canonical


def test_sys_modules_aliasing_shims_resolve_to_core():
    """src.engine, src.price and storage.storage replace themselves in sys.modules.

    That aliasing is what lets tests monkeypatch `src.engine.fetch_price_history`
    and have the core module see it. Assert the alias actually took effect.
    """
    import pulseengine.core.app
    import pulseengine.core.price
    import pulseengine.core.storage

    assert importlib.import_module("src.engine") is pulseengine.core.app
    assert importlib.import_module("src.price") is pulseengine.core.price
    assert importlib.import_module("storage.storage") is pulseengine.core.storage


def test_legacy_dashboard_entry_point_is_intact():
    """`streamlit run dashboard/main.py` must keep working.

    Deliberately NOT an import: dashboard/main.py exec()s the canonical dashboard
    at module scope, so importing it would run the whole Streamlit app inside the
    test session. This checks the two things that actually break — the wrapper
    failing to compile, and the exec target moving — without executing it.
    """
    root = Path(__file__).resolve().parents[1]
    wrapper = root / "dashboard" / "main.py"
    canonical = root / "pulseengine" / "local" / "dashboard.py"

    assert wrapper.is_file(), "legacy dashboard entry point is missing"
    assert canonical.is_file(), "dashboard/main.py exec target has moved"
    # Raises SyntaxError if the wrapper itself is malformed.
    compile(wrapper.read_text(encoding="utf-8"), str(wrapper), "exec")


# The documented public UI surface, frozen here on purpose. Asserting only
# "the shim exports whatever __all__ says" would pass if a name were dropped
# from both sides at once; this list is the independent third party.
PUBLIC_COMPONENTS = {
    "render_article",
    "render_category_overview",
    "render_data_status_banner",
    "render_heatmap",
    "render_live_analysis",
    "render_mover_rows",
    "render_news_section",
    "render_scan_status_sidebar",
    "render_signal_card",
    "render_signal_legend_sidebar",
    "render_snapshot_metrics",
    "render_why_box",
    "sidebar_header_html",
}


def test_component_star_import_contract():
    """`from dashboard.components import *` must yield exactly the documented set.

    components/ is a package now, so the star-import path runs through
    __init__.__all__. This exercises real star-import semantics rather than
    trusting that importing the module is enough, and checks identity so a
    stale copy re-exported from the shim cannot pass.
    """
    import pulseengine.local.components as canonical

    assert set(canonical.__all__) == PUBLIC_COMPONENTS

    namespace: dict[str, object] = {}
    exec("from dashboard.components import *", namespace)
    exported = set(namespace) - {"__builtins__"}

    assert exported == PUBLIC_COMPONENTS
    for name in PUBLIC_COMPONENTS:
        assert namespace[name] is getattr(canonical, name)


def test_dashboard_calls_only_documented_components():
    """Every ui.<name> the dashboard calls must be in the public contract."""
    source = (
        Path(__file__).resolve().parents[1] / "pulseengine" / "local" / "dashboard.py"
    ).read_text(encoding="utf-8")
    used = set(re.findall(r"\bui\.([a-zA-Z_][a-zA-Z0-9_]*)", source))
    assert used <= PUBLIC_COMPONENTS, f"undocumented component(s): {used - PUBLIC_COMPONENTS}"


def test_version_is_single_sourced():
    """pulseengine.__version__ is the one place the version is written.

    pyproject.toml derives its version from this attribute, so a future edit that
    re-hardcodes `version = "..."` under [project] would reintroduce the drift
    this test exists to prevent (pyproject said 0.3.2 while the package said
    0.3.0). Assert the dynamic wiring is still in place, not a literal value.
    """
    import tomllib

    import pulseengine

    assert re.fullmatch(r"\d+\.\d+\.\d+", pulseengine.__version__)

    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    cfg = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    assert "version" not in cfg["project"], "version must not be hardcoded in [project]"
    assert "version" in cfg["project"]["dynamic"]
    assert cfg["tool"]["setuptools"]["dynamic"]["version"]["attr"] == "pulseengine.__version__"
