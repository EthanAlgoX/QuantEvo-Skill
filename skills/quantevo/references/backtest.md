# Backtest contract — implemented foundation

Supported strategy: a JSON object with exactly these fields:

```json
{"schema":"quantevo.strategy.v1","kind":"sma_cross","fast":10,"slow":30,"position_weight":0.5}
```

`fast` and `slow` are integer SMA windows in [2, 500], with fast < slow.
`position_weight` is in (0, 1]. This is an SMA example, not the private
QuantEvo EMA strategy. No arbitrary Python code is imported or executed.

CSV columns: `timestamp,open,high,low,close,volume`. Timestamps include a
timezone and are unique and increasing; prices are finite and positive,
volume nonnegative, and OHLC consistent. At least `slow + 2` rows are needed.
The producer must supply completed bars; CSV timestamps alone cannot establish
whether a bar is complete, adjusted for corporate actions, or trustworthy.

```bash
python3 "$skill_dir/scripts/quantevo.py" backtest \
  --strategy /absolute/path/strategy.json \
  --data /absolute/path/bars.csv \
  --initial-cash 10000 --fee-bps 10 --slippage-bps 5 \
  --periods-per-year 365 \
  --output /absolute/path/new-result.json
```

Annualization is explicit: typically 252 for stock daily bars, 365 for crypto
daily bars, 8760 for crypto hourly bars. These are frequency assumptions,
not inferred exchange calendars. Irregular or missing bars require review.

Both SMA observations used for a crossover precede execution. A completed-bar
signal fills at the next supplied bar's open with adverse slippage and fees.
The model is single-asset, long-only, fractional inventory, without leverage,
funding, partial fills, order queues, stops, portfolio risk controls or corporate
actions. Position weight sets entry spend; it does not continuously rebalance.

Metrics cover the entire supplied sample, including initial warmup cash bars.
Zero return variance gives `sharpe: null`. Cash plus inventory marked at the
last close is final equity; the engine does not liquidate at the end. Fill
count is different from closed-trade count. Drawdown is reported as a negative
fraction; the evaluator reports it and does not enforce a drawdown ceiling.

Output includes source-byte SHA256 hashes for the CSV, strategy and engine,
settings, sample bounds, fills and equity. Hashes establish input identity, not
data correctness. Existing output files are never overwritten.
