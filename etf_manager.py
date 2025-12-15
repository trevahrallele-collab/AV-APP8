#!/usr/bin/env python3
"""
ETF Manager - Manage ETF data and operations
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime

class ETFManager:
    def __init__(self, db_path='database/etf_data.db'):
        self.db_path = db_path
    
    def get_etf_list(self):
        """Get list of all available ETFs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT DISTINCT symbol FROM etf_prices ORDER BY symbol")
        symbols = [row[0] for row in cursor.fetchall()]
        conn.close()
        return symbols
    
    def get_etf_data(self, symbol):
        """Get price data for specific ETF"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM etf_prices WHERE symbol = ? ORDER BY date",
            conn, params=(symbol,)
        )
        conn.close()
        
        if df.empty:
            return None
        
        return {
            'symbol': symbol,
            'dates': df['date'].tolist(),
            'prices': {
                'open': df['open'].tolist(),
                'high': df['high'].tolist(),
                'low': df['low'].tolist(),
                'close': df['close'].tolist(),
                'volume': df['volume'].tolist()
            }
        }
    
    def get_etf_fundamentals(self, symbol):
        """Get fundamentals for specific ETF"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM etf_fundamentals WHERE symbol = ?", (symbol,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    
    def add_etf_routes(self, app):
        """Add ETF routes to Flask app"""
        etf_symbols = self.get_etf_list()
        
        for symbol in etf_symbols:
            route_name = f'/{symbol.lower()}'
            
            def create_route_handler(etf_symbol):
                def route_handler():
                    from flask import render_template
                    return render_template('backtest_detail.html', 
                                         data_type='etfs', 
                                         symbol=etf_symbol)
                return route_handler
            
            app.add_url_rule(
                route_name,
                f'{symbol.lower()}_backtest',
                create_route_handler(symbol)
            )
    
    def update_web_app_routes(self, web_app_path='src/web_app.py'):
        """Update web app with ETF routes"""
        etf_symbols = self.get_etf_list()
        
        routes_code = "\n# ETF Routes (Auto-generated)\n"
        for symbol in etf_symbols:
            routes_code += f"""
@app.route('/{symbol.lower()}')
def {symbol.lower()}_backtest():
    return render_template('backtest_detail.html', data_type='etfs', symbol='{symbol}')
"""
        
        # Read current web app
        with open(web_app_path, 'r') as f:
            content = f.read()
        
        # Find insertion point (before the generic backtest route)
        insertion_point = content.find('@app.route(\'/backtest/<data_type>/<symbol>\')')
        
        if insertion_point != -1:
            new_content = content[:insertion_point] + routes_code + "\n" + content[insertion_point:]
            
            with open(web_app_path, 'w') as f:
                f.write(new_content)
            
            print(f"Added {len(etf_symbols)} ETF routes to web app")
        else:
            print("Could not find insertion point in web app")
    
    def update_frontend_routing(self, template_path='templates/backtest_results.html'):
        """Update frontend with ETF routing logic"""
        etf_symbols = self.get_etf_list()
        etf_routes = [symbol.lower() for symbol in etf_symbols]
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Update ETF routes array
        old_pattern = "// Use generic backtest route for all symbols"
        new_routing_logic = f"""// Check if this is an ETF with a specific route
            const etfRoutes = {etf_routes};
            const symbolLower = symbol.toLowerCase();
            
            // Check if symbol is an ETF regardless of dataType
            if (etfRoutes.includes(symbolLower)) {{
                window.location.href = `/${{symbolLower}}?capital=${{startingCapital}}&risk=${{riskPerTrade}}`;
            }} else {{
                // For all other symbols, use the generic backtest route"""
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_routing_logic)
            
            with open(template_path, 'w') as f:
                f.write(content)
            
            print(f"Updated frontend routing with {len(etf_symbols)} ETF routes")
        else:
            print("Could not find routing pattern in template")

def main():
    """Main function to update ETF routes"""
    manager = ETFManager()
    
    print("Available ETFs:", manager.get_etf_list())
    
    # Update web app routes
    manager.update_web_app_routes()
    
    # Update frontend routing
    manager.update_frontend_routing()
    
    print("ETF management completed!")

if __name__ == "__main__":
    main()