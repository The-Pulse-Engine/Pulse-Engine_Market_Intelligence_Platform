"""Restricted stateless Streamlit demo for PulseEngine."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from pulseengine.core import (
    DASHBOARD_ICON,
    DASHBOARD_LAYOUT,
    DASHBOARD_TITLE,
    DEFAULT_CATEGORY,
    TRACKED_ASSETS,
    DataFetchError,
    analyse_market_context,
    build_explanation,
    cluster_articles,
    compute_momentum_metrics,
    compute_price_metrics,
    compute_signal_score,
    correlate_news,
    fetch_all_metrics_parallel,
    fetch_news_articles,
    fetch_price_history,
)

_LOCKED_FEATURES: tuple[tuple[str, str], ...] = (
    ("Arbitrary ticker lookup", "The web demo only shows the 24 tracked assets."),
    ("Backtesting", "Historical evaluation stays local because it is compute heavy."),
    ("Historical snapshots", "Snapshots are written only by the local app."),
    ("Export to CSV / PDF", "Exports are a local-app feature and never run in the demo."),
    ("FinBERT local model", "No local model downloads or inference run in the web build."),
    ("Custom RSS feeds", "User-defined feeds are intentionally local-only."),
    ("Offline mode", "Offline caching and replay stay on the local surface."),
)


st.set_page_config(
    page_title=f"{DASHBOARD_TITLE} | Web Demo",
    page_icon=DASHBOARD_ICON,
    layout=DASHBOARD_LAYOUT,  # type: ignore[arg-type]
)

st.title("PulseEngine Web Demo")
st.caption(
    "A lightweight live preview of the shared engine. Locked features stay local-only."
)

st.info(
    "This demo is stateless and write-free: no snapshot storage, no backtesting, no local model "
    "inference, and no arbitrary ticker lookup. We store nothing. Ever. Download the local app "
    "for the full experience."
)


def _format_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.2f}%"


def _build_live_analysis(asset_name: str, ticker: str, category: str) -> dict:
    """Build a live, read-only analysis for the selected asset."""
    try:
        history = fetch_price_history(ticker)
    except DataFetchError as exc:
        return {"error": str(exc), "history": None, "metrics": {}, "momentum": {}}

    if history is None or history.empty:
        return {
            "error": f"No price history available for {asset_name}.",
            "history": history,
            "metrics": {},
            "momentum": {},
            "news": [],
            "clusters": {},
            "market_ctx": None,
            "signal": {"score": 0.0, "label": "No Data"},
            "explanation": {"verdict": "No price data available."},
        }

    metrics = compute_price_metrics(history)
    momentum = compute_momentum_metrics(history)
    try:
        articles = fetch_news_articles()
    except DataFetchError:
        articles = []
    news = correlate_news(asset_name, articles)
    clusters = cluster_articles(news)
    market_ctx = None
    if metrics.get("change_1d") is not None:
        market_ctx = analyse_market_context(asset_name, category, metrics.get("change_1d"))
    signal = compute_signal_score(metrics, momentum, news, market_ctx, category=category)
    explanation = build_explanation(
        asset_name,
        metrics,
        news,
        market_ctx=market_ctx,
        momentum=momentum,
        signal=signal,
    )
    return {
        "error": None,
        "history": history,
        "metrics": metrics,
        "momentum": momentum,
        "news": news,
        "clusters": clusters,
        "market_ctx": market_ctx,
        "signal": signal,
        "explanation": explanation,
    }


def _render_locked_features() -> None:
    st.subheader("Download the local app to unlock")
    st.caption("These capabilities are intentionally disabled in the web demo.")
    for feature, reason in _LOCKED_FEATURES:
        st.markdown(f"**{feature}**")
        st.info(f"{reason} Download the local app to unlock this feature.", icon="🔒")
    st.code("streamlit run pulseengine/local/dashboard.py", language="bash")


st.sidebar.header("Demo controls")
categories = list(TRACKED_ASSETS.keys())
default_index = categories.index(DEFAULT_CATEGORY) if DEFAULT_CATEGORY in categories else 0
selected_category = st.sidebar.selectbox("Category", categories, index=default_index)
asset_names = list(TRACKED_ASSETS[selected_category].keys())
selected_asset = st.sidebar.selectbox("Asset", asset_names)
_ticker = TRACKED_ASSETS[selected_category][selected_asset]

selected = _build_live_analysis(selected_asset, _ticker, selected_category)

if selected.get("error"):
    st.warning(selected["error"])
else:
    _metrics = selected["metrics"]
    _momentum = selected["momentum"]
    _signal = selected["signal"]
    _explanation = selected["explanation"]
    _history = selected["history"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Signal", _signal.get("label", "n/a"), f"{_signal.get('score', 0.0):+.1f}")
    c2.metric(
        "Price",
        f"${_metrics.get('latest_price', 0.0):,.2f}",
        _format_pct(_metrics.get("change_1d")),
    )
    c3.metric("RSI", f"{_momentum.get('rsi', 0.0):.1f}")
    c4.metric("ROC 10d", _format_pct(_momentum.get("roc_10d")))

    st.subheader("Why it matters")
    st.write(_explanation.get("why_it_matters") or _explanation.get("verdict", ""))

    if _history is not None and not _history.empty and "Close" in _history.columns:
        st.subheader("Price chart")
        st.line_chart(_history["Close"])

    st.subheader("News sentiment")
    if selected["news"]:
        for article in selected["news"][:5]:
            sent = article.get("sentiment", {}).get("compound", 0.0)
            st.markdown(f"- **{article.get('title', 'Untitled')}** ({_format_pct(sent * 100)})")
    else:
        st.caption("No relevant articles matched this asset.")

    st.subheader("Current market context")
    _market_ctx = selected.get("market_ctx") or {}
    context_cols = st.columns(3)
    context_cols[0].metric("Sector-wide", str(bool(_market_ctx.get("is_sector_wide"))))
    context_cols[1].metric("Market-wide", str(bool(_market_ctx.get("is_market_wide"))))
    context_cols[2].metric("Asset-specific", str(bool(_market_ctx.get("is_asset_specific"))))

    _render_locked_features()


st.divider()
st.subheader("Market heatmap and category overview")
st.caption("Computed on demand from live price data only. No state is written to disk.")

if st.button("Build market overview"):
    try:
        _overview = fetch_all_metrics_parallel(days=5)
    except DataFetchError as _exc:
        st.error(f"Could not build the market overview: {_exc}")
    else:
        rows: list[dict] = []
        asset_order = [asset for _category in TRACKED_ASSETS.values() for asset in _category]
        categories = list(TRACKED_ASSETS.keys())

        matrix: list[list[float | None]] = []
        labels: list[list[str]] = []
        for _category in categories:
            row_values: list[float | None] = []
            row_labels: list[str] = []
            for _asset_name in asset_order:
                _asset_map = TRACKED_ASSETS.get(_category, {})
                if _asset_name in _asset_map:
                    data = _overview.get(_category, {}).get(_asset_name, {})
                    _metrics = data.get("metrics", {})
                    _momentum = data.get("momentum", {})
                    rows.append(
                        {
                            "Category": _category,
                            "Asset": _asset_name,
                            "Ticker": _asset_map[_asset_name],
                            "Price": _metrics.get("latest_price"),
                            "Change 1d": _metrics.get("change_1d"),
                            "RSI": _momentum.get("rsi"),
                            "Trend": _metrics.get("trend"),
                        }
                    )
                    row_values.append(_metrics.get("change_1d"))
                    row_labels.append(f"{_asset_name}<br>{_format_pct(_metrics.get('change_1d'))}")
                else:
                    row_values.append(None)
                    row_labels.append("")
            matrix.append(row_values)
            labels.append(row_labels)

        fig = go.Figure(
            data=go.Heatmap(
                z=matrix,
                x=asset_order,
                y=categories,
                text=labels,
                colorscale="RdYlGn",
                zmid=0,
                hovertemplate="%{y} / %{x}<br>Change: %{z:+.2f}%<extra></extra>",
            )
        )
        fig.update_layout(height=380, margin={"l": 20, "r": 20, "t": 40, "b": 20})

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.caption("Click to load the full market overview.")
