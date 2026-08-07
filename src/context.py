"""
src/context.py — Backward-compatible re-export shim.

All logic now lives in pulseengine.core.context.
New code should import directly from there.

Names are re-exported explicitly with `as` aliases rather than `import *`:
that is the form both mypy and IDE inspectors recognise as a deliberate
re-export, so the shim no longer reads as a file full of unused imports.
"""

from __future__ import annotations

from pulseengine.core.context import (
    analyse_market_context as analyse_market_context,
)
from pulseengine.core.context import (
    find_category as find_category,
)

__all__ = [
    "analyse_market_context",
    "find_category",
]
