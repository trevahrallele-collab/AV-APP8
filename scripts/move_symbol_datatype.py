#!/usr/bin/env python3
"""Move a symbol between data types in cache files (e.g., 'stocks' -> 'etfs')."""
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CACHE_DIR = os.path.join(REPO_ROOT, 'cache')
FILES = [
    'market_data.json',
    'backtest_results.json',
    'ob_refined_strategy_results.json',
    'fractal_refined_strategy_results.json',
    'fractal_ob_strategy_results.json',
    'ob_refined_strategy_signal_log.json',
    'fractal_refined_strategy_signal_log.json',
    'fractal_ob_strategy_signal_log.json',
    'signal_ranking_report.json'
]


def move_symbol(symbol: str, to_type: str = 'etfs'):
    moved = []
    for fname in FILES:
        path = os.path.join(CACHE_DIR, fname)
        if not os.path.exists(path):
            continue
        with open(path, 'r') as f:
            try:
                data = json.load(f)
            except Exception:
                continue

        # If file has data-type structure
        changed = False
        if isinstance(data, dict) and any(k in data for k in ['stocks','etfs','forex','commodities','crypto','etfs']):
            # find symbol in any datatype
            for dtype, symbols in list(data.items()):
                if isinstance(symbols, dict) and symbol in symbols:
                    value = symbols.pop(symbol)
                    # ensure target dtype exists
                    if to_type not in data:
                        data[to_type] = {}
                    data[to_type][symbol] = value
                    changed = True
                    moved.append((fname, dtype, to_type))
        else:
            # For signal log files where structure may be different
            if fname.endswith('_signal_log.json') and 'by_symbol' in data and symbol in data['by_symbol']:
                data['by_symbol'][symbol + '_moved'] = data['by_symbol'].pop(symbol)
                changed = True
                moved.append((fname, 'by_symbol', 'by_symbol'))
            if fname == 'signal_ranking_report.json':
                # More complex; skip for now
                pass

        if changed:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)

    return moved


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: move_symbol_datatype.py SYMBOL [TO_TYPE]')
        sys.exit(1)
    symbol = sys.argv[1]
    to_type = sys.argv[2] if len(sys.argv) > 2 else 'etfs'
    moved = move_symbol(symbol, to_type)
    if moved:
        print('Moved entries:')
        for m in moved:
            print(f' - {m[0]}: {m[1]} -> {m[2]}')
    else:
        print('No entries moved')
