"""Machine-readable CLI used by either host agent."""
import argparse
import json
import sys
from pathlib import Path

from .engine import ENGINE_VERSION, evaluate_files


def main():
    parser = argparse.ArgumentParser(description="QuantEvo Skill foundation")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Report available and planned capabilities")
    run = commands.add_parser("backtest", help="Evaluate a single-asset SMA strategy on an OHLCV CSV")
    run.add_argument("--strategy", type=Path, required=True)
    run.add_argument("--data", type=Path, required=True)
    run.add_argument("--output", type=Path)
    run.add_argument("--initial-cash", type=float, default=10000)
    run.add_argument("--fee-bps", type=float, default=10)
    run.add_argument("--slippage-bps", type=float, default=5)
    run.add_argument("--periods-per-year", type=float, required=True,
                     help="Explicit annualization: e.g. 252 stock daily / 365 crypto daily / 8760 crypto hourly")
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            value = {"status": "foundation", "engine_version": ENGINE_VERSION,
                     "python": sys.version.split()[0], "available": ["sma_cross_csv_backtest"],
                     "planned": ["persistent_research_trials", "final_evaluation", "forward_paper_worker", "local_dashboard"],
                     "llm_api_required": False, "order_placement": False}
        else:
            value = evaluate_files(args.strategy, args.data, initial_cash=args.initial_cash,
                                   fee_bps=args.fee_bps, slippage_bps=args.slippage_bps,
                                   periods_per_year=args.periods_per_year)
        content = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.command == "backtest" and args.output:
            # Exclusive creation prevents accidental replacement of an old experiment.
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(content)
            print(json.dumps({"output": str(args.output.resolve()), "metrics": value["metrics"]}, ensure_ascii=False))
        else:
            print(content, end="")
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
