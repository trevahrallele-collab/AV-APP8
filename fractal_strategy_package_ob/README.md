

## Fractals + Order Blocks (OB) Integration

This package includes a pragmatic **Order Block** detector (`order_blocks.py`) and a runner `run_ob_backtest.py`.

### Usage
```bash
python run_ob_backtest.py --data example_data.csv --date-col Date --output-dir outputs_ob --filter-trades
```
- Produces `price_fractals_ob.png` with fractals & OB zones overlaid.
- If `--filter-trades` is set, it saves `trades_filtered_by_ob.csv` keeping entries that occur within/near an OB zone.

### Notes
- OB detection here uses a simple impulse + structure-break heuristic tied to **fractal extremes**.
- Tune `--impulse-bars`, `--min-body-ratio`, and `--lookback` per instrument/timeframe.
