"""Backward-compat shim. Real code lives in the pulseengine/local/components/ package."""
from pulseengine.local.components import *  # noqa: F403

# Re-exported deliberately: without it this shim has no declared export contract,
# so `from dashboard.components import *` would leak any future non-underscore
# name bound here rather than exporting exactly the documented set.
from pulseengine.local.components import __all__  # noqa: F401
