"""Backward-compat shim. Real code lives in the pulseengine/local/components/ package."""
import pulseengine.local.components as _canonical
from pulseengine.local.components import *  # noqa: F403

# Mirrored deliberately: without its own __all__ this shim has no declared export
# contract, so `from dashboard.components import *` would leak any future
# non-underscore name bound here instead of exactly the documented set.
__all__ = list(_canonical.__all__)
