"""News rendering: individual article cards and the clustered news section."""

from __future__ import annotations

import html as _html
from urllib.parse import urlparse

import streamlit as st

from pulseengine.core import RELEVANCE_HIGH, RELEVANCE_MEDIUM


def render_article(item: dict) -> None:
    """Render a single news article as a styled card."""
    sent       = item.get("sentiment", {}).get("compound", 0.0)
    sent_word  = "Positive" if sent > 0.05 else "Negative" if sent < -0.05 else "Neutral"
    sent_color = "#7db888" if sent > 0.05 else "#c08080" if sent < -0.05 else "#635a48"

    rel = item.get("relevance_score", 0)
    rel_html = (
        '<span class="rel-high">HIGH</span>'  if rel >= RELEVANCE_HIGH
        else '<span class="rel-med">MED</span>'  if rel >= RELEVANCE_MEDIUM
        else '<span class="rel-low">LOW</span>'
    )

    pub   = ""
    if item.get("published"):
        pub = item["published"].strftime("%b %d, %H:%M")

    events_html = ""
    if item.get("events_detected"):
        tags = " · ".join(
            f'{e.get("icon", "")} {e.get("label", "")}'.strip()
            for e in item["events_detected"]
        )
        events_html = f'<br><span style="font-size:0.80rem;color:#635a48">{tags}</span>'

    raw_summary = item.get("summary", "") if isinstance(item.get("summary"), str) else ""
    summary     = _html.escape(raw_summary[:220])
    if len(raw_summary) > 220:
        summary += " ..."

    # Validate link — only http/https allowed; anything else (javascript:, data:, etc.) is dropped
    raw_link = item.get("link", "")
    try:
        _parsed_link = urlparse(raw_link)
        safe_link = (
            _html.escape(raw_link, quote=True)
            if _parsed_link.scheme in ("http", "https")
            else "#"
        )
    except ValueError:
        safe_link = "#"

    safe_title  = _html.escape(item.get("title", ""))
    safe_source = _html.escape(item.get("source", ""))

    st.markdown(
        f'<div class="news-row">'
        f'<strong style="color:#e4d9c4;font-family:var(--font-display)">{safe_title}</strong><br>'
        f'<span class="news-meta">'
        f'{safe_source} &middot; {pub} &middot; '
        f'<span style="color:{sent_color}">{sent_word} ({sent:+.2f})</span>'
        f' &middot; Relevance: {rel_html}'
        f'</span>'
        f'{events_html}'
        f'<br><span style="color:#9e9078;font-size:0.87rem;font-style:italic">{summary}</span>'
        f'<br><a href="{safe_link}" target="_blank" '
        f'style="color:#8a7040;font-size:0.82rem">Read full article →</a>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_news_section(
    clusters_data: list[dict],
    suppressed: int,
    total_news: int,
    news: list[dict],
) -> None:
    """Render clustered or flat news results (handles all three states)."""
    if not news:
        st.markdown("## Related News")
        st.info("No recent articles matched this asset. Try a different one.")
        return

    if clusters_data:
        cluster_count = len(clusters_data)
        st.markdown(
            f"## Related News — Top {cluster_count} Cluster{'s' if cluster_count > 1 else ''}"
            + (f" ({suppressed} low-relevance article(s) suppressed)" if suppressed > 0 else "")
        )

        for cluster in clusters_data:
            sent_color_c = (
                "#7db888" if cluster["avg_sentiment"] > 0.05
                else "#c08080" if cluster["avg_sentiment"] < -0.05
                else "#635a48"
            )
            st.markdown(
                f'<div class="cluster-card">'
                f'<div class="cluster-header-row">'
                f'<span class="cluster-title">{cluster["label"]}</span>'
                f'<span class="cluster-meta">'
                f'{cluster["count"]} article{"s" if cluster["count"] != 1 else ""}'
                f' &middot; sentiment: '
                f'<span style="color:{sent_color_c}">{cluster["sentiment_summary"]}</span>'
                f'</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            for art in cluster["articles"][:3]:
                render_article(art)

        shown_set = {id(a) for c in clusters_data for a in c["articles"][:3]}
        remaining = [a for a in news if id(a) not in shown_set]
        if remaining:
            with st.expander(f"More articles ({len(remaining)} remaining)"):
                for art in remaining[:10]:
                    render_article(art)
    else:
        st.markdown(f"## Related News ({total_news} articles)")
        for article in news[:10]:
            render_article(article)
