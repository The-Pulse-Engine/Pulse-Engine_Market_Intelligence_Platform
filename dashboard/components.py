"""
dashboard/components.py — Backward-compatible re-export shim.

All logic now lives in the pulseengine.local.components package.
New code should import directly from there.

Names are re-exported explicitly with `as` aliases rather than `import *`:
that is the form both mypy and IDE inspectors recognise as a deliberate
re-export, so the shim no longer reads as a file full of unused imports.

This list is the documented compatibility contract and is asserted
name-by-name against pulseengine.local.components.__all__ in
tests/test_legacy_interface.py.
"""

from __future__ import annotations

from pulseengine.local.components import (
    render_article as render_article,
)
from pulseengine.local.components import (
    render_category_overview as render_category_overview,
)
from pulseengine.local.components import (
    render_data_status_banner as render_data_status_banner,
)
from pulseengine.local.components import (
    render_heatmap as render_heatmap,
)
from pulseengine.local.components import (
    render_live_analysis as render_live_analysis,
)
from pulseengine.local.components import (
    render_mover_rows as render_mover_rows,
)
from pulseengine.local.components import (
    render_news_section as render_news_section,
)
from pulseengine.local.components import (
    render_scan_status_sidebar as render_scan_status_sidebar,
)
from pulseengine.local.components import (
    render_signal_card as render_signal_card,
)
from pulseengine.local.components import (
    render_signal_legend_sidebar as render_signal_legend_sidebar,
)
from pulseengine.local.components import (
    render_snapshot_metrics as render_snapshot_metrics,
)
from pulseengine.local.components import (
    render_why_box as render_why_box,
)
from pulseengine.local.components import (
    sidebar_header_html as sidebar_header_html,
)

__all__ = [
    "render_article",
    "render_category_overview",
    "render_data_status_banner",
    "render_heatmap",
    "render_live_analysis",
    "render_mover_rows",
    "render_news_section",
    "render_scan_status_sidebar",
    "render_signal_card",
    "render_signal_legend_sidebar",
    "render_snapshot_metrics",
    "render_why_box",
    "sidebar_header_html",
]
