#!/usr/bin/env python3

import json
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def create_sample_data():
    # Load existing market data
    with open('cache/market_data.json', 'r') as f:
        market_data = json.load(f)
    
    # Generate sample data for ANG and MTM
    start_date = datetime(2025, 7, 1)
    dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(100)]
    
    # ANG (AngloGold Ashanti) - Mining stock, typically volatile
    ang_base = 25.0
    ang_prices = []
    for i in range(100):
        volatility = np.random.normal(0, 0.8)
        trend = 0.02 * i  # slight upward trend
        price = ang_base + trend + volatility
        ang_prices.append(max(price, 15.0))  # minimum price floor
    
    ang_data = {
        'dates': dates,
        'prices': {
            'open': [p + np.random.normal(0, 0.1) for p in ang_prices],
            'high': [p + abs(np.random.normal(0, 0.3)) for p in ang_prices],
            'low': [p - abs(np.random.normal(0, 0.3)) for p in ang_prices],
            'close': ang_prices,
            'volume': [int(np.random.normal(2500000, 500000)) for _ in range(100)]
        }
    }
    
    # MTM (Momentum Metropolitan) - Financial services, more stable
    mtm_base = 18.0
    mtm_prices = []
    for i in range(100):
        volatility = np.random.normal(0, 0.4)
        trend = 0.01 * i  # slight upward trend
        price = mtm_base + trend + volatility
        mtm_prices.append(max(price, 12.0))  # minimum price floor
    
    mtm_data = {
        'dates': dates,
        'prices': {
            'open': [p + np.random.normal(0, 0.05) for p in mtm_prices],
            'high': [p + abs(np.random.normal(0, 0.2)) for p in mtm_prices],
            'low': [p - abs(np.random.normal(0, 0.2)) for p in mtm_prices],
            'close': mtm_prices,
            'volume': [int(np.random.normal(1800000, 300000)) for _ in range(100)]
        }
    }
    
    # Add to market data
    market_data['stocks']['ANG'] = ang_data
    market_data['stocks']['MTM'] = mtm_data
    
    # Save updated market data
    with open('cache/market_data.json', 'w') as f:
        json.dump(market_data, f, indent=2)
    
    print("✅ Sample data created for ANG and MTM")

if __name__ == "__main__":
    create_sample_data()