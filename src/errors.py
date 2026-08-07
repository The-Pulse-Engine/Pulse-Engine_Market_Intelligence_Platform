"""
src/errors.py — Backward-compatible re-export shim.

All logic now lives in pulseengine.core.errors.
New code should import directly from pulseengine.core.
"""

from __future__ import annotations

from pulseengine.core.errors import *  # noqa: F403
