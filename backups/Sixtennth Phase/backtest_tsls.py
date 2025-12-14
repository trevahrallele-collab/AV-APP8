#!/usr/bin/env python3

import pandas as pd
import json
import os
from src.av_data_fetcher import AVDataFetcher

def simple_backtest(df, symbol, initial_capital=10000):
    """Simple buy-and-hold backtest"""
    if df.empty:
        return {"error": "No data available"}
    
    start_price = df['close'].iloc[0]
    end_price = df['close'].iloc[-1]
    total_return = (end_price - start_price) / start_price * 100
    
    return {
        "symbol": symbol,
        "strategy": "buy_hold",
        "summary": {
            "num_trades": 1,
            "avg_outcome_R": total_return / 100,
            "win_rate_pos_R": 1.0 if total_return > 0 else 0.0,
            "bullish_trades": 1,
            "bearish_trades": 0
        },
        "trades": [{
            "entry_date": df.index[0].isoformat(),
            "exit_date": df.index[-1].isoformat(),
            "entry_price": start_price,
            "exit_price": end_price,
            "outcome_R": total_return / 100,
            "type": "Bullish"
        }],
        "equity_curve": [0, total_return / 100]
    }

def save_to_cache(df, result, symbol, data_type='stocks'):
    """Save data and results to cache"""
    os.makedirs('cache', exist_ok=True)
    market_data = {
        'dates': df.index.strftime('%Y-%m-%d').tolist(),
        'prices': {
            'open': df['open'].tolist(),
            'high': df['high'].tolist(),
            'low': df['low'].tolist(),
            'close': df['close'].tolist(),
            'volume': df['volume'].tolist()
        }
    }
    
    # Update market data cache
    cache_file = 'cache/market_data.json'
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache = json.load(f)
    else:
        cache = {}
    
    if data_type not in cache:
        cache[data_type] = {}
    cache[data_type][symbol] = market_data
    
    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=2)
    
    # Update backtest results cache
    results_file = 'cache/backtest_results.json'
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            results = json.load(f)
    else:
        results = {}
    
    if data_type not in results:
        results[data_type] = {}
    results[data_type][symbol] = result
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

def main():
    API_KEY = "74M88OXCGWTNUIV9"
    fetcher = AVDataFetcher(API_KEY)
    symbol = "TSLS"
    data_type = 'etfs'
    
    # Try to load from cache first
    cache_market = {}
    try:
        with open('cache/market_data.json', 'r') as f:
            cache_market = json.load(f)
    except Exception:
        cache_market = {}

    df = None
    if data_type in cache_market and symbol in cache_market[data_type]:
        sd = cache_market[data_type][symbol]
        df = pd.DataFrame({
            'open': sd['prices']['open'],
            'high': sd['prices']['high'],
            'low': sd['prices']['low'],
            'close': sd['prices']['close'],
            'volume': sd['prices']['volume']
        }, index=pd.to_datetime(sd['dates']))
    else:
        # If not cached, fetch from API
        print(f"Fetching {symbol} data from AlphaVantage...")
        try:
            df = fetcher.fetch_daily_data(symbol)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return

    print(f"Running buy-and-hold backtest for {symbol}...")
    result = simple_backtest(df, symbol)
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        save_to_cache(df, result, symbol, data_type=data_type)
        summary = result['summary']
        print(f"\n=== {symbol} BACKTEST RESULTS ===")
        print(f"Period: {result['trades'][0]['entry_date'][:10]} to {result['trades'][0]['exit_date'][:10]}")
        print(f"Total Return: {summary['avg_outcome_R']*100:.2f}%")
        print(f"✅ Results saved to web app cache")

if __name__ == "__main__":
    main()
