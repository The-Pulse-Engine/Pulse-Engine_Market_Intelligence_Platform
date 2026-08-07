"""Regression tests for the PulseEngine local surface.

Mirrors tests/test_web_surface.py. The focus here is the dashboard stylesheet,
which moved out of a Python string into a packaged data file: that swap trades a
loud ImportError for a silent "dashboard renders unstyled", so the resource
being present and reachable needs asserting rather than assuming.
"""

from __future__ import annotations

from pathlib import Path

from pulseengine.local import styles

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stylesheet_is_readable_as_a_package_resource():
    """read_css() must resolve via importlib.resources, not a __file__ path.

    A __file__-relative lookup passes in a source checkout and fails once the
    package is installed, so this asserts the resource loads and is non-trivial.
    """
    css = styles.read_css()
    assert len(css) > 1000, "stylesheet looks truncated or empty"
    assert ":root" in css, "expected CSS custom properties block"


def test_stylesheet_file_sits_inside_the_package():
    """The .css must live under pulseengine/local/ so package-data ships it."""
    css_path = REPO_ROOT / "pulseengine" / "local" / styles.CSS_FILENAME
    assert css_path.is_file(), f"{styles.CSS_FILENAME} missing from pulseengine/local/"


def test_stylesheet_is_declared_as_package_data():
    """Without this pyproject entry the wheel silently omits the stylesheet."""
    import tomllib

    cfg = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    patterns = cfg["tool"]["setuptools"]["package-data"]["pulseengine.local"]
    assert any(p.endswith(".css") for p in patterns)


def test_sidebar_logo_resolves_to_the_real_asset():
    """_build_logo_html() must find assets/logo/, not fall back to the icon.

    The helper walks up to the repo root. It moved one directory deeper when
    components.py became components/, so the parent depth had to change with it.
    Getting that wrong is silent: the function returns the emoji fallback and
    nothing raises, so only asserting the real image is embedded catches it.

    Scope: a source checkout, which is the documented way to run the dashboard.
    assets/ sits outside the package and so is absent from a built wheel; both
    the logo here and the favicon in core/config.py fall back gracefully there.
    That is a pre-existing packaging gap, not something this test guards.
    """
    from pulseengine.local.components import sidebar

    assert sidebar._LOGO_HTML.startswith('<img src="data:image/png;base64,'), (
        "logo fell back to the icon — check the parents[] depth in _build_logo_html"
    )


def test_load_css_wraps_the_sheet_in_a_style_tag(monkeypatch):
    """load_css() injects the stylesheet; the <style> wrapper lives in Python now."""
    captured: dict[str, object] = {}

    def fake_markdown(body, **kwargs):
        captured["body"] = body
        captured["kwargs"] = kwargs

    monkeypatch.setattr(styles.st, "markdown", fake_markdown)
    styles.load_css()

    body = captured["body"]
    assert isinstance(body, str)
    assert body.startswith("<style>")
    assert body.rstrip().endswith("</style>")
    assert captured["kwargs"].get("unsafe_allow_html") is True
