#!/usr/bin/env python3
"""Generate a clearly synthetic daily fixture; never fetch market data."""
import argparse
import csv
import math
from datetime import datetime, timedelta, timezone


def make_demo(stream):
    writer = csv.writer(stream)
    writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
    start, previous = datetime(2024, 1, 1, tzinfo=timezone.utc), 100.0
    for i in range(400):
        close = 100 + i*0.04 + 12*math.sin(i/12) + 3*math.sin(i/3)
        writer.writerow([(start+timedelta(days=i)).isoformat().replace("+00:00", "Z"),
                         previous, max(previous, close)*1.01, min(previous, close)*0.99, close, 1000])
        previous = close


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic daily OHLCV for installation checks")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with open(args.output, "x", encoding="utf-8", newline="") as stream:
        make_demo(stream)
    print(f"Synthetic example saved: {args.output}")
