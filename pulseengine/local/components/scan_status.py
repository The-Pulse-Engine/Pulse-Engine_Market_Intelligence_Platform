"""Scan state presentation — how fresh the data is, wherever it is shown.

Grouped by responsibility rather than by Streamlit location: the sidebar status
line and the main-panel banner both answer "what is the state of the scan?".
"""

from __future__ import annotations

import datetime as dt

import streamlit as st

from pulseengine.core.config import SCAN_INTERVAL_MINUTES


def _format_scan_label(scan_state: dict, summary: dict) -> tuple[str, str]:
    """Return (human-readable label, CSS colour) for the scan status line."""
    if scan_state["running"]:
        return "⏳ Scan running...", "#a07840"

    ts = summary.get("scan_time")
    if not ts:
        return "No scan data yet", "#635a48"

    try:
        last_dt = dt.datetime.fromisoformat(ts)
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=dt.UTC)
        age_sec = int((dt.datetime.now(dt.UTC) - last_dt).total_seconds())
        age_min = max(age_sec // 60, 0)
    except (ValueError, TypeError):
        return "No scan data yet", "#635a48"

    if age_min < 1:
        ago = "just now"
    elif age_min < 60:
        ago = f"{age_min} min ago"
    else:
        h, m = divmod(age_min, 60)
        ago = f"{h}h {m}m ago" if m else f"{h}h ago"

    next_min = SCAN_INTERVAL_MINUTES - age_min
    next_str = "overdue" if next_min <= 0 else f"~{next_min} min"
    label = f"✅ Last scanned {ago}  ·  next scan in {next_str}"
    color = "#8a7040" if age_min < SCAN_INTERVAL_MINUTES else "#635a48"
    return label, color


def render_scan_status_sidebar(scan_state: dict, summary: dict) -> None:
    """Render the scan age label plus assets-done / error captions in the sidebar."""
    label, color = _format_scan_label(scan_state, summary)
    st.sidebar.markdown(
        f'<span style="font-size:0.80rem;color:{color};font-style:italic">{label}</span>',
        unsafe_allow_html=True,
    )
    if scan_state.get("assets_done"):
        st.sidebar.caption(f"{scan_state['assets_done']} assets in last scan")
    error_count = scan_state.get("errors_count", 0) or len(summary.get("errors", []))
    if error_count:
        st.sidebar.caption(f"{error_count} asset(s) reported scan errors")
    if scan_state.get("error"):
        st.sidebar.caption(f"Scan error: {scan_state['error'][:80]}")


def render_data_status_banner(scan_state: dict, stale: bool, summary: dict) -> None:
    """Show scan-running info, stale-data warning, and last-updated caption."""
    if scan_state["running"]:
        st.info("Updating market data in background — snapshot data shown below.", icon="🔄")
    elif stale:
        st.warning(
            "Market data may be outdated. A background refresh has been triggered. "
            "Use **Refresh Data** in the sidebar to reload immediately.",
            icon="⚠️",
        )

    scan_time = summary.get("scan_time", "")
    if scan_time:
        try:
            last_dt = dt.datetime.fromisoformat(scan_time)
            tz_label = " UTC" if last_dt.tzinfo is not None else ""
            st.caption(f"Market data last updated: {last_dt.strftime('%Y-%m-%d %H:%M')}{tz_label}")
        except (ValueError, TypeError):
            pass
