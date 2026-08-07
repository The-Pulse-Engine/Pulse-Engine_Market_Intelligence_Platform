"""
components — Reusable UI rendering functions for the PulseEngine local dashboard.

Each function takes pre-computed data as arguments and issues Streamlit calls.
No heavy computation, no network calls, no caching here — that belongs in
scan.py / data.py respectively.

This was a single 890-line module covering seven unrelated concerns (its own
section comments ran "Section 5" straight to "Section 13"). It is now split by
responsibility:

    sidebar      logo header, signal legend, top-mover rows
    scan_status  how fresh the data is — sidebar line and main-panel banner
    snapshot     single-asset signal card, why-box, metric cards
    news         article cards and the clustered news section
    analysis     price/volume charts, signal breakdown, backtest, history
    overview     market-wide heatmap and category table

Both consumers of the old module keep working unchanged:
    pulseengine/local/dashboard.py  ->  import pulseengine.local.components as ui
    dashboard/components.py         ->  from pulseengine.local.components import *

__all__ is the compatibility contract for the second one and is asserted
name-by-name in tests/test_legacy_interface.py. Adding a public renderer means
adding it here deliberately.
"""

from __future__ import annotations

from .analysis import render_live_analysis
from .news import render_article, render_news_section
from .overview import render_category_overview, render_heatmap
from .scan_status import render_data_status_banner, render_scan_status_sidebar
from .sidebar import render_mover_rows, render_signal_legend_sidebar, sidebar_header_html
from .snapshot import render_signal_card, render_snapshot_metrics, render_why_box

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
