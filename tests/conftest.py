"""
conftest.py — Shared imports and fixtures for the test suite.

Mock targets use the "patch where it's used" rule:
  src.engine.fetch_price_history  (engine imports it from src.price)
  src.engine.fetch_news_articles  (engine imports it from src.news)
  src.engine.analyse_market_context (engine imports it from src.context)
"""

import datetime as dt

import pandas as pd
import pytest

import storage.storage as storage

# ── Price series ──────────────────────────────────────────────────────────────

@pytest.fixture
def price_series_flat():
    return pd.Series([100.0] * 40)


@pytest.fixture
def price_series_rising():
    return pd.Series([100.0 + i for i in range(40)])


@pytest.fixture
def price_series_falling():
    return pd.Series([139.0 - i for i in range(40)])


# ── OHLCV DataFrame factory ───────────────────────────────────────────────────

@pytest.fixture
def ohlcv_df():
    """Call ohlcv_df(series) to get a yfinance-shaped DataFrame with DatetimeIndex."""
    def _make(series):
        n   = len(series)
        idx = pd.date_range(
            end=pd.Timestamp.today().normalize(),
            periods=n,
            freq="B",  # business days — matches yfinance OHLCV output
        )
        v = series.values
        return pd.DataFrame(
            {"Open": v, "High": v * 1.005, "Low": v * 0.995, "Close": v,
             "Volume": [1_000_000] * n},
            index=idx,
        )
    return _make


# ── Articles ──────────────────────────────────────────────────────────────────

@pytest.fixture
def synthetic_articles():
    """5 articles: 2 gold, 1 near-duplicate, 1 clearly negative, 1 clearly positive."""
    now = dt.datetime.now(dt.UTC)
    return [
        {"title": "gold bullion prices surge on central bank demand",
         "summary": "Gold hits new highs.", "link": "https://example.com/1",
         "source": "Reuters Business", "published": now - dt.timedelta(hours=2)},
        {"title": "central bank gold buying lifts bullion to record highs",
         "summary": "Bullion advances.", "link": "https://example.com/2",
         "source": "CNBC Top News", "published": now - dt.timedelta(hours=4)},
        {"title": "central bank demand surge on gold bullion prices",  # near-duplicate of [0]
         "summary": "Central bank demand pushes gold higher.", "link": "https://example.com/3",
         "source": "BBC Business", "published": now - dt.timedelta(hours=5)},
        {"title": "market crash plunge crisis recession fear selloff",
         "summary": "Markets in freefall.", "link": "https://example.com/4",
         "source": "MarketWatch", "published": now - dt.timedelta(hours=6)},
        {"title": "stocks surge rally record high breakout boom growth",
         "summary": "Equity markets surge to record highs.", "link": "https://example.com/5",
         "source": "Reuters Business", "published": now - dt.timedelta(hours=8)},
    ]


# ── Signal input dicts ────────────────────────────────────────────────────────

@pytest.fixture
def synthetic_metrics():
    return {
        "latest_price": 1850.50, "change_1d": 1.25, "change_7d": 3.40,
        "change_30d": 8.20, "high_30d": 1900.00, "low_30d": 1780.00,
        "volatility": 0.85, "trend": "uptrend",
    }


@pytest.fixture
def synthetic_momentum():
    return {"rsi": 58.5, "roc_10d": 4.2, "trend_strength": 2.1, "momentum_accel": 0.3}


# ── Storage isolation ─────────────────────────────────────────────────────────

@pytest.fixture
def storage_dir(tmp_path, monkeypatch):
    """Redirect storage writes to a temp dir so no real files are touched."""
    monkeypatch.setattr(storage, "_storage_path", tmp_path)
    yield tmp_path


# ── Network mocks ─────────────────────────────────────────────────────────────
# Patch names where they are *used* (in src.engine), not where they are defined.

@pytest.fixture
def mock_price_history(mocker, ohlcv_df, price_series_rising):
    return mocker.patch(
        "src.engine.fetch_price_history",
        return_value=ohlcv_df(price_series_rising),
    )


@pytest.fixture
def mock_news_articles(mocker, synthetic_articles):
    return mocker.patch(
        "src.engine.fetch_news_articles",
        return_value=synthetic_articles,
    )


@pytest.fixture
def mock_market_context(mocker):
    return mocker.patch(
        "src.engine.analyse_market_context",
        return_value=None,
    )
