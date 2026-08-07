"""
config/settings.py — Backward-compatible re-export shim.

All configuration now lives in pulseengine.core/config.py.
New code should import directly from pulseengine.core.
"""

from pulseengine.core.config import *  # noqa: F403
