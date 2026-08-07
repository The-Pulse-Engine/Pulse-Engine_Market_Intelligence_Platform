"""
dashboard/data.py — Backward-compatible re-export shim.

All logic now lives in pulseengine.local.data.
New code should import directly from there.

Names are re-exported explicitly with `as` aliases rather than `import *`:
that is the form both mypy and IDE inspectors recognise as a deliberate
re-export, so the shim no longer reads as a file full of unused imports.
"""

from __future__ import annotations

from pulseengine.local.data import (
    cached_generated_keywords as cached_generated_keywords,
)
from pulseengine.local.data import (
    cached_history as cached_history,
)
from pulseengine.local.data import (
    cached_live_analysis as cached_live_analysis,
)
from pulseengine.local.data import (
    cached_news as cached_news,
)
from pulseengine.local.data import (
    cached_scan_summary as cached_scan_summary,
)
from pulseengine.local.data import (
    is_data_stale as is_data_stale,
)

__all__ = [
    "cached_generated_keywords",
    "cached_history",
    "cached_live_analysis",
    "cached_news",
    "cached_scan_summary",
    "is_data_stale",
]
