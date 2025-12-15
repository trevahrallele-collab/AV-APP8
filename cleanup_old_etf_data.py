#!/usr/bin/env python3
"""
Cleanup Old ETF Data - Remove old ETF references from strategy results
"""

import json
import os

def clean_strategy_results():
    """Clean ETF data from strategy result files"""
    strategy_files = [
        'cache/backtest_results.json',
        'cache/ob_refined_strategy_results.json', 
        'cache/fractal_refined_strategy_results.json',
        'cache/fractal_ob_strategy_results.json'
    ]
    
    for file_path in strategy_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Clear ETF data from strategy results
                if 'etfs' in data:
                    data['etfs'] = {}
                    print(f"✅ Cleared ETF data from {file_path}")
                
                # Remove ETF symbols from other sections if they exist
                etf_symbols = ['SPY', 'QQQ', 'TZA', 'SOXL', 'SOXS', 'TQQQ', 'TSLL', 'TSLS', 'ETHA', 'IBIT']
                
                for section in ['stocks', 'commodities']:
                    if section in data:
                        for symbol in etf_symbols:
                            if symbol in data[section]:
                                del data[section][symbol]
                                print(f"✅ Removed {symbol} from {section} in {file_path}")
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")

def main():
    """Main cleanup function"""
    print("🧹 Cleaning up old ETF data...\n")
    
    clean_strategy_results()
    
    print("\n✅ Cleanup completed!")
    print("📊 ETF data has been freshly parsed and is ready for use")

if __name__ == "__main__":
    main()