"""
src/context.py — Backward-compatible re-export shim.

All logic now lives in pulseengine.core.context.
New code should import directly from pulseengine.core.
"""

from __future__ import annotations

from pulseengine.core.context import *  # noqa: F403
