#!/usr/bin/env python3
"""Append synthetic completed OHLCV bars for paper workflow checks only."""
import argparse
import csv
import math
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


def row(index, stamp, previous):
    close = 100+10*math.sin(index/4)+2*math.sin(index/2)
    return [stamp.isoformat().replace('+00:00', 'Z'), previous,
            max(previous, close)*1.01, min(previous, close)*.99, close, 1000]


def main():
    parser = argparse.ArgumentParser(description='Synthetic feed for paper workflow testing; not market data')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--append', action='store_true')
    parser.add_argument('--updates', type=int, default=120)
    parser.add_argument('--interval-seconds', type=float, default=1)
    args = parser.parse_args()
    if args.updates < 0 or not math.isfinite(args.interval_seconds) or args.interval_seconds <= 0:
        parser.error('updates must be >= 0 and interval-seconds > 0')
    if args.append:
        with args.output.open() as stream:
            rows = list(csv.DictReader(stream))
        if not rows:
            parser.error('Existing feed has no rows')
        index, previous = len(rows), float(rows[-1]['close'])
        mode = 'a'
    else:
        index, previous, mode = 0, 100.0, 'x'
    with args.output.open(mode, newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        if not args.append:
            writer.writerow(['timestamp','open','high','low','close','volume'])
            now = datetime.now(timezone.utc)
            for index in range(80):
                values = row(index, now-timedelta(seconds=(80-index)*args.interval_seconds), previous)
                writer.writerow(values); previous = values[4]
            index = 80; stream.flush()
        for _ in range(args.updates):
            time.sleep(args.interval_seconds)
            values = row(index, datetime.now(timezone.utc), previous)
            writer.writerow(values); stream.flush()
            previous = values[4]; index += 1
    print(f'Synthetic feed completed: {args.output}', flush=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
