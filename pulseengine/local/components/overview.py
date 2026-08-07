"""Market-wide views: the 24h change heatmap and the category overview table."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from pulseengine.core import TRACKED_ASSETS


def render_heatmap(summary: dict, summary_date: str) -> None:
    """Render the Market Heatmap — 24h Changes plotly figure."""
    heatmap_data     = summary.get("heatmap", {})
    cats_for_heatmap = heatmap_data.get("categories", list(TRACKED_ASSETS.keys()))
    max_assets       = heatmap_data.get("max_assets", 1)
    z_matrix         = heatmap_data.get("z", [])
    text_matrix      = heatmap_data.get("text", [])

    hm_fig = go.Figure(go.Heatmap(
        z=z_matrix,
        x=[f"#{i+1}" for i in range(max_assets)],
        y=cats_for_heatmap,
        text=text_matrix,
        texttemplate="%{text}",
        colorscale=[
            [0.0, "#3d1010"],
            [0.2, "#7a3a3a"],
            [0.4, "#a06060"],
            [0.5, "#1a1510"],
            [0.6, "#4a6e50"],
            [0.8, "#4a7a52"],
            [1.0, "#5a9a62"],
        ],
        zmid=0, zmin=-5, zmax=5,
        showscale=True,
        colorbar={
            "title": {"text": "24h %", "font": {"color": "#635a48", "family": "Georgia, serif"}},
            "tickfont": {"color": "#635a48", "family": "Georgia, serif"},
            "thickness": 12,
        },
        xgap=3, ygap=3,
        hovertemplate="%{text}<extra></extra>",
    ))
    hm_fig.update_layout(
        height=220,
        margin={"l": 120, "r": 80, "t": 10, "b": 10},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis={"showticklabels": False, "showgrid": False},
        yaxis={"color": "#9e9078", "showgrid": False},
        font={"size": 10, "color": "#9e9078", "family": "Georgia, 'Times New Roman', serif"},
    )
    st.plotly_chart(hm_fig, config={"responsive": True})

    caption = "Clipped at ±5%. Cells with no data show 0%."
    if summary_date:
        caption += f"  ·  Data from scan: {summary_date}"
    st.caption(caption)


def render_category_overview(cat_data: dict, summary_date: str) -> None:
    """Render the styled category overview dataframe (content inside the expander)."""
    rows          = cat_data.get("rows", [])
    missing_names = cat_data.get("missing", [])

    if not rows:
        st.info("No scan data for this category. Run a full scan first.")
        return

    df = pd.DataFrame(rows)

    def _color_pct(val: object) -> str:
        if isinstance(val, (int, float)):
            if val > 0:
                return "color: #7db888"
            if val < 0:
                return "color: #c08080"
        return ""

    def _color_rsi(val: object) -> str:
        if isinstance(val, (int, float)):
            if val > 70:
                return "color: #c08080"
            if val < 30:
                return "color: #7db888"
        return ""

    styled = (
        df.style
        .format({
            "Price":   "${:,.2f}",
            "24h %":   "{:+.2f}%",
            "7d %":    "{:+.2f}%",
            "RSI":     "{:.1f}",
            "10d ROC": "{:+.2f}%",
        })
        .map(_color_pct, subset=["24h %", "7d %", "10d ROC"])
        .map(_color_rsi, subset=["RSI"])
    )
    st.dataframe(styled, width="stretch", hide_index=True)

    if missing_names:
        st.caption(
            f"No snapshot data for: {', '.join(missing_names)}. "
            "Run a full scan to populate."
        )
    elif summary_date:
        st.caption(f"Data from scan: {summary_date}.")
