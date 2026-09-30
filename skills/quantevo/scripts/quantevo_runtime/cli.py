"""JSON CLI for host-agent research and persistent paper monitoring."""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from . import paper
from .engine import ENGINE_VERSION, evaluate_files


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), flush=True)


def background(home, operation, extra):
    home = Path(home).expanduser().resolve(); home.mkdir(parents=True, exist_ok=True)
    filename = '.worker.lock' if operation == 'run' else '.server.lock'
    with paper.worker_lock(home, filename):
        pass
    package_root = Path(__file__).resolve().parents[1]
    bootstrap = 'import sys;sys.path.insert(0,sys.argv.pop(1));from quantevo_runtime.cli import main;main()'
    command = [sys.executable, '-c', bootstrap, str(package_root)]
    command += ['paper', 'run'] if operation == 'run' else ['serve']
    command += ['--home', str(home)] + extra
    log = home/('worker.log' if operation == 'run' else 'server.log')
    with log.open('ab') as stream:
        options = {'start_new_session': True} if os.name != 'nt' else {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS}
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stream, stderr=stream, cwd=home, **options)
    key = 'worker' if operation == 'run' else 'server'
    for _ in range(50):
        if child.poll() is not None:
            raise ValueError(f'{key} failed to start; inspect {log}')
        with paper.database(home) as con:
            info = paper.get_meta(con, key, {})
        if info.get('pid') == child.pid and info.get('running'):
            return {**info, 'background': True, 'home': str(home), 'log': str(log)}
        time.sleep(.1)
    child.terminate()
    child.wait(timeout=5)
    raise ValueError(f'{key} startup timed out; inspect {log}')


def main():
    parser = argparse.ArgumentParser(description='QuantEvo Skill')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('doctor', help='Report implemented capabilities')
    run = commands.add_parser('backtest', help='Backtest a JSON strategy on an OHLCV CSV')
    run.add_argument('--strategy', type=Path, required=True)
    run.add_argument('--data', type=Path, required=True)
    run.add_argument('--output', type=Path)
    run.add_argument('--initial-cash', type=float, default=10000)
    run.add_argument('--fee-bps', type=float, default=10)
    run.add_argument('--slippage-bps', type=float, default=5)
    run.add_argument('--periods-per-year', type=float, required=True)
    accounts = commands.add_parser('paper', help='Create, run and inspect CSV paper accounts')
    operations = accounts.add_subparsers(dest='operation', required=True)
    for operation in ['create', 'run', 'tick', 'status', 'watch', 'pause', 'resume', 'stop-worker']:
        item = operations.add_parser(operation)
        item.add_argument('--home', type=Path, default=Path(os.environ.get('QUANTEVO_HOME', '.quantevo')))
        if operation == 'create':
            item.add_argument('--strategy', type=Path, required=True)
            item.add_argument('--feed', type=Path, required=True)
            item.add_argument('--name', required=True)
            item.add_argument('--source-label', default='external CSV')
            item.add_argument('--interval-seconds', type=float, required=True)
            item.add_argument('--initial-cash', type=float, default=10000)
            item.add_argument('--fee-bps', type=float, default=10)
            item.add_argument('--slippage-bps', type=float, default=5)
        if operation in ['status', 'watch']:
            item.add_argument('--id')
        if operation in ['pause', 'resume']:
            item.add_argument('--id', required=True)
        if operation == 'run':
            item.add_argument('--poll-seconds', type=float, default=1)
            item.add_argument('--background', action='store_true')
        if operation == 'watch':
            item.add_argument('--interval', type=float, default=2)
            item.add_argument('--count', type=int, default=3, help='Bounded snapshots; 0 continues until interrupted')
    server = commands.add_parser('serve', help='Serve a loopback-only monitoring website')
    server.add_argument('--home', type=Path, default=Path(os.environ.get('QUANTEVO_HOME', '.quantevo')))
    server.add_argument('--port', type=int, default=8765)
    server.add_argument('--background', action='store_true')
    server.add_argument('--stop', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'doctor':
            value = {'status': 'paper-ready', 'version': '0.1.0', 'engine_version': ENGINE_VERSION,
                     'python': sys.version.split()[0], 'available': ['sma_cross_csv_backtest', 'csv_forward_paper_accounts', 'background_worker', 'local_dashboard', 'json_monitoring'],
                     'planned': ['persistent_research_trials', 'final_evaluation', 'market_api_feeds'],
                     'llm_api_required': False, 'order_placement': False}
        elif args.command == 'backtest':
            value = evaluate_files(args.strategy, args.data, initial_cash=args.initial_cash,
                                   fee_bps=args.fee_bps, slippage_bps=args.slippage_bps,
                                   periods_per_year=args.periods_per_year)
            if args.output:
                with args.output.open('x', encoding='utf-8') as stream:
                    stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
                value = {'output': str(args.output.resolve()), 'metrics': value['metrics']}
        elif args.command == 'serve':
            from . import monitor
            if args.stop:
                value = monitor.stop(args.home)
            elif args.background:
                value = background(args.home, 'serve', ['--port', str(args.port)])
            else:
                monitor.serve(args.home, args.port); return
        elif args.operation == 'create':
            value = paper.create(args.home, args.strategy, args.feed, args.name, args.interval_seconds,
                                  args.initial_cash, args.fee_bps, args.slippage_bps, args.source_label)
        elif args.operation == 'tick':
            value = paper.tick(args.home)
        elif args.operation == 'status':
            value = paper.status(args.home, args.id)
        elif args.operation in ['pause', 'resume']:
            value = paper.control(args.home, args.id, args.operation)
        elif args.operation == 'stop-worker':
            value = paper.request_stop(args.home)
        elif args.operation == 'run':
            if args.background:
                value = background(args.home, 'run', ['--poll-seconds', str(args.poll_seconds)])
            else:
                paper.run(args.home, args.poll_seconds); return
        elif args.operation == 'watch':
            if args.interval < .1 or args.count < 0:
                raise ValueError('interval must be >= .1 and count >= 0')
            index = 0
            while args.count == 0 or index < args.count:
                emit(paper.status(args.home, args.id)); index += 1
                if args.count == 0 or index < args.count:
                    time.sleep(args.interval)
            return
        emit(value)
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()
