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

@app.route('/signals')
def trading_signals():
    return render_template('trading_signals.html')

# ETF Routes (Complete list)
@app.route('/agg')
def agg_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='AGG')

@app.route('/arkf')
def arkf_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='ARKF')

@app.route('/arkg')
def arkg_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='ARKG')

@app.route('/arkk')
def arkk_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='ARKK')

@app.route('/arkq')
def arkq_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='ARKQ')

@app.route('/arkw')
def arkw_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='ARKW')

@app.route('/bnd')
def bnd_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='BND')

@app.route('/etha')
def etha_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='ETHA')

@app.route('/gld')
def gld_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='GLD')

@app.route('/ibit')
def ibit_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='IBIT')

@app.route('/iwm')
def iwm_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='IWM')

@app.route('/qqq')
def qqq_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='QQQ')

@app.route('/slv')
def slv_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='SLV')

@app.route('/soxl')
def soxl_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='SOXL')

@app.route('/soxs')
def soxs_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='SOXS')

@app.route('/spxl')
def spxl_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='SPXL')

@app.route('/spxs')
def spxs_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='SPXS')

@app.route('/spy')
def spy_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='SPY')

@app.route('/sqqq')
def sqqq_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='SQQQ')

@app.route('/tlt')
def tlt_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='TLT')

@app.route('/tqqq')
def tqqq_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='TQQQ')

@app.route('/tsll')
def tsll_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='TSLL')

@app.route('/tsls')
def tsls_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='TSLS')

@app.route('/tza')
def tza_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='TZA')

@app.route('/ung')
def ung_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='UNG')

@app.route('/uso')
def uso_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='USO')

@app.route('/vea')
def vea_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='VEA')

@app.route('/voo')
def voo_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='VOO')

@app.route('/vti')
def vti_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='VTI')

@app.route('/vwo')
def vwo_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='VWO')

@app.route('/xle')
def xle_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='XLE')

@app.route('/xlf')
def xlf_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='XLF')

@app.route('/xli')
def xli_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='XLI')

@app.route('/xlk')
def xlk_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='XLK')

@app.route('/xlp')
def xlp_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='XLP')

@app.route('/xlv')
def xlv_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='XLV')

@app.route('/backtest/<data_type>/<symbol>')
def backtest_detail(data_type, symbol):
    return render_template('backtest_detail.html', data_type=data_type, symbol=symbol)

@app.route('/api/backtest-detail/<data_type>/<symbol>')
def api_backtest_detail(data_type, symbol):
    try:
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        with open(os.path.join(project_root, 'cache', 'backtest_results.json'), 'r') as f:
            results = json.load(f)
        
        with open(os.path.join(project_root, 'cache', 'market_data.json'), 'r') as f:
            market_data = json.load(f)
        
        if data_type not in results or symbol not in results[data_type]:
            return jsonify({'error': 'Symbol not found'}), 404
        
        backtest_result = results[data_type][symbol]
        price_data = market_data.get(data_type, {}).get(symbol, {})
        
        # Get admin settings from query parameters
        risk_per_trade = float(request.args.get('risk', 100))
        starting_capital = float(request.args.get('capital', 10000))
        
        trades = backtest_result['trades']
        is_etf = data_type == 'etfs' or backtest_result.get('strategy') == 'buy_hold'
        
        if is_etf:
            # ETF buy-and-hold calculation
            if trades:
                total_return = starting_capital * trades[0]['outcome_R']
                equity_curve = [starting_capital, starting_capital + total_return]
                returns = [trades[0]['outcome_R']]
            else:
                total_return = 0
                equity_curve = [starting_capital]
                returns = [0]
            total_invested = starting_capital
        else:
            # Trading strategy calculation
            equity_curve = [starting_capital]
            total_invested = 0
            total_return = 0
            returns = []
            
            for trade in trades:
                pnl = trade['outcome_R'] * risk_per_trade
                total_return += pnl
                equity_curve.append(equity_curve[-1] + pnl)
                total_invested += risk_per_trade
                returns.append(pnl / equity_curve[-2] if equity_curve[-2] > 0 else 0)
        
        final_capital = equity_curve[-1] if equity_curve else starting_capital
        roi_percent = ((final_capital - starting_capital) / starting_capital) * 100
        
        # Calculate drawdown
        drawdown = []
        peak = equity_curve[0]
        max_drawdown = 0
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (value - peak) / peak
            drawdown.append(dd)
            if dd < max_drawdown:
                max_drawdown = dd
        
        # Calculate ratios
        import math
        if len(returns) > 0 and returns[0] != 0:
            avg_return = sum(returns) / len(returns)
            if len(returns) > 1:
                return_std = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1))
            else:
                return_std = 0
            
            sharpe_ratio = avg_return / return_std if return_std > 0 else 0
            
            negative_returns = [r for r in returns if r < 0]
            if negative_returns:
                downside_std = math.sqrt(sum(r ** 2 for r in negative_returns) / len(negative_returns))
                sortino_ratio = avg_return / downside_std if downside_std > 0 else 0
            else:
                sortino_ratio = 999 if avg_return > 0 else 0
            
            calmar_ratio = (roi_percent / 100) / abs(max_drawdown) if max_drawdown < 0 else 999
        else:
            sharpe_ratio = sortino_ratio = calmar_ratio = 0
        
        return jsonify({
            'backtest': backtest_result,
            'price_data': price_data,
            'investment_metrics': {
                'starting_capital': starting_capital,
                'risk_per_trade': risk_per_trade if not is_etf else starting_capital,
                'total_invested': total_invested,
                'total_return': total_return,
                'final_capital': final_capital,
                'roi_percent': roi_percent,
                'equity_curve': equity_curve,
                'max_drawdown_percent': max_drawdown * 100,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'calmar_ratio': calmar_ratio,
                'is_etf': is_etf
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest-results')
def api_backtest_results():
    try:
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        cache_path = os.path.join(project_root, 'cache', 'backtest_results.json')
        
        with open(cache_path, 'r') as f:
            results = json.load(f)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy-results/<strategy_name>')
def api_strategy_results(strategy_name):
    try:
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        cache_path = os.path.join(project_root, 'cache', f'{strategy_name}_results.json')
        
        with open(cache_path, 'r') as f:
            results = json.load(f)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/install-strategy', methods=['POST'])
def api_install_strategy():
    try:
        data = request.get_json()
        strategy_name = data.get('strategy')
        
        if not strategy_name:
            return jsonify({'error': 'Strategy name required'}), 400
        
        # Import and run installation
        import sys
        import os
        sys.path.append('..')
        
        from install_strategies import install_strategy
        success = install_strategy(strategy_name)
        
        if success:
            return jsonify({'success': True, 'message': f'{strategy_name} installed successfully'})
        else:
            return jsonify({'success': False, 'error': 'Installation failed'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trading-signals')
def api_trading_signals():
    """Generate real trading signals from strategy results"""
    try:
        from signal_generator import generate_real_signals
        from datetime import datetime
        
        signals = generate_real_signals()
        
        return jsonify({
            'signals': signals,
            'total_count': len(signals),
            'generated_at': datetime.now().isoformat()
        })
        
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
            db_path = "../database/stock_data.db"
        elif data_type == 'forex':
            db_path = "../database/forex_data.db"
        elif data_type == 'crypto':
            db_path = "../database/stock_data.db"  # Crypto stored in stock db for now
        elif data_type == 'etfs':
            db_path = "../database/etf_data.db"
        else:  # commodities
            db_path = "../database/commodity_data.db"
        
        table_name = symbol.replace('/', '_')
        
        # Fetch new data
        if data_type == 'stocks':
            df = fetcher.fetch_daily_data(symbol)
        elif data_type == 'forex':
            from_symbol, to_symbol = symbol.split('/')
            df = fetcher.fetch_forex_data(from_symbol, to_symbol)
        elif data_type == 'crypto':
            df = fetcher.fetch_daily_data(symbol)  # Crypto uses same API as stocks
        elif data_type == 'etfs':
            df = fetcher.fetch_etf_data(symbol)
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
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        cache_path = os.path.join(project_root, 'cache', 'market_data.json')
        
        with open(cache_path, 'r') as f:
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
    app.run(debug=False, host='0.0.0.0', port=8080)