"""
src/errors.py — Backward-compatible re-export shim.

All logic now lives in pulseengine.core.errors.
New code should import directly from there.

Names are re-exported explicitly with `as` aliases rather than `import *`:
that is the form both mypy and IDE inspectors recognise as a deliberate
re-export, so the shim no longer reads as a file full of unused imports.
"""

from __future__ import annotations

from pulseengine.core.errors import (
    DataFetchError as DataFetchError,
)
from pulseengine.core.errors import (
    PipelineError as PipelineError,
)
from pulseengine.core.errors import (
    SignalComputationError as SignalComputationError,
)
from pulseengine.core.errors import (
    StorageError as StorageError,
)
from pulseengine.core.errors import (
    build_error_payload as build_error_payload,
)

__all__ = [
    "DataFetchError",
    "PipelineError",
    "SignalComputationError",
    "StorageError",
    "build_error_payload",
]
