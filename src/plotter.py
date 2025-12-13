import plotly.graph_objects as go
import plotly.offline as pyo

class StockPlotter:
    @staticmethod
    def plot_interactive(df, filename):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Close Price'))
        fig.update_layout(title='Interactive Stock Price', xaxis_title='Date', yaxis_title='Price')
        pyo.plot(fig, filename=filename, auto_open=False)
    
    @staticmethod
    def plot_interactive_candlestick(df, filename):
        fig = go.Figure(data=go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        ))
        fig.update_layout(title='Interactive Candlestick Chart')
        pyo.plot(fig, filename=filename, auto_open=False)