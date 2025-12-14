#!/usr/bin/env python3
"""Run OB and Fractal strategies for TZA and save results to cache"""
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, REPO_ROOT)

from run_backtests import run_strategy_backtest


def load_market_data(symbol: str, data_type: str = 'etfs'):
    try:
        cache_file = os.path.join(REPO_ROOT, 'cache', 'market_data.json')
        with open(cache_file, 'r') as f:
            cache = json.load(f)
    except Exception:
        return None
    if data_type in cache and symbol in cache[data_type]:
        return cache[data_type][symbol]
    return None


def save_strategy_result(strategy_name: str, symbol: str, result: dict, data_type: str = 'etfs'):
    os.makedirs('cache', exist_ok=True)
    cache_dir = os.path.join(REPO_ROOT, 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f'{strategy_name}_results.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            existing = json.load(f)
    else:
        existing = {}
    if data_type not in existing:
        existing[data_type] = {}
    existing[data_type][symbol] = result
    with open(path, 'w') as f:
        json.dump(existing, f, indent=2)


def main():
    symbol = 'TZA'
    data_type = 'etfs'
    market_data = load_market_data(symbol, data_type)
    if not market_data:
        print(f'No cached market data for {symbol} found; aborting.')
        return

    strategies = ['ob_refined_strategy', 'fractal_refined_strategy']
    for s in strategies:
        print(f'Running {s} for {symbol}...')
        result = run_strategy_backtest(market_data, symbol_name=symbol, strategy_name=s)
        save_strategy_result(s, symbol, result, data_type=data_type)
        print(f'Saved {s} results for {symbol} to cache/{s}_results.json')


if __name__ == '__main__':
    main()
