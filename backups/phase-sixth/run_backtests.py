import json
import os
import pandas as pd
from ob_refined_strategy import (
    compute_indicators, detect_order_blocks, refined_backtest, 
    summarize_trades, year_by_year, plot_equity_curve, plot_yearly_cumR
)

def run_backtest_on_symbol(data, symbol_name):
    """Run backtest on a single symbol's data"""
    try:
        # Convert JSON data to DataFrame
        df = pd.DataFrame({
            'open': data['prices']['open'],
            'high': data['prices']['high'],
            'low': data['prices']['low'],
            'close': data['prices']['close']
        }, index=pd.to_datetime(data['dates']))
        
        # Add indicators
        df = compute_indicators(df, ema_span=50, atr_span=14)
        
        # Detect order blocks
        ob = detect_order_blocks(df, lookback=10)
        
        # Run backtest
        trades = refined_backtest(
            df=df,
            ob=ob,
            entry_wait_bars=60,
            atr_threshold=0.0060,
            stop_on_tie=True
        )
        
        # Generate summary
        summary = summarize_trades(trades)
        by_year = year_by_year(trades)
        
        # Convert timestamps to strings for JSON serialization
        trades_dict = []
        if not trades.empty:
            for _, trade in trades.iterrows():
                trade_dict = trade.to_dict()
                for key, value in trade_dict.items():
                    if pd.isna(value):
                        trade_dict[key] = None
                    elif hasattr(value, 'isoformat'):
                        trade_dict[key] = value.isoformat()
                trades_dict.append(trade_dict)
        
        return {
            'symbol': symbol_name,
            'summary': summary,
            'trades': trades_dict,
            'yearly': by_year.to_dict('records') if not by_year.empty else [],
            'equity_curve': trades['outcome_R'].cumsum().tolist() if not trades.empty else []
        }
        
    except Exception as e:
        return {
            'symbol': symbol_name,
            'error': str(e),
            'summary': {'num_trades': 0, 'avg_outcome_R': 0.0, 'win_rate_pos_R': 0.0}
        }

def run_all_backtests():
    """Run backtests on all cached data"""
    print("=== RUNNING BACKTESTS ON ALL DATA ===\n")
    
    # Load cached data
    with open('cache/market_data.json', 'r') as f:
        cache_data = json.load(f)
    
    results = {}
    
    # Run backtests for each data type and symbol
    for data_type, symbols in cache_data.items():
        print(f"Processing {data_type.upper()}...")
        results[data_type] = {}
        
        for symbol, data in symbols.items():
            if symbol == 'daily_prices':  # Skip generic table
                continue
                
            print(f"  Running backtest on {symbol}...")
            result = run_backtest_on_symbol(data, symbol)
            results[data_type][symbol] = result
            
            if 'error' not in result:
                summary = result['summary']
                print(f"    ✅ {summary['num_trades']} trades, {summary['avg_outcome_R']:.2f}R avg, {summary['win_rate_pos_R']:.1%} win rate")
            else:
                print(f"    ❌ Error: {result['error']}")
    
    # Save results
    os.makedirs('cache', exist_ok=True)
    with open('cache/backtest_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Backtest results saved to cache/backtest_results.json")
    return results

if __name__ == "__main__":
    run_all_backtests()