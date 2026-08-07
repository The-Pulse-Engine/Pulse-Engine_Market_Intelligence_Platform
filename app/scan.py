"""
app/scan.py — Backward-compatible re-export shim.

All logic now lives in pulseengine.local.scan.
New code should import directly from there.

Names are re-exported explicitly with `as` aliases rather than `import *`:
that is the form both mypy and IDE inspectors recognise as a deliberate
re-export, so the shim no longer reads as a file full of unused imports.

`python -m app.scan` keeps working, including its flags.
"""

from __future__ import annotations

from pulseengine.local.scan import (
    load_last_scan_summary as load_last_scan_summary,
)
from pulseengine.local.scan import (
    main as main,
)
from pulseengine.local.scan import (
    run_scan as run_scan,
)

__all__ = [
    "load_last_scan_summary",
    "main",
    "run_scan",
]

if __name__ == "__main__":
    main()
