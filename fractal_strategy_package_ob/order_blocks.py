# -*- coding: utf-8 -*-
"""
Order Block detection and utilities (simple SMC-style approximation).

Definitions used:
- Bearish Order Block (Supply): last up candle (Open < Close) before an impulsive down move
  where the subsequent N bars break the prior structure (close below recent fractal low)
- Bullish Order Block (Demand): last down candle (Open > Close) before an impulsive up move
  where the subsequent N bars break the prior structure (close above recent fractal high)

Outputs zones as (start_ts, end_ts, low, high) rectangles for plotting/filtering.
This is a pragmatic approximation suitable for backtesting.
"""
import pandas as pd
import numpy as np

from typing import List, Tuple


def find_order_blocks(df: pd.DataFrame,
                      fractal_high: pd.Series,
                      fractal_low: pd.Series,
                      impulse_bars: int = 3,
                      min_body_ratio: float = 0.3,
                      lookback: int = 20) -> pd.DataFrame:
    """
    Detect bullish/bearish order blocks using a simple impulse + structure-break heuristic.

    Params:
      - impulse_bars: how many bars to confirm an impulse after the candidate OB candle
      - min_body_ratio: min(|Close-Open| / (High-Low)) to treat the candidate candle body as meaningful
      - lookback: structure reference window for fractal extremes

    Returns DataFrame with columns:
      - 'bullish_ob' (bool), 'bearish_ob' (bool)
      - 'ob_low', 'ob_high' (price range of the defining candle)
    """
    o, h, l, c = df['Open'], df['High'], df['Low'], df['Close']
    rng = h - l
    body = (c - o).abs()
    body_ratio = body / rng.replace(0, np.nan)

    n = len(df)
    bull = np.zeros(n, dtype=bool)
    bear = np.zeros(n, dtype=bool)
    ob_low = np.full(n, np.nan)
    ob_high = np.full(n, np.nan)

    # Rolling reference of fractal extremes for structure
    fh_roll = fractal_high.rolling(lookback, min_periods=1).max()
    fl_roll = fractal_low.rolling(lookback, min_periods=1).min()

    for i in range(n - impulse_bars):
        # Candidate bullish OB: last down candle (Close < Open)
        if c.iat[i] < o.iat[i] and body_ratio.iat[i] >= min_body_ratio:
            # Impulse up: subsequent bars break above recent fractal high
            future = c.iloc[i+1:i+1+impulse_bars]
            level = fh_roll.iat[i]
            if future.max() > level:
                bull[i] = True
                ob_low[i] = l.iat[i]
                ob_high[i] = h.iat[i]
        # Candidate bearish OB: last up candle (Close > Open)
        if c.iat[i] > o.iat[i] and body_ratio.iat[i] >= min_body_ratio:
            future = c.iloc[i+1:i+1+impulse_bars]
            level = fl_roll.iat[i]
            if future.min() < level:
                bear[i] = True
                ob_low[i] = l.iat[i]
                ob_high[i] = h.iat[i]

    out = pd.DataFrame(index=df.index)
    out['bullish_ob'] = bull
    out['bearish_ob'] = bear
    out['ob_low'] = ob_low
    out['ob_high'] = ob_high
    return out
