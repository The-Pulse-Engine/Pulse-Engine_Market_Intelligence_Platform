"""Backward-compat shim. Real code lives in pulseengine/local/scan.py."""
from pulseengine.local.scan import *  # noqa: F403
from pulseengine.local.scan import load_last_scan_summary, run_scan  # noqa: F401

if __name__ == "__main__":
    from pulseengine.local.scan import main
    main()
