from flask import Flask, render_template, jsonify, request
from av_data_fetcher import AVDataFetcher
import pandas as pd
import json

app = Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/dashboard')
def dashboard():
    return render_template('interactive_dashboard.html')

@app.route('/backtests')
def backtests():
    return render_template('backtest_results.html')

@app.route('/api/backtest-results')
def api_backtest_results():
    try:
        with open('backtest_results.json', 'r') as f:
            results = json.load(f)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fetch-data')
def fetch_data():
    data_type = request.args.get('type', 'stocks')
    symbol = request.args.get('symbol', 'AAPL')
    
    API_KEY = "74M88OXCGWTNUIV9"
    
    try:
        fetcher = AVDataFetcher(API_KEY)
        
        # Determine database path
        if data_type == 'stocks':
            db_path = "database/stock_data.db"
        elif data_type == 'forex':
            db_path = "database/forex_data.db"
        else:  # commodities
            db_path = "database/commodity_data.db"
        
        table_name = symbol.replace('/', '_')
        
        # Fetch new data
        if data_type == 'stocks':
            df = fetcher.fetch_daily_data(symbol)
        elif data_type == 'forex':
            from_symbol, to_symbol = symbol.split('/')
            df = fetcher.fetch_forex_data(from_symbol, to_symbol)
        else:  # commodities
            df = fetcher.fetch_commodity_data(symbol)
        
        # Save to database
        fetcher.save_to_db(df, db_path, table_name)
        
        return jsonify({'success': f'Data fetched and cached for {symbol}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data')
def api_data():
    data_type = request.args.get('type', 'stocks')
    symbol = request.args.get('symbol', 'AAPL')
    time_range = request.args.get('range', '1Y')
    
    try:
        # Load from JSON cache
        with open('market_data.json', 'r') as f:
            cache_data = json.load(f)
        
        table_name = symbol.replace('/', '_')
        
        if data_type not in cache_data or table_name not in cache_data[data_type]:
            return jsonify({'error': f'No cached data for {symbol}'}), 404
        
        data = cache_data[data_type][table_name]
        
        # Filter data based on time range
        range_map = {'1M': 30, '3M': 90, '6M': 180, '1Y': 365, '2Y': 730}
        limit = range_map.get(time_range, 365)
        
        filtered_data = {
            'dates': data['dates'][-limit:],
            'prices': {
                'open': data['prices']['open'][-limit:],
                'high': data['prices']['high'][-limit:],
                'low': data['prices']['low'][-limit:],
                'close': data['prices']['close'][-limit:],
                'volume': data['prices']['volume'][-limit:]
            }
        }
        
        return jsonify(filtered_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)