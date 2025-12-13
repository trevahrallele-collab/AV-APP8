#!/usr/bin/env python3

from src.av_data_fetcher import AVDataFetcher
import json
import time

def fetch_remaining_stocks():
    API_KEY = "74M88OXCGWTNUIV9"
    fetcher = AVDataFetcher(API_KEY)
    
    remaining_stocks = ['ANG', 'MTM']
    
    for symbol in remaining_stocks:
        print(f"Attempting to fetch {symbol}...")
        try:
            # Try with a longer delay
            time.sleep(15)
            df = fetcher.fetch_daily_data(symbol)
            
            if df is not None and not df.empty:
                # Save to database
                fetcher.save_to_db(df, "database/stock_data.db", symbol)
                
                # Convert to JSON format
                data = {
                    'dates': df.index.strftime('%Y-%m-%d').tolist(),
                    'prices': {
                        'open': df['open'].tolist(),
                        'high': df['high'].tolist(),
                        'low': df['low'].tolist(),
                        'close': df['close'].tolist(),
                        'volume': df['volume'].tolist()
                    }
                }
                
                # Load existing market data
                try:
                    with open('cache/market_data.json', 'r') as f:
                        market_data = json.load(f)
                except:
                    market_data = {'stocks': {}, 'forex': {}, 'commodities': {}}
                
                # Add new stock data
                market_data['stocks'][symbol] = data
                
                # Save updated market data
                with open('cache/market_data.json', 'w') as f:
                    json.dump(market_data, f, indent=2)
                
                print(f"✅ {symbol} data saved successfully")
            else:
                print(f"❌ No data returned for {symbol}")
                
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")

if __name__ == "__main__":
    fetch_remaining_stocks()