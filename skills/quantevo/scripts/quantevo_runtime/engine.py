"""Single-asset, long-only SMA foundation; no arbitrary strategy execution."""
import csv
import hashlib
import io
import json
import math
import statistics
from datetime import datetime, timezone

ENGINE_VERSION = "sma-long-only-v0.1.0"


def crossover(closes, spec):
    """Signal from two completed SMA observations, shared with paper accounts."""
    if len(closes) < spec["slow"] + 1:
        return None
    def above(values):
        return math.fsum(values[-spec["fast"]:])/spec["fast"] > math.fsum(values[-spec["slow"]:])/spec["slow"]
    previous, current = above(closes[:-1]), above(closes)
    return "BUY" if current and not previous else "SELL" if previous and not current else None


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def validate_strategy(spec):
    fields = {"schema", "kind", "fast", "slow", "position_weight"}
    if not isinstance(spec, dict) or set(spec) != fields:
        raise ValueError("Strategy must contain exactly schema,kind,fast,slow,position_weight")
    if spec["schema"] != "quantevo.strategy.v1" or spec["kind"] != "sma_cross":
        raise ValueError("Foundation supports quantevo.strategy.v1 / sma_cross only")
    for key in ("fast", "slow"):
        if type(spec[key]) is not int or not 2 <= spec[key] <= 500:
            raise ValueError(f"{key} must be an integer in [2, 500]")
    if spec["fast"] >= spec["slow"]:
        raise ValueError("fast must be less than slow")
    weight = spec["position_weight"]
    if type(weight) not in (int, float) or not math.isfinite(weight) or not 0 < weight <= 1:
        raise ValueError("position_weight must be finite and in (0, 1]")
    return dict(spec)


def parse_bars(raw):
    if len(raw) > 15_000_000:
        raise ValueError("CSV exceeds 15 MB")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        raise ValueError("CSV requires timestamp,open,high,low,close,volume")
    bars, previous = [], None
    for line, row in enumerate(reader, 2):
        try:
            stamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("timestamp requires a timezone")
            stamp = stamp.astimezone(timezone.utc)
            if previous is not None and stamp <= previous:
                raise ValueError("timestamps must be unique and increasing")
            values = {k: float(row[k]) for k in required - {"timestamp"}}
            if not all(math.isfinite(v) for v in values.values()):
                raise ValueError("nonfinite OHLCV")
            if min(values[k] for k in ("open", "high", "low", "close")) <= 0 or values["volume"] < 0:
                raise ValueError("prices must be positive and volume nonnegative")
            if values["high"] < max(values["open"], values["close"]) or values["low"] > min(values["open"], values["close"]):
                raise ValueError("inconsistent OHLC")
            bars.append({"timestamp": stamp.isoformat().replace("+00:00", "Z"), **values})
            previous = stamp
        except (TypeError, KeyError, ValueError, AttributeError, OverflowError) as exc:
            raise ValueError(f"CSV row {line}: {exc}") from exc
    if len(bars) < 3:
        raise ValueError("At least three bars required")
    return bars


def number(value, name, lower, upper=None):
    if type(value) not in (float, int) or not math.isfinite(value) or value < lower or (upper is not None and value >= upper):
        raise ValueError(f"Invalid {name}")
    return float(value)


def backtest(bars, spec, initial_cash=10000, fee_bps=10, slippage_bps=5, periods_per_year=365):
    spec = validate_strategy(spec)
    initial_cash = number(initial_cash, "initial_cash", 0)
    periods_per_year = number(periods_per_year, "periods_per_year", 0)
    if not initial_cash or not periods_per_year:
        raise ValueError("initial_cash and periods_per_year must be positive")
    fee = number(fee_bps, "fee_bps", 0, 10000) / 10000
    slip = number(slippage_bps, "slippage_bps", 0, 10000) / 10000
    if len(bars) < spec["slow"] + 2:
        raise ValueError("Need at least slow + 2 bars")
    closes = [bar["close"] for bar in bars]
    cash, qty, previous, peak = initial_cash, 0.0, initial_cash, initial_cash
    returns, curve, fills = [], [], []
    fees = 0.0
    max_drawdown = 0.0
    for i, bar in enumerate(bars):
        if i >= spec["slow"] + 1:
            side = crossover(closes[max(0, i-spec["slow"]-1):i], spec)
            if (side == "BUY" and qty > 0) or (side == "SELL" and qty == 0):
                side = None
            if side:
                fill_price = bar["open"] * (1 + slip if side == "BUY" else 1 - slip)
                fill_qty = cash * spec["position_weight"] / (fill_price * (1+fee)) if side == "BUY" else qty
                gross = fill_price * fill_qty
                cost = gross * fee
                cash += -(gross+cost) if side == "BUY" else gross-cost
                qty = fill_qty if side == "BUY" else 0.0
                fees += cost
                fills.append({"timestamp": bar["timestamp"], "signal_timestamp": bars[i-1]["timestamp"],
                              "side": side, "qty": fill_qty, "price": fill_price, "fee": cost})
        equity = cash + qty * bar["close"]
        peak = max(peak, equity)
        drawdown = equity/peak - 1
        max_drawdown = min(max_drawdown, drawdown)
        if i > 0:
            returns.append(equity/previous - 1)
        curve.append({"timestamp": bar["timestamp"], "equity": equity, "cash": cash,
                      "qty": qty, "drawdown": drawdown})
        previous = equity
    stdev = statistics.stdev(returns) if len(returns) > 1 else 0.0
    sharpe = statistics.mean(returns)/stdev*math.sqrt(periods_per_year) if stdev else None
    return {"engine_version": ENGINE_VERSION, "strategy": spec,
            "evaluation": {"initial_cash": initial_cash, "fee_bps": fee_bps, "slippage_bps": slippage_bps,
                           "periods_per_year": periods_per_year, "risk_free_rate": 0,
                           "execution": "completed-bar crossover / next-bar open", "final_liquidation": False,
                           "metric_window": "entire supplied sample, including warmup"},
            "sample": {"bars": len(bars), "start": bars[0]["timestamp"], "end": bars[-1]["timestamp"]},
            "metrics": {"total_return": curve[-1]["equity"]/initial_cash-1,
                        "sharpe": sharpe, "max_drawdown": max_drawdown, "fees_paid": fees,
                        "fill_count": len(fills), "closed_trade_count": sum(f["side"] == "SELL" for f in fills)},
            "fills": fills, "equity": curve}


def evaluate_files(strategy_path, data_path, **settings):
    strategy_raw, data_raw = strategy_path.read_bytes(), data_path.read_bytes()
    spec = json.loads(strategy_raw)
    result = backtest(parse_bars(data_raw), spec, **settings)
    result["provenance"] = {"strategy_sha256": digest(strategy_raw), "data_sha256": digest(data_raw),
                            "engine_sha256": digest(__import__("pathlib").Path(__file__).read_bytes())}
    return result
