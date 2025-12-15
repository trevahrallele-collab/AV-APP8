#!/usr/bin/env python3
"""
ETF Data Scraper - Comprehensive ETF data fetching and parsing
"""

import requests
import pandas as pd
import sqlite3
import json
import time
from datetime import datetime, timedelta
import yfinance as yf
from src.av_data_fetcher import AVDataFetcher

class ETFDataScraper:
    def __init__(self, api_key="74M88OXCGWTNUIV9"):
        self.api_key = api_key
        self.av_fetcher = AVDataFetcher(api_key)
        self.etf_symbols = [
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'AGG', 'BND', 'TLT',
            'GLD', 'SLV', 'USO', 'UNG', 'XLF', 'XLK', 'XLE', 'XLV', 'XLI', 'XLP',
            'SOXL', 'SOXS', 'TQQQ', 'SQQQ', 'SPXL', 'SPXS', 'TZA', 'IWM', 'TSLL',
            'TSLS', 'ETHA', 'IBIT', 'ARKK', 'ARKQ', 'ARKG', 'ARKW', 'ARKF'
        ]
        
    def fetch_etf_fundamentals(self, symbol):
        """Fetch ETF fundamentals using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'expense_ratio': info.get('annualReportExpenseRatio', 0),
                'net_assets': info.get('totalAssets', 0),
                'inception_date': info.get('fundInceptionDate', None),
                'category': info.get('category', 'ETF'),
                'family': info.get('fundFamily', 'Unknown'),
                'yield': info.get('yield', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'beta': info.get('beta', 0),
                'volume': info.get('averageVolume', 0),
                'market_cap': info.get('marketCap', 0)
            }
        except Exception as e:
            print(f"Error fetching fundamentals for {symbol}: {e}")
            return None
    
    def fetch_etf_price_data(self, symbol):
        """Fetch ETF price data using Alpha Vantage"""
        try:
            return self.av_fetcher.fetch_daily_data(symbol)
        except Exception as e:
            print(f"Error fetching price data for {symbol}: {e}")
            try:
                # Fallback to yfinance
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="2y")
                df.columns = df.columns.str.lower()
                return df
            except Exception as e2:
                print(f"Fallback failed for {symbol}: {e2}")
                return None
    
    def scrape_all_etfs(self):
        """Scrape all ETF data"""
        etf_data = {}
        fundamentals_data = {}
        
        print("Starting ETF data scraping...")
        
        for i, symbol in enumerate(self.etf_symbols):
            print(f"Processing {symbol} ({i+1}/{len(self.etf_symbols)})")
            
            # Fetch fundamentals
            fundamentals = self.fetch_etf_fundamentals(symbol)
            if fundamentals:
                fundamentals_data[symbol] = fundamentals
            
            # Fetch price data
            price_data = self.fetch_etf_price_data(symbol)
            if price_data is not None and not price_data.empty:
                etf_data[symbol] = {
                    'dates': price_data.index.strftime('%Y-%m-%d').tolist(),
                    'prices': {
                        'open': price_data['open'].tolist(),
                        'high': price_data['high'].tolist(),
                        'low': price_data['low'].tolist(),
                        'close': price_data['close'].tolist(),
                        'volume': price_data['volume'].tolist()
                    }
                }
            
            # Rate limiting
            time.sleep(0.5)
        
        return etf_data, fundamentals_data
    
    def save_to_database(self, etf_data, fundamentals_data):
        """Save ETF data to database"""
        conn = sqlite3.connect('database/etf_data.db')
        
        # Create tables
        conn.execute('''
            CREATE TABLE IF NOT EXISTS etf_prices (
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                PRIMARY KEY (symbol, date)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS etf_fundamentals (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                expense_ratio REAL,
                net_assets REAL,
                inception_date TEXT,
                category TEXT,
                family TEXT,
                yield REAL,
                pe_ratio REAL,
                beta REAL,
                volume INTEGER,
                market_cap REAL
            )
        ''')
        
        # Insert price data
        for symbol, data in etf_data.items():
            for i, date in enumerate(data['dates']):
                conn.execute('''
                    INSERT OR REPLACE INTO etf_prices 
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, date,
                    data['prices']['open'][i],
                    data['prices']['high'][i],
                    data['prices']['low'][i],
                    data['prices']['close'][i],
                    data['prices']['volume'][i]
                ))
        
        # Insert fundamentals data
        for symbol, data in fundamentals_data.items():
            conn.execute('''
                INSERT OR REPLACE INTO etf_fundamentals 
                (symbol, name, expense_ratio, net_assets, inception_date, 
                 category, family, yield, pe_ratio, beta, volume, market_cap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['symbol'], data['name'], data['expense_ratio'],
                data['net_assets'], data['inception_date'], data['category'],
                data['family'], data['yield'], data['pe_ratio'], data['beta'],
                data['volume'], data['market_cap']
            ))
        
        conn.commit()
        conn.close()
        print("ETF data saved to database")
    
    def update_cache_files(self, etf_data):
        """Update cache files with new ETF data"""
        # Update market_data.json
        try:
            with open('cache/market_data.json', 'r') as f:
                market_data = json.load(f)
        except FileNotFoundError:
            market_data = {}
        
        market_data['etfs'] = etf_data
        
        with open('cache/market_data.json', 'w') as f:
            json.dump(market_data, f, indent=2)
        
        # Clear ETF data from strategy results
        strategy_files = [
            'cache/backtest_results.json',
            'cache/ob_refined_strategy_results.json',
            'cache/fractal_refined_strategy_results.json',
            'cache/fractal_ob_strategy_results.json'
        ]
        
        for file_path in strategy_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if 'etfs' in data:
                    data['etfs'] = {}
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            except FileNotFoundError:
                continue
        
        print("Cache files updated")

def main():
    """Main execution function"""
    scraper = ETFDataScraper()
    
    print("Scraping ETF data...")
    etf_data, fundamentals_data = scraper.scrape_all_etfs()
    
    print(f"Successfully scraped {len(etf_data)} ETFs")
    
    # Save to database
    scraper.save_to_database(etf_data, fundamentals_data)
    
    # Update cache files
    scraper.update_cache_files(etf_data)
    
    print("ETF data scraping completed!")
    print(f"Scraped symbols: {list(etf_data.keys())}")

if __name__ == "__main__":
    main()