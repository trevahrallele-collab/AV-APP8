#!/usr/bin/env python3
"""
Batch Backtest Runner - Run backtests across all markets and strategies efficiently
"""

import json
import time
import subprocess
import sys
from datetime import datetime

class BatchBacktestRunner:
    def __init__(self):
        self.strategies = [
            'ob_refined_strategy',
            'fractal_refined_strategy', 
            'fractal_ob_strategy'
        ]
        
        self.markets = {
            'stocks': ['MSFT', 'GOOGL', 'AAPL', 'BTC', 'LTC'],
            'etfs': ['SPY', 'QQQ', 'TZA', 'SOXL', 'SOXS', 'TQQQ', 'TSLL'],
            'forex': ['GBP_USD', 'USD_JPY', 'EUR_USD', 'USD_CHF'],
            'commodities': ['GOLD', 'NATURAL_GAS']
        }
    
    def run_strategy_backtest(self, strategy_name):
        """Run backtest for a specific strategy"""
        try:
            print(f"🔄 Running {strategy_name}...")
            result = subprocess.run([
                sys.executable, f'{strategy_name}.py'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {strategy_name} completed")
                return True
            else:
                print(f"❌ {strategy_name} failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {strategy_name} timed out")
            return False
        except Exception as e:
            print(f"❌ {strategy_name} error: {e}")
            return False
    
    def run_all_backtests(self):
        """Run all strategy backtests"""
        print("🚀 Starting batch backtest run...\n")
        start_time = datetime.now()
        
        results = {}
        
        for i, strategy in enumerate(self.strategies, 1):
            print(f"📊 Strategy {i}/{len(self.strategies)}: {strategy}")
            
            success = self.run_strategy_backtest(strategy)
            results[strategy] = success
            
            # Brief pause between strategies
            if i < len(self.strategies):
                print("⏸️  Pausing 5 seconds...\n")
                time.sleep(5)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Summary
        print(f"\n📈 Batch Backtest Summary")
        print(f"⏱️  Total time: {duration}")
        
        successful = sum(results.values())
        total = len(results)
        
        print(f"✅ Successful: {successful}/{total}")
        
        for strategy, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {strategy}")
        
        return results
    
    def verify_results(self):
        """Verify backtest results were generated"""
        print("\n🔍 Verifying results...")
        
        result_files = [
            'cache/ob_refined_strategy_results.json',
            'cache/fractal_refined_strategy_results.json', 
            'cache/fractal_ob_strategy_results.json'
        ]
        
        for file_path in result_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                total_symbols = 0
                for market, symbols in data.items():
                    if isinstance(symbols, dict):
                        total_symbols += len(symbols)
                
                print(f"✅ {file_path}: {total_symbols} symbols")
                
            except Exception as e:
                print(f"❌ {file_path}: Error - {e}")

def main():
    """Main execution"""
    runner = BatchBacktestRunner()
    
    print("🎯 Batch Backtest Runner")
    print("=" * 50)
    
    # Show what will be processed
    total_symbols = sum(len(symbols) for symbols in runner.markets.values())
    print(f"📊 Markets: {len(runner.markets)} ({total_symbols} symbols)")
    print(f"🔧 Strategies: {len(runner.strategies)}")
    
    for market, symbols in runner.markets.items():
        print(f"  📈 {market}: {len(symbols)} symbols")
    
    print("\n" + "=" * 50)
    
    # Run backtests
    results = runner.run_all_backtests()
    
    # Verify results
    runner.verify_results()
    
    print(f"\n🎉 Batch backtest completed!")

if __name__ == "__main__":
    main()