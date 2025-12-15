#!/usr/bin/env python3
"""
Verify ETF Setup - Check if all ETF components are working
"""

import sqlite3
import json
import os
from etf_manager import ETFManager

def verify_database():
    """Verify ETF database"""
    print("=== Database Verification ===")
    
    if not os.path.exists('database/etf_data.db'):
        print("❌ ETF database not found")
        return False
    
    conn = sqlite3.connect('database/etf_data.db')
    
    # Check tables
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    if 'etf_prices' not in tables or 'etf_fundamentals' not in tables:
        print("❌ Required tables not found")
        return False
    
    # Check data
    cursor = conn.execute("SELECT COUNT(*) FROM etf_prices")
    price_count = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) FROM etf_fundamentals")
    fund_count = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(DISTINCT symbol) FROM etf_prices")
    etf_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Database found with {etf_count} ETFs")
    print(f"✅ Price records: {price_count}")
    print(f"✅ Fundamental records: {fund_count}")
    
    return True

def verify_cache_files():
    """Verify cache files"""
    print("\n=== Cache Files Verification ===")
    
    try:
        with open('cache/market_data.json', 'r') as f:
            market_data = json.load(f)
        
        if 'etfs' in market_data:
            etf_count = len(market_data['etfs'])
            print(f"✅ Market data cache contains {etf_count} ETFs")
            
            # Check specific ETFs
            test_etfs = ['SPY', 'QQQ', 'TZA', 'SOXL']
            for etf in test_etfs:
                if etf in market_data['etfs']:
                    print(f"✅ {etf} found in cache")
                else:
                    print(f"❌ {etf} not found in cache")
        else:
            print("❌ No ETF data in market cache")
            return False
            
    except Exception as e:
        print(f"❌ Error reading cache: {e}")
        return False
    
    return True

def verify_web_routes():
    """Verify web app routes"""
    print("\n=== Web Routes Verification ===")
    
    try:
        with open('src/web_app.py', 'r') as f:
            content = f.read()
        
        # Check for ETF routes
        test_routes = ['spy_backtest', 'qqq_backtest', 'tza_backtest']
        found_routes = 0
        
        for route in test_routes:
            if route in content:
                found_routes += 1
                print(f"✅ {route} found")
            else:
                print(f"❌ {route} not found")
        
        if found_routes > 0:
            print(f"✅ Found {found_routes} ETF routes in web app")
            return True
        else:
            print("❌ No ETF routes found in web app")
            return False
            
    except Exception as e:
        print(f"❌ Error reading web app: {e}")
        return False

def verify_frontend_routing():
    """Verify frontend routing"""
    print("\n=== Frontend Routing Verification ===")
    
    try:
        with open('templates/backtest_results.html', 'r') as f:
            content = f.read()
        
        if 'etfRoutes' in content:
            print("✅ ETF routing logic found in frontend")
            return True
        else:
            print("❌ ETF routing logic not found in frontend")
            return False
            
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 Verifying ETF Setup...\n")
    
    results = []
    results.append(verify_database())
    results.append(verify_cache_files())
    results.append(verify_web_routes())
    results.append(verify_frontend_routing())
    
    print(f"\n=== Summary ===")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} verification tests passed!")
        print("✅ ETF setup is complete and working")
    else:
        print(f"⚠️  {passed}/{total} verification tests passed")
        print("❌ Some issues need to be resolved")
    
    # Show available ETFs
    manager = ETFManager()
    etfs = manager.get_etf_list()
    print(f"\n📊 Available ETFs ({len(etfs)}):")
    print(", ".join(etfs))

if __name__ == "__main__":
    main()