"""
styles.py — CSS theming for the PulseEngine local dashboard.

Retro Financial Broadsheet palette.  Call load_css() once at the top of
dashboard.py, immediately after st.set_page_config().

The stylesheet itself lives in dashboard.css next to this module rather than in
a Python string, so editors syntax-highlight it and it is not subject to Python
line-length rules. It is read through importlib.resources, which resolves both
from a source checkout and from an installed wheel — a __file__-relative path
would work in the checkout and silently lose all styling once installed.
"""

from __future__ import annotations

from functools import lru_cache
from importlib import resources

import streamlit as st

CSS_FILENAME = "dashboard.css"


@lru_cache(maxsize=1)
def read_css() -> str:
    """Return the dashboard stylesheet. Cached: the file never changes at runtime."""
    return (
        resources.files("pulseengine.local")
        .joinpath(CSS_FILENAME)
        .read_text(encoding="utf-8")
    )


def load_css() -> None:
    """Inject the full Retro Financial Broadsheet stylesheet into Streamlit."""
    st.markdown(f"<style>\n{read_css()}\n</style>", unsafe_allow_html=True)
