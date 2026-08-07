"""
app/analysis.py — Backward-compatible re-export shim.

All domain logic now lives in pulseengine.core/. This file re-exports every name
for backward compatibility with existing code (dashboard.py, scan.py, tests).

New code should import directly from pulseengine.core.
"""

import logging

# ── Re-exports from pulseengine.core ──────────────────────────────────────────
# Names are listed alphabetically. For the grouping by domain (price, sentiment,
# news, signals, context, explanation), see pulseengine/core/__init__.py.
from pulseengine.core import (  # noqa:F401
    FINANCE_LEXICON,
    STORAGE_AVAILABLE,
    VADER_AVAILABLE,
    DataFetchError,
    PipelineError,
    SignalComputationError,
    StorageError,
    analyse_asset,
    analyse_market_context,
    build_explanation,
    classify_trend,
    cluster_articles,
    compute_momentum_metrics,
    compute_price_metrics,
    compute_roc,
    compute_rsi,
    compute_signal_score,
    correlate_news,
    deduplicate_articles,
    detect_events,
    fetch_all_metrics_parallel,
    fetch_news_articles,
    fetch_price_history,
    find_category,
    generate_keywords,
    get_display_clusters,
    run_full_scan,
    score_sentiment,
)

# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    )
    from pulseengine.core import TRACKED_ASSETS

    print("=" * 60)
    print("  PulseEngine — CLI Test")
    print("=" * 60)
    print(f"VADER available:   {VADER_AVAILABLE}")
    print(f"Storage available: {STORAGE_AVAILABLE}")

    _articles = fetch_news_articles()
    print(f"Fetched {len(_articles)} articles\n")

    first_cat   = list(TRACKED_ASSETS.keys())[0]
    first_asset = list(TRACKED_ASSETS[first_cat].keys())[0]
    first_tick  = TRACKED_ASSETS[first_cat][first_asset]

    result = analyse_asset(
        first_asset, first_tick, first_cat, _articles, with_market_ctx=False
    )
    print(result["explanation"]["verdict"])
    print()
    print(f"Signal: {result['signal']['label']} ({result['signal']['score']:+.1f})")
    print()
    print(f"Why it matters: {result['explanation']['why_it_matters']}")
    print()
    print(result["explanation"]["detail"][:800])
