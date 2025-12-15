#!/usr/bin/env python3
"""
Run All Strategies - Execute all trading strategies with proper parameters
"""

import subprocess
import sys
import time
import json
from datetime import datetime

def run_ob_strategy():
    """Run OB refined strategy with CSV parameter"""
    try:
        print("🔄 Running OB Refined Strategy...")
        result = subprocess.run([
            sys.executable, 'ob_refined_strategy.py',
            '--csv', 'data-storage/stock_data.csv'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ OB Strategy completed")
            return True
        else:
            print(f"❌ OB Strategy failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ OB Strategy error: {e}")
        return False

def run_fractal_strategy():
    """Run Fractal refined strategy"""
    try:
        print("🔄 Running Fractal Refined Strategy...")
        result = subprocess.run([
            sys.executable, 'fractal_refined_strategy.py'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Fractal Strategy completed")
            return True
        else:
            print(f"❌ Fractal Strategy failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Fractal Strategy error: {e}")
        return False

def run_fractal_ob_strategy():
    """Run Fractal OB combined strategy"""
    try:
        print("🔄 Running Fractal OB Strategy...")
        result = subprocess.run([
            sys.executable, 'fractal_ob_strategy.py'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Fractal OB Strategy completed")
            return True
        else:
            print(f"❌ Fractal OB Strategy failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Fractal OB Strategy error: {e}")
        return False

def verify_results():
    """Verify all strategy results"""
    print("\n🔍 Verifying strategy results...")
    
    files = {
        'OB Strategy': 'cache/ob_refined_strategy_results.json',
        'Fractal Strategy': 'cache/fractal_refined_strategy_results.json',
        'Fractal OB Strategy': 'cache/fractal_ob_strategy_results.json'
    }
    
    for name, file_path in files.items():
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            total_symbols = 0
            for market, symbols in data.items():
                if isinstance(symbols, dict):
                    total_symbols += len(symbols)
            
            print(f"✅ {name}: {total_symbols} symbols processed")
            
        except Exception as e:
            print(f"❌ {name}: Error reading results - {e}")

def main():
    """Main execution"""
    print("🚀 Running All Trading Strategies")
    print("=" * 50)
    
    start_time = datetime.now()
    results = {}
    
    # Run each strategy
    strategies = [
        ("OB Refined", run_ob_strategy),
        ("Fractal Refined", run_fractal_strategy), 
        ("Fractal OB", run_fractal_ob_strategy)
    ]
    
    for i, (name, func) in enumerate(strategies, 1):
        print(f"\n📊 Strategy {i}/{len(strategies)}: {name}")
        success = func()
        results[name] = success
        
        if i < len(strategies):
            print("⏸️  Pausing 3 seconds...")
            time.sleep(3)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Summary
    print(f"\n📈 Strategy Execution Summary")
    print(f"⏱️  Total time: {duration}")
    
    successful = sum(results.values())
    total = len(results)
    print(f"✅ Successful: {successful}/{total}")
    
    for strategy, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {strategy}")
    
    # Verify results
    verify_results()
    
    print(f"\n🎉 All strategies completed!")

if __name__ == "__main__":
    main()