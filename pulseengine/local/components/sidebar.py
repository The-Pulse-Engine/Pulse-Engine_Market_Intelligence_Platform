"""Sidebar chrome: logo header, signal legend, and top-mover rows."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from pulseengine.core import DASHBOARD_ICON


def _build_logo_html() -> str:
    logo_path = Path(__file__).resolve().parents[3] / "assets" / "logo" / "pulseengine_logo.png"
    if logo_path.exists():
        data = base64.b64encode(logo_path.read_bytes()).decode()
        return (
            f'<img src="data:image/png;base64,{data}" '
            f'style="width:100%;max-width:190px;display:block;'
            f'margin:0 auto 4px auto;opacity:0.93;" />'
        )
    return f"<span style='font-size:1.4rem'>{DASHBOARD_ICON}</span>"


# Logo HTML is static for the lifetime of the process — build it once at import
# time so the PNG is not read and base64-encoded on every Streamlit rerun.
_LOGO_HTML: str = _build_logo_html()


def sidebar_header_html() -> str:
    """Return the full sidebar header HTML (logo + subtitle)."""
    return f"""
    <div style="text-align:center;padding:10px 0 6px 0;">
      {_LOGO_HTML}
      <div style="
        font-family:'EB Garamond','Georgia',serif;
        font-size:0.66rem;
        font-weight:400;
        letter-spacing:0.22em;
        text-transform:uppercase;
        color:#8a7650;
        margin-top:4px;
      ">Market Intelligence Platform</div>
    </div>
    """


def render_signal_legend_sidebar() -> None:
    """Render a compact signal interpretation legend in the sidebar."""
    with st.sidebar.expander("Signal Interpretation", expanded=False):
        st.markdown(
            "- **+6 to +10** — Strong Bullish\n"
            "- **+3 to +6** — Bullish\n"
            "- **+1 to +3** — Slightly Bullish\n"
            "- **-1 to +1** — Neutral\n"
            "- **-3 to -1** — Slightly Bearish\n"
            "- **-6 to -3** — Bearish\n"
            "- **-10 to -6** — Strong Bearish"
        )
        st.caption("Scores are weighted composite signals, not raw price change.")


def render_mover_rows(gainers: list[dict], losers: list[dict], summary_date: str) -> None:
    """Render the Top Movers gainers/losers lists in the sidebar."""
    if not gainers and not losers:
        st.caption("No scan data yet — run a full scan to see top movers.")
        return

    def _mover_html(items: list[dict], color: str) -> str:
        return "".join(
            f'<div class="mover-row">'
            f'<span style="color:#9e9078">{m["name"]}</span>'
            f'<span style="color:{color};font-weight:600">{m["chg"]:+.2f}%</span>'
            f'</div>'
            for m in items
        )

    if gainers:
        st.markdown(
            '<div style="margin-bottom:6px;font-size:0.72rem;color:#8a7040;'
            'font-weight:600;letter-spacing:0.10em;text-transform:uppercase;font-style:italic">Gainers</div>'
            + _mover_html(gainers, "#7db888"),
            unsafe_allow_html=True,
        )
    if losers:
        st.markdown(
            '<div style="margin-top:10px;margin-bottom:6px;font-size:0.72rem;'
            'color:#7a3a3a;font-weight:600;letter-spacing:0.10em;text-transform:uppercase;font-style:italic">Losers</div>'
            + _mover_html(losers, "#c08080"),
            unsafe_allow_html=True,
        )
    if summary_date:
        st.caption(f"From scan: {summary_date}")
