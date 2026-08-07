"""
dashboard/styles.py — Backward-compatible re-export shim.

All logic now lives in pulseengine.local.styles.
New code should import directly from there.

Names are re-exported explicitly with `as` aliases rather than `import *`:
that is the form both mypy and IDE inspectors recognise as a deliberate
re-export, so the shim no longer reads as a file full of unused imports.
"""

from __future__ import annotations

from pulseengine.local.styles import (
    CSS_FILENAME as CSS_FILENAME,
)
from pulseengine.local.styles import (
    load_css as load_css,
)
from pulseengine.local.styles import (
    read_css as read_css,
)

__all__ = [
    "CSS_FILENAME",
    "load_css",
    "read_css",
]
