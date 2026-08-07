"""Live analysis: price/volume charts, signal breakdown, backtest, history."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from pulseengine.core.config import BACKTEST_WINDOW, CHART_HEIGHT, SNAPSHOT_LOAD_LIMIT

# ── Optional dependencies ──────────────────────────────────────────────────────

# The fallbacks mirror the real signatures exactly. A catch-all (*_a, **_kw)
# would accept calls the real functions reject, so a bad call site would work
# only on machines where the optional import failed.
#
# The parameters are therefore unused on purpose: the signature IS the contract.
try:
    from pulseengine.core import evaluate_signal_accuracy, get_signal_streak
    _BACKTEST_AVAILABLE = True
except ImportError:
    _BACKTEST_AVAILABLE = False

    def evaluate_signal_accuracy(asset_name: str, lookback: int = BACKTEST_WINDOW) -> dict:
        _ = asset_name, lookback
        return {}

    def get_signal_streak(details: list[dict]) -> dict:
        _ = details
        return {"type": "none", "length": 0}

try:
    from pulseengine.core import get_historical_features
    _STORAGE_AVAILABLE = True
except ImportError:
    _STORAGE_AVAILABLE = False

    def get_historical_features(
        asset_name: str,
        limit: int = SNAPSHOT_LOAD_LIMIT,
        strict: bool = False,
    ) -> dict:
        _ = asset_name, limit, strict
        return {}


_WARN_FACTOR_TYPES = {"rsi_overbought", "rsi_oversold", "sentiment_diverged", "volatility"}


def _render_primary_driver(primary_driver: dict) -> None:
    st.markdown(
        f'<div class="driver-box">'
        f'<div class="driver-label">Primary driver</div>'
        f'<strong>{primary_driver["label"]}</strong>'
        + (f' — {primary_driver["detail"]}' if primary_driver.get("detail") else "")
            + '</div>',
        unsafe_allow_html=True,
    )


def _render_factor_pills(live_factors: list[dict]) -> None:
    pills_html = "".join(
        f'<span class="factor-pill'
        f'{" factor-pill-warn" if f["type"] in _WARN_FACTOR_TYPES else ""}">'
        f'{f["label"]}</span>'
        for f in live_factors
    )
    st.markdown(f"**Contributing factors:** {pills_html}", unsafe_allow_html=True)


def _render_contradictions(contradictions: list[dict]) -> None:
    with st.expander(f"Risks and contradictions ({len(contradictions)})"):
        for c in contradictions:
            st.markdown(
                f'<div class="contra-box">'
                f'<strong>{c["type"].replace("_", " ").title()}:</strong> '
                f'{c["description"]}'
                f'</div>',
                unsafe_allow_html=True,
            )


def _render_confidence_reasoning(conf_info: dict) -> None:
    with st.expander("Confidence reasoning"):
        if conf_info.get("increases"):
            st.markdown("**Increases confidence:**")
            for r in conf_info["increases"]:
                st.markdown(f"- {r}")
        if conf_info.get("decreases"):
            st.markdown("**Decreases confidence:**")
            for r in conf_info["decreases"]:
                st.markdown(f"- {r}")
        st.caption(f"Confidence score: {conf_info.get('score', 0)} / 12")


def _render_price_chart(history: pd.DataFrame) -> None:
    """Render the 30-day close price chart with optional MA overlays."""
    st.markdown("### Price History")
    close_col = history["Close"]
    if isinstance(close_col, pd.DataFrame):
        close_col = close_col.iloc[:, 0]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history.index, y=close_col,
        mode="lines",
        line={"color": "#c4a35a", "width": 2.0},
        fill="tozeroy",
        fillcolor="rgba(196,163,90,0.06)",
        name="Close",
        hovertemplate="$%{y:,.4f}<br>%{x|%b %d}<extra></extra>",
    ))

    if len(close_col) >= 7:
        fig.add_trace(go.Scatter(
            x=history.index, y=close_col.rolling(7).mean(),
            mode="lines",
            line={"color": "#8a7040", "width": 1.4, "dash": "dash"},
            name="7d MA",
            hovertemplate="MA7: $%{y:,.4f}<extra></extra>",
        ))

    if len(close_col) >= 20:
        fig.add_trace(go.Scatter(
            x=history.index, y=close_col.rolling(20).mean(),
            mode="lines",
            line={"color": "#5a5040", "width": 1.2, "dash": "dot"},
            name="20d MA",
            hovertemplate="MA20: $%{y:,.4f}<extra></extra>",
        ))

    fig.update_layout(
        height=CHART_HEIGHT,
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis={"showgrid": False, "color": "#635a48", "tickformat": "%b %d"},
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(82,72,64,0.2)",
            "color": "#635a48",
            "tickprefix": "$",
        },
        legend={
            "orientation": "h", "yanchor": "bottom", "y": 1.02,
            "xanchor": "right", "x": 1, "font": {"size": 11, "color": "#9e9078"},
        },
        hovermode="x unified",
        font={"family": "Georgia, 'Times New Roman', serif"},
    )
    st.plotly_chart(fig, config={"responsive": True})


def _render_volume_chart(history: pd.DataFrame) -> None:
    with st.expander("Volume chart"):
        if "Volume" not in history.columns:
            st.info("Volume data not available.")
            return
        vol_col = history["Volume"]
        if isinstance(vol_col, pd.DataFrame):
            vol_col = vol_col.iloc[:, 0]
        vfig = go.Figure(go.Bar(
            x=history.index, y=vol_col,
            marker={"color": "rgba(196,163,90,0.25)"},
            hovertemplate="%{y:,.0f}<extra></extra>",
        ))
        vfig.update_layout(
            height=200,
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis={"showgrid": False, "color": "#635a48"},
            yaxis={"showgrid": False, "color": "#635a48"},
            font={"family": "Georgia, 'Times New Roman', serif"},
        )
        st.plotly_chart(vfig, config={"responsive": True})


def _render_signal_components(live_signal: dict) -> None:
    with st.expander("Signal component breakdown"):
        comps = live_signal.get("components", {})
        if not comps:
            st.info("No component data available.")
            return
        comp_names  = list(comps.keys())
        comp_values = [comps[k] for k in comp_names]
        colors      = ["#4a7a52" if v >= 0 else "#7a3a3a" for v in comp_values]

        # Dynamic y-axis range so clipped bars are always fully visible.
        max_abs = max((abs(v) for v in comp_values), default=1.0)
        y_range = max(round(max_abs * 1.30 + 0.2, 1), 1.5)

        cfig = go.Figure(go.Bar(
            x=comp_names,
            y=comp_values,
            marker={"color": colors},
            text=[f"{v:+.2f}" for v in comp_values],
            textposition="outside",
        ))
        cfig.update_layout(
            height=220,
            margin={"l": 0, "r": 0, "t": 10, "b": 0},
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis={"color": "#635a48"},
            yaxis={
                "color": "#635a48",
                "showgrid": True,
                "gridcolor": "rgba(82,72,64,0.2)",
                "range": [-y_range, y_range],
            },
            font={"family": "Georgia, 'Times New Roman', serif", "color": "#9e9078"},
        )
        cfig.add_hline(y=0, line_color="#524840", line_width=1)
        st.plotly_chart(cfig, config={"responsive": True})
        if live_signal.get("category"):
            st.caption(
                f"Per-class weights applied for {live_signal['category']}. "
                "Weighted values shown. Each component contributes to the -10 to +10 signal."
            )
        else:
            st.caption("Each component contributes to the -10 to +10 composite signal score.")


def _render_backtest_section(selected_asset: str) -> None:
    """Render the backtest expander (no-op when backtest module is unavailable)."""
    if not _BACKTEST_AVAILABLE:
        return

    bt = evaluate_signal_accuracy(selected_asset)
    if bt["num_evaluated"] == 0:
        with st.expander("Signal Backtest (no history yet)"):
            st.info(
                bt["message"] + "\n\n"
                "Snapshots are saved each time this app runs. "
                "Return after a few days to see backtest results."
            )
        return

    st.markdown("### Signal Backtest")
    hit_rate = bt["hit_rate"]
    streak   = get_signal_streak(bt["details"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        pct = f"{hit_rate * 100:.1f}%" if hit_rate is not None else "N/A"
        st.metric("Directional Accuracy", pct)
    with c2:
        st.metric("Signals Evaluated", bt["num_evaluated"])
    with c3:
        avg_str = f"{bt['avg_signal_score']:+.2f}" if bt["avg_signal_score"] is not None else "N/A"
        st.metric("Avg Signal Score", avg_str)
    with c4:
        if streak["type"] != "none":
            st.metric("Current Streak", f"{streak['length']} {streak['type'].upper()}")

    st.caption(bt["message"])

    if bt.get("label_summaries"):
        with st.expander("Accuracy by signal label"):
            for s in bt["label_summaries"]:
                st.markdown(f"- {s}")

    bss = bt.get("by_signal_strength", {})
    if bss:
        with st.expander("Accuracy by signal strength"):
            for bucket in ("strong", "moderate", "weak"):
                if bucket in bss:
                    st.markdown(f"- {bss[bucket]['summary']}")

    if bt["details"]:
        with st.expander("Signal history (last 15)"):
            detail_rows = [
                {
                    "Date":      d["date"],
                    "Signal":    d["signal_label"],
                    "Score":     d["signal_score"],
                    "Predicted": d["predicted"],
                    "Actual":    f"{d['actual_change']:+.2f}% ({d['actual']})",
                    "Correct":   "Yes" if d["correct"] else "No",
                }
                for d in bt["details"][:15]
            ]
            bt_df     = pd.DataFrame(detail_rows)
            bt_styled = bt_df.style.map(
                lambda v: "color:#7db888" if v == "Yes" else "color:#c08080" if v == "No" else "",
                subset=["Correct"],
            )
            st.dataframe(bt_styled, width="stretch", hide_index=True)


def _render_historical_context(selected_asset: str, snap: dict) -> None:
    """Render the historical context expander (no-op when storage is unavailable)."""
    if not _STORAGE_AVAILABLE:
        return

    hist_feat = get_historical_features(selected_asset)
    if hist_feat.get("available", 0) < 2:
        return

    with st.expander("Historical context"):
        consistency: float | None = hist_feat.get("signal_consistency")
        persistence: float = hist_feat.get("trend_persistence", 0)
        t_vs_y: dict = hist_feat.get("today_vs_yesterday", {})

        hf_parts: list[str] = []
        if consistency is not None:
            hf_parts.append(
                f"Signal consistency over last {hist_feat['available']} snapshots: "
                f"**{consistency * 100:.0f}%** pointing same direction as today."
            )
        if persistence > 0:
            hf_parts.append(
                f"Trend **{snap.get('trend', 'unknown')}** has persisted "
                f"for **{persistence}** consecutive snapshot(s)."
            )
        if t_vs_y.get("signal_score"):
            d         = t_vs_y["signal_score"]
            direction = (
                "higher" if d["change"] > 0 else "lower" if d["change"] < 0 else "unchanged"
            )
            hf_parts.append(
                f"Signal score today ({d['today']:+.2f}) is **{direction}** "
                f"than yesterday ({d['yesterday']:+.2f}, change: {d['change']:+.2f})."
            )

        for part in hf_parts:
            st.markdown(part)

        st.caption(
            f"Based on {hist_feat['available']} stored snapshot(s). "
            "Snapshots accumulate as the app runs over multiple days."
        )


def render_live_analysis(
    history: pd.DataFrame,
    selected_asset: str,
    live_signal: dict,
    live_explanation: dict,
    snap: dict,
    is_significant: bool,
) -> None:
    """
    Render the full live-analysis block inside the Price Chart & Live Analysis
    expander: primary driver, factor pills, contradictions, confidence reasoning,
    price chart, volume chart, signal components, backtest, historical context,
    and full analysis text.
    """
    live_factors: list[dict] = live_explanation.get("factors", [])
    event_factors   = [f for f in live_factors if f["type"] == "event"]
    context_factors = [
        f for f in live_factors
        if f["type"] in ("market_wide", "sector_wide", "asset_specific")
    ]
    primary_driver = next(iter(event_factors or context_factors or live_factors), None)

    if primary_driver:
        _render_primary_driver(primary_driver)

    if live_factors:
        _render_factor_pills(live_factors)

    contradictions = live_explanation.get("contradictions", [])
    if contradictions:
        _render_contradictions(contradictions)

    conf_info = live_explanation.get("confidence_info", {})
    if conf_info.get("increases") or conf_info.get("decreases"):
        _render_confidence_reasoning(conf_info)

    _render_price_chart(history)
    _render_volume_chart(history)
    _render_signal_components(live_signal)
    _render_backtest_section(selected_asset)
    _render_historical_context(selected_asset, snap)

    live_score = abs(live_signal.get("score") or 0)
    with st.expander("Full Analysis", expanded=is_significant or live_score >= 3.0):
        st.markdown(live_explanation["detail"])
