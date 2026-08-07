"""Single-asset snapshot presentation: signal card, why-box, metric cards.

All three render from the `snap` dict produced by a scan.
"""

from __future__ import annotations

import html as _html

import streamlit as st

_SIGNAL_CLASS_MAP: dict[str, str] = {
    "Strong Bullish":   "signal-strong-bull",
    "Bullish":          "signal-bull",
    "Slightly Bullish": "signal-slight-bull",
    "Neutral":          "signal-neutral",
    "Slightly Bearish": "signal-slight-bear",
    "Bearish":          "signal-bear",
    "Strong Bearish":   "signal-strong-bear",
}


def render_signal_card(
    snap: dict,
    selected_category: str,
    selected_asset: str,
    chg_1d: float | None,
    is_significant: bool,
) -> None:
    """Render the signal card (and significant-move warning if applicable)."""
    sig_score  = float(snap.get("signal_score") or 0.0)
    sig_label  = snap.get("signal_label") or "Neutral"
    low_news_conf = bool(snap.get("low_news_confidence", False))
    news_count = int(snap.get("news_article_count", 0) or 0)
    conf       = snap.get("confidence") or "low"
    conf_class = {"high": "conf-high", "medium": "conf-medium"}.get(conf, "conf-low")
    conf_label = conf.upper()
    sig_css    = _SIGNAL_CLASS_MAP.get(sig_label, "signal-neutral")

    sig_col, _spacer = st.columns([2, 3])
    with sig_col:
        if snap:
            st.markdown(
                f'<div class="signal-card {sig_css}">'
                f'<div class="signal-label-text">{sig_label}'
                f'<span class="confidence-badge {conf_class}">Confidence: {conf_label}</span>'
                f'</div>'
                f'<div class="signal-score-text">Score: {sig_score:+.1f} / 10'
                f'&nbsp;&nbsp;&middot;&nbsp;&nbsp;'
                f'<span style="font-size:0.9rem;opacity:0.7">{selected_category}</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("No snapshot data yet — run a full scan from the sidebar.")

    if low_news_conf:
        st.warning(
            "Low news coverage — this signal is based primarily on price data. "
            "Sentiment component has low confidence.",
            icon="⚠️",
        )
        st.caption(f"Matched relevant articles: {news_count}")

    if is_significant and chg_1d is not None:
        verb = "surged" if chg_1d > 0 else "dropped"
        st.warning(
            f"Significant move: {selected_asset} {verb} {abs(chg_1d):.2f}% in 24 hours."
        )


def render_why_box(snap: dict) -> None:
    """Render the 'Why it matters' verdict box if the snapshot has one."""
    verdict = snap.get("verdict", "")
    if verdict:
        st.markdown(
            f'<div class="why-box">'
            f'<div class="why-label">Why it matters</div>'
            f'{_html.escape(verdict)}'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_snapshot_metrics(snap: dict, chg_1d: float | None) -> None:
    """Render the 5-column price metrics and 4-column momentum row from the snapshot."""
    if not snap:
        st.info("Run a full scan to populate metric data.")
        return

    price = snap.get("price") or 0
    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    with mc1:
        st.metric(
            "Price",
            f"${price:,.2f}",
            delta=(f"{chg_1d:+.2f}% (24h)" if chg_1d is not None else None),
        )
    with mc2:
        v7 = snap.get("change_7d")
        st.metric("7-Day", f"{v7:+.2f}%" if v7 is not None else "N/A")
    with mc3:
        v30 = snap.get("change_30d")
        st.metric("30-Day", f"{v30:+.2f}%" if v30 is not None else "N/A")
    with mc4:
        vol = snap.get("volatility")
        st.metric("Volatility", f"{vol:.2f}%" if vol is not None else "N/A")
    with mc5:
        trend = snap.get("trend") or "sideways"
        st.metric("Trend", trend.title())

    m1, m2, m3, m4 = st.columns(4)
    rsi = float(snap.get("rsi") or 50.0)
    roc = float(snap.get("roc_10d") or 0.0)
    with m1:
        rsi_delta = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else None
        st.metric("RSI (14-day)", f"{rsi:.1f}", delta=rsi_delta)
    with m2:
        st.metric("10-day ROC", f"{roc:+.2f}%")
    with m3:
        ts = snap.get("trend_strength")
        st.metric("Trend Strength", f"{ts:+.2f}%" if ts is not None else "N/A",
                  help="MA7 vs MA30 divergence")
    with m4:
        ma = snap.get("momentum_accel")
        st.metric("Momentum Accel", f"{ma:+.2f}%" if ma is not None else "N/A",
                  help="Recent 5d ROC minus prior 5d ROC")
