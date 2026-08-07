"""
config/settings.py — Backward-compatible re-export shim.

All logic now lives in pulseengine.core.config.
New code should import directly from there.

Names are re-exported explicitly with `as` aliases rather than `import *`:
that is the form both mypy and IDE inspectors recognise as a deliberate
re-export, so the shim no longer reads as a file full of unused imports.
"""

from __future__ import annotations

from pulseengine.core.config import (
    ASSET_CLASS_WEIGHTS as ASSET_CLASS_WEIGHTS,
)
from pulseengine.core.config import (
    ASSET_KEYWORDS as ASSET_KEYWORDS,
)
from pulseengine.core.config import (
    BACKTEST_WINDOW as BACKTEST_WINDOW,
)
from pulseengine.core.config import (
    BASE_DIR as BASE_DIR,
)
from pulseengine.core.config import (
    CHART_HEIGHT as CHART_HEIGHT,
)
from pulseengine.core.config import (
    DASHBOARD_ICON as DASHBOARD_ICON,
)
from pulseengine.core.config import (
    DASHBOARD_LAYOUT as DASHBOARD_LAYOUT,
)
from pulseengine.core.config import (
    DASHBOARD_TITLE as DASHBOARD_TITLE,
)
from pulseengine.core.config import (
    DEDUP_SIMILARITY_THRESHOLD as DEDUP_SIMILARITY_THRESHOLD,
)
from pulseengine.core.config import (
    DEFAULT_CATEGORY as DEFAULT_CATEGORY,
)
from pulseengine.core.config import (
    EVENT_TRIGGERS as EVENT_TRIGGERS,
)
from pulseengine.core.config import (
    LOOKBACK_DAYS as LOOKBACK_DAYS,
)
from pulseengine.core.config import (
    LOW_NEWS_SENTIMENT_WEIGHT_MULTIPLIER as LOW_NEWS_SENTIMENT_WEIGHT_MULTIPLIER,
)
from pulseengine.core.config import (
    MARKET_BENCHMARK as MARKET_BENCHMARK,
)
from pulseengine.core.config import (
    MAX_RETRIES as MAX_RETRIES,
)
from pulseengine.core.config import (
    MAX_WORKERS as MAX_WORKERS,
)
from pulseengine.core.config import (
    MIN_NEWS_ARTICLES_FOR_CONFIDENCE as MIN_NEWS_ARTICLES_FOR_CONFIDENCE,
)
from pulseengine.core.config import (
    MOMENTUM_PERIOD as MOMENTUM_PERIOD,
)
from pulseengine.core.config import (
    NEWS_CACHE_TTL as NEWS_CACHE_TTL,
)
from pulseengine.core.config import (
    NEWS_FEEDS as NEWS_FEEDS,
)
from pulseengine.core.config import (
    NEWS_MAX_AGE_HOURS as NEWS_MAX_AGE_HOURS,
)
from pulseengine.core.config import (
    NEWS_MAX_ARTICLES as NEWS_MAX_ARTICLES,
)
from pulseengine.core.config import (
    PRICE_CACHE_TTL as PRICE_CACHE_TTL,
)
from pulseengine.core.config import (
    PRICE_CHANGE_THRESHOLD as PRICE_CHANGE_THRESHOLD,
)
from pulseengine.core.config import (
    PRICE_FETCH_WORKERS as PRICE_FETCH_WORKERS,
)
from pulseengine.core.config import (
    RELEVANCE_HIGH as RELEVANCE_HIGH,
)
from pulseengine.core.config import (
    RELEVANCE_MEDIUM as RELEVANCE_MEDIUM,
)
from pulseengine.core.config import (
    REQUEST_TIMEOUT as REQUEST_TIMEOUT,
)
from pulseengine.core.config import (
    RSI_PERIOD as RSI_PERIOD,
)
from pulseengine.core.config import (
    SCAN_INTERVAL_MINUTES as SCAN_INTERVAL_MINUTES,
)
from pulseengine.core.config import (
    SECTOR_PEERS as SECTOR_PEERS,
)
from pulseengine.core.config import (
    SIGNAL_THRESHOLDS as SIGNAL_THRESHOLDS,
)
from pulseengine.core.config import (
    SNAPSHOT_LOAD_LIMIT as SNAPSHOT_LOAD_LIMIT,
)
from pulseengine.core.config import (
    SOURCE_WEIGHTS as SOURCE_WEIGHTS,
)
from pulseengine.core.config import (
    STORAGE_DIR as STORAGE_DIR,
)
from pulseengine.core.config import (
    STORAGE_FULL_DETAIL_DAYS as STORAGE_FULL_DETAIL_DAYS,
)
from pulseengine.core.config import (
    STORAGE_MAX_DAYS as STORAGE_MAX_DAYS,
)
from pulseengine.core.config import (
    STORAGE_REDUCED_DETAIL_DAYS as STORAGE_REDUCED_DETAIL_DAYS,
)
from pulseengine.core.config import (
    TRACKED_ASSETS as TRACKED_ASSETS,
)
from pulseengine.core.config import (
    YFINANCE_BACKOFF_BASE as YFINANCE_BACKOFF_BASE,
)
from pulseengine.core.config import (
    YFINANCE_REQUEST_DELAY as YFINANCE_REQUEST_DELAY,
)

__all__ = [
    "ASSET_CLASS_WEIGHTS",
    "ASSET_KEYWORDS",
    "BACKTEST_WINDOW",
    "BASE_DIR",
    "CHART_HEIGHT",
    "DASHBOARD_ICON",
    "DASHBOARD_LAYOUT",
    "DASHBOARD_TITLE",
    "DEDUP_SIMILARITY_THRESHOLD",
    "DEFAULT_CATEGORY",
    "EVENT_TRIGGERS",
    "LOOKBACK_DAYS",
    "LOW_NEWS_SENTIMENT_WEIGHT_MULTIPLIER",
    "MARKET_BENCHMARK",
    "MAX_RETRIES",
    "MAX_WORKERS",
    "MIN_NEWS_ARTICLES_FOR_CONFIDENCE",
    "MOMENTUM_PERIOD",
    "NEWS_CACHE_TTL",
    "NEWS_FEEDS",
    "NEWS_MAX_AGE_HOURS",
    "NEWS_MAX_ARTICLES",
    "PRICE_CACHE_TTL",
    "PRICE_CHANGE_THRESHOLD",
    "PRICE_FETCH_WORKERS",
    "RELEVANCE_HIGH",
    "RELEVANCE_MEDIUM",
    "REQUEST_TIMEOUT",
    "RSI_PERIOD",
    "SCAN_INTERVAL_MINUTES",
    "SECTOR_PEERS",
    "SIGNAL_THRESHOLDS",
    "SNAPSHOT_LOAD_LIMIT",
    "SOURCE_WEIGHTS",
    "STORAGE_DIR",
    "STORAGE_FULL_DETAIL_DAYS",
    "STORAGE_MAX_DAYS",
    "STORAGE_REDUCED_DETAIL_DAYS",
    "TRACKED_ASSETS",
    "YFINANCE_BACKOFF_BASE",
    "YFINANCE_REQUEST_DELAY",
]
