import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"skills/quantevo/scripts"))
from quantevo_runtime.engine import backtest, parse_bars, validate_strategy


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/"scripts"/f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT/"examples/sma-cross.json").read_text())
        stream = io.StringIO()
        load_script("make_demo").make_demo(stream)
        self.raw = stream.getvalue().encode()
        self.bars = parse_bars(self.raw)

    def test_fills_use_previous_completed_signal(self):
        result = backtest(self.bars, self.spec)
        self.assertGreater(len(result["fills"]), 0)
        for fill in result["fills"]:
            i = next(i for i, bar in enumerate(self.bars) if bar["timestamp"] == fill["timestamp"])
            self.assertEqual(fill["signal_timestamp"], self.bars[i-1]["timestamp"])
            self.assertAlmostEqual(fill["price"], self.bars[i]["open"]*(1.0005 if fill["side"] == "BUY" else .9995))

    def test_current_and_future_closes_do_not_change_current_fill(self):
        baseline = backtest(self.bars, self.spec)
        fill = baseline["fills"][0]
        index = next(i for i, bar in enumerate(self.bars) if bar["timestamp"] == fill["timestamp"])
        changed = [dict(bar) for bar in self.bars]
        for bar in changed[index:]:
            bar["close"] *= 5
            bar["high"] = max(bar["high"], bar["close"])
        result = backtest(changed, self.spec)
        self.assertEqual(result["fills"][0], fill)

    def test_ledger_reconciles_every_equity_point(self):
        result = backtest(self.bars, self.spec, fee_bps=20, slippage_bps=10)
        by_time = {fill["timestamp"]: fill for fill in result["fills"]}
        cash, qty, fees = 10000., 0., 0.
        for bar, point in zip(self.bars, result["equity"]):
            fill = by_time.get(bar["timestamp"])
            if fill:
                gross = fill["qty"]*fill["price"]
                self.assertAlmostEqual(fill["fee"], gross*.002)
                fees += fill["fee"]
                if fill["side"] == "BUY":
                    cash -= gross+fill["fee"]
                    qty += fill["qty"]
                else:
                    cash += gross-fill["fee"]
                    qty -= fill["qty"]
            self.assertAlmostEqual(point["cash"], cash)
            self.assertAlmostEqual(point["qty"], qty)
            self.assertAlmostEqual(point["equity"], cash+qty*bar["close"])
        self.assertAlmostEqual(result["metrics"]["fees_paid"], fees)

    def test_invalid_strategy_and_data_are_rejected(self):
        for changes in ({"fast": True}, {"slow": 5}, {"position_weight": float("nan")}, {"kind": "python"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_strategy({**self.spec, **changes})
        lines = self.raw.decode().splitlines()
        with self.assertRaises(ValueError):
            parse_bars((lines[0]+"\n"+lines[1]+"\n"+lines[1]+"\n").encode())
        with self.assertRaises(ValueError):
            parse_bars(self.raw.replace(b"T00:00:00Z", b"T00:00:00"))

    def test_no_trades_have_undefined_sharpe(self):
        flat = [{**bar, "open": 100, "close": 100, "high": 101, "low": 99} for bar in self.bars]
        result = backtest(flat, self.spec)
        self.assertEqual(result["metrics"]["fill_count"], 0)
        self.assertIsNone(result["metrics"]["sharpe"])
        self.assertEqual(result["metrics"]["total_return"], 0)

    def test_installed_skill_runs_outside_checkout_and_preserves_existing_install(self):
        installer = load_script("install_skill")
        with tempfile.TemporaryDirectory() as temp:
            target = installer.install("codex", Path(temp)/"skills")
            result = subprocess.run([sys.executable, str(target/"scripts/quantevo.py"), "doctor"],
                                    cwd=temp, capture_output=True, text=True, check=True)
            self.assertIn("sma_cross_csv_backtest", json.loads(result.stdout)["available"])
            with self.assertRaises(FileExistsError):
                installer.install("claude", Path(temp)/"skills")
            self.assertTrue((target/"SKILL.md").exists())

    def test_cli_backtest_records_provenance_and_cannot_overwrite_result(self):
        with tempfile.TemporaryDirectory() as temp:
            data, output = Path(temp)/"bars.csv", Path(temp)/"result.json"
            data.write_bytes(self.raw)
            command = [sys.executable, str(ROOT/"skills/quantevo/scripts/quantevo.py"), "backtest",
                       "--data", str(data), "--strategy", str(ROOT/"examples/sma-cross.json"),
                       "--periods-per-year", "365", "--output", str(output)]
            subprocess.run(command, capture_output=True, text=True, check=True, cwd=temp)
            before = output.read_bytes()
            result = json.loads(before)
            self.assertEqual(len(result["provenance"]["data_sha256"]), 64)
            retry = subprocess.run(command, capture_output=True, text=True, cwd=temp)
            self.assertEqual(retry.returncode, 2)
            self.assertEqual(output.read_bytes(), before)
            self.assertIn("error", json.loads(retry.stderr))


if __name__ == "__main__":
    unittest.main()
