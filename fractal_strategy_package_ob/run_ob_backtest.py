# -*- coding: utf-8 -*-
"""
Run Fractal + Order Block filtered strategy.
Requires: fractal_strategy.py and order_blocks.py in the same package folder.
"""
import os, json, argparse
import pandas as pd
import matplotlib.pyplot as plt
from fractal_strategy import FractalParams, backtest, detect_fractals, plot_equity
from order_blocks import find_order_blocks


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def plot_price_with_ob(df, fr_df, ob_df, save_path=None):
    fig, ax = plt.subplots(1,1, figsize=(12,6))
    ax.plot(df.index, df['Close'], color='black', lw=1.2, label='Close')
    # Fractals
    ax.scatter(fr_df.index[fr_df['bearish_fractal']], df['High'][fr_df['bearish_fractal']],
               marker='^', color='red', s=40, label='Fractal High')
    ax.scatter(fr_df.index[fr_df['bullish_fractal']], df['Low'][fr_df['bullish_fractal']],
               marker='v', color='green', s=40, label='Fractal Low')
    # OB zones
    for ts in ob_df.index[ob_df['bullish_ob']]:
        low, high = ob_df.loc[ts, 'ob_low'], ob_df.loc[ts, 'ob_high']
        ax.axhspan(low, high, color='green', alpha=0.15)
    for ts in ob_df.index[ob_df['bearish_ob']]:
        low, high = ob_df.loc[ts, 'ob_low'], ob_df.loc[ts, 'ob_high']
        ax.axhspan(low, high, color='red', alpha=0.15)
    ax.legend()
    ax.set_title('Price with Fractals & Order Blocks')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        plt.close(fig)
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description='Fractal + Order Block Strategy Runner')
    parser.add_argument('--data', default='example_data.csv', help='CSV with Date,Open,High,Low,Close[,Volume]')
    parser.add_argument('--date-col', default='Date')
    parser.add_argument('--output-dir', default='outputs_ob')
    parser.add_argument('--impulse-bars', type=int, default=3)
    parser.add_argument('--min-body-ratio', type=float, default=0.3)
    parser.add_argument('--lookback', type=int, default=20)
    parser.add_argument('--filter-trades', action='store_true', help='Only take fractal breakouts interacting with OB zones')
    args = parser.parse_args()
    ensure_dir(args.output_dir)

    df = pd.read_csv(args.data)
    if args.date_col in df.columns:
        df[args.date_col] = pd.to_datetime(df[args.date_col])
        df = df.set_index(args.date_col).sort_index()
    else:
        raise ValueError('Date column not found')

    # Detect fractals for reference
    fr = detect_fractals(df, left_bars=2, right_bars=2)

    # Detect order blocks using fractal extremes as structure reference
    ob = find_order_blocks(df, fr['fractal_high'], fr['fractal_low'],
                           impulse_bars=args.impulse_bars,
                           min_body_ratio=args.min_body_ratio,
                           lookback=args.lookback)

    plot_price_with_ob(df, fr, ob, save_path=os.path.join(args.output_dir, 'price_fractals_ob.png'))

    # If filtering trades by OB interaction, we simply advise parameters and run standard backtest,
    # then post-filter the trades list to those near OB zones (illustrative).
    from fractal_strategy import backtest, FractalParams
    params = FractalParams(use_htf=True, htf_rule='W')
    perf = backtest(df, params)

    # Simple post-filter: keep trades where entry price lies within any OB zone +/- tolerance
    tol = df['Close'].std() * 0.02  # 2% of std as band
    keep = []
    for t in perf.trades:
        if t.entry_idx is None or t.entry_price is None:
            continue
        price = t.entry_price
        ts = t.entry_idx
        # Check nearby window around entry date for OB zones
        win = ob.loc[:ts].tail(5)  # last 5 days
        ok = False
        for idx, row in win.iterrows():
            if row['bullish_ob'] or row['bearish_ob']:
                low, high = row['ob_low'], row['ob_high']
                if low - tol <= price <= high + tol:
                    ok = True
                    break
        if (not args.filter_trades) or ok:
            keep.append(t)

    # Save outputs
    with open(os.path.join(args.output_dir, 'order_blocks_summary.json'), 'w') as f:
        json.dump({
            'num_bullish_ob': int(ob['bullish_ob'].sum()),
            'num_bearish_ob': int(ob['bearish_ob'].sum())
        }, f, indent=2)

    # Equity/Drawdown from unfiltered perf for simplicity
    perf.equity_curve.to_csv(os.path.join(args.output_dir, 'equity_curve.csv'))
    plot_equity(perf, title='Equity (Unfiltered) — OB Overlay',
                save_path=os.path.join(args.output_dir, 'equity_curve.png'))

    # Save filtered trades if requested
    import pandas as pd
    rows = []
    for t in keep:
        rows.append({
            'entry_ts': t.entry_idx.isoformat() if t.entry_idx is not None else None,
            'exit_ts': t.exit_idx.isoformat() if t.exit_idx is not None else None,
            'side': t.side,
            'qty': t.qty,
            'entry_price': t.entry_price,
            'pnl': t.pnl,
            'R_multiple': t.R_multiple
        })
    pd.DataFrame(rows).to_csv(os.path.join(args.output_dir, 'trades_filtered_by_ob.csv'), index=False)

    print('Done. Outputs at:', os.path.abspath(args.output_dir))

if __name__ == '__main__':
    main()
