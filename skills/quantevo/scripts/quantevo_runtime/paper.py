"""Persistent bar-based CSV simulator. Never places exchange orders."""
import json
import math
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .engine import crossover, digest, number, parse_bars, validate_strategy

PAPER_VERSION = 'csv-forward-v0.1.0'


def utcnow():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def epoch(stamp):
    return datetime.fromisoformat(stamp.replace('Z', '+00:00')).timestamp()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def prefix_hash(bars):
    return digest(encoded(bars).encode())


@contextmanager
def database(home):
    home = Path(home).expanduser().resolve()
    home.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(home/'paper.sqlite3'), timeout=10)
    connection.execute('PRAGMA journal_mode=WAL')
    connection.execute('CREATE TABLE IF NOT EXISTS accounts (id TEXT PRIMARY KEY, state TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
    connection.commit()
    try:
        yield connection
    finally:
        connection.close()


def get_meta(con, key, default=None):
    row = con.execute('SELECT value FROM metadata WHERE key=?', (key,)).fetchone()
    return json.loads(row[0]) if row else default


def set_meta(con, key, value):
    con.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)', (key, encoded(value)))


def create(home, strategy, feed, name, interval_seconds, initial_cash=10000,
           fee_bps=10, slippage_bps=5, source_label='external CSV', now=None):
    now = now or utcnow()
    raw = Path(strategy).read_bytes()
    spec = validate_strategy(json.loads(raw))
    feed = Path(feed).expanduser().resolve()
    bars = parse_bars(feed.read_bytes())
    if len(bars) < spec['slow'] + 2:
        raise ValueError('Need slow + 2 warmup bars')
    if epoch(bars[-1]['timestamp']) > epoch(now):
        raise ValueError('Initial feed includes future timestamps; provide completed bars')
    settings = {'initial_cash': number(initial_cash, 'initial_cash', 0),
                'fee_bps': number(fee_bps, 'fee_bps', 0, 10000),
                'slippage_bps': number(slippage_bps, 'slippage_bps', 0, 10000),
                'interval_seconds': number(interval_seconds, 'interval_seconds', 0)}
    if not settings['initial_cash'] or not settings['interval_seconds']:
        raise ValueError('Cash and interval_seconds must be positive')
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 120:
        raise ValueError('Account name must be 1–120 characters')
    account_id = uuid.uuid4().hex[:12]
    state = {'id': account_id, 'name': name.strip(), 'mode': 'CSV_FORWARD',
             'source_label': source_label, 'feed': str(feed), 'settings': settings,
             'strategy': spec, 'strategy_sha256': digest(raw), 'paper_version': PAPER_VERSION,
             'signal_engine_sha256': digest(Path(__file__).with_name('engine.py').read_bytes()),
             'paper_engine_sha256': digest(Path(__file__).read_bytes()),
             'status': 'running', 'created_at': now, 'last_poll': None, 'last_error': None,
             'consumed': len(bars), 'prefix_sha256': prefix_hash(bars),
             'history': bars[-spec['slow']-1:], 'last_bar': bars[-1]['timestamp'],
             'cash': settings['initial_cash'], 'qty': 0.0, 'fees_paid': 0.0,
             'equity': settings['initial_cash'], 'peak': settings['initial_cash'],
             'max_drawdown': 0.0, 'fills': [], 'decisions': [],
             'curve': [{'timestamp': now, 'equity': settings['initial_cash'], 'cash': settings['initial_cash'], 'qty': 0.0}]}
    with database(home) as con:
        con.execute('INSERT INTO accounts VALUES (?,?)', (account_id, encoded(state)))
        con.commit()
    return summarize(state, now)


def advance(state, now):
    if state['status'] != 'running':
        return state
    state['last_poll'] = now
    expected = digest(Path(__file__).with_name('engine.py').read_bytes())
    if state['signal_engine_sha256'] != expected or state['paper_engine_sha256'] != digest(Path(__file__).read_bytes()):
        raise ValueError('Account engine has changed; restore the pinned runtime or create a new account')
    bars = parse_bars(Path(state['feed']).read_bytes())
    count = state['consumed']
    if len(bars) < count or prefix_hash(bars[:count]) != state['prefix_sha256']:
        raise ValueError('Consumed feed history was rewritten or truncated; account stopped')
    spec, settings = state['strategy'], state['settings']
    fee, slip = settings['fee_bps']/10000, settings['slippage_bps']/10000
    for bar in bars[count:]:
        if epoch(bar['timestamp']) > epoch(now):
            break  # Future rows are not consumed; producer must supply completed bars.
        history = state['history']
        if epoch(bar['timestamp']) > epoch(state['created_at']):
            side = crossover([row['close'] for row in history], spec)
            if (side == 'BUY' and state['qty'] > 0) or (side == 'SELL' and state['qty'] == 0):
                side = None
            if side:
                price = bar['open']*(1+slip if side == 'BUY' else 1-slip)
                qty = state['cash']*spec['position_weight']/(price*(1+fee)) if side == 'BUY' else state['qty']
                gross, cost = qty*price, qty*price*fee
                state['cash'] += -(gross+cost) if side == 'BUY' else gross-cost
                state['qty'] = qty if side == 'BUY' else 0.0
                state['fees_paid'] += cost
                state['fills'].append({'timestamp': bar['timestamp'], 'observed_at': now,
                                       'signal_timestamp': history[-1]['timestamp'],
                                       'side': side, 'qty': qty, 'price': price, 'fee': cost,
                                       'execution': 'modeled next-bar open, observed after CSV delivery'})
            state['equity'] = state['cash']+state['qty']*bar['close']
            state['peak'] = max(state['peak'], state['equity'])
            state['max_drawdown'] = min(state['max_drawdown'], state['equity']/state['peak']-1)
            state['curve'].append({'timestamp': bar['timestamp'], 'observed_at': now,
                                   'equity': state['equity'], 'cash': state['cash'], 'qty': state['qty']})
            state['decisions'].append({'timestamp': bar['timestamp'], 'observed_at': now,
                                       'action': side or 'HOLD', 'close': bar['close']})
        state['history'] = (history+[bar])[-spec['slow']-1:]
        state['consumed'] += 1
        state['last_bar'] = bar['timestamp']
    state['prefix_sha256'] = prefix_hash(bars[:state['consumed']])
    state['last_error'] = None
    return state


def tick(home, now=None):
    now = now or utcnow()
    with database(home) as con:
        con.execute('BEGIN IMMEDIATE')
        rows = con.execute('SELECT id,state FROM accounts').fetchall()
        for account_id, raw in rows:
            state = json.loads(raw)
            try:
                # Work on a copy so a mid-poll error cannot partially advance a ledger.
                updated = advance(json.loads(raw), now)
                state = updated
            except (OSError, ValueError, TypeError, OverflowError) as exc:
                state['last_error'], state['last_poll'] = str(exc), now
                # Missing or partially-written feeds can recover. Changed history cannot.
                if 'rewritten or truncated' in str(exc) or 'engine has changed' in str(exc):
                    state['status'] = 'failed'
            con.execute('UPDATE accounts SET state=? WHERE id=?', (encoded(state), account_id))
        con.commit()
    return status(home, now=now)


def summarize(state, now):
    age = max(0, epoch(now)-epoch(state['last_bar']))
    health = 'error' if state['last_error'] else 'stale' if age > max(3*state['settings']['interval_seconds'], 5) else 'waiting' if len(state['curve']) == 1 else 'fresh'
    return {key: state[key] for key in ('id','name','mode','source_label','status','created_at','last_poll','last_bar','last_error','strategy','strategy_sha256','settings','cash','qty','equity','fees_paid','max_drawdown')} | {
        'data_health': health, 'data_age_seconds': age, 'total_return': state['equity']/state['settings']['initial_cash']-1,
        'fill_count': len(state['fills']), 'observation_count': len(state['curve'])-1}


def status(home, account_id=None, now=None, limit=300):
    now = now or utcnow()
    with database(home) as con:
        worker = get_meta(con, 'worker', {})
        rows = con.execute('SELECT id,state FROM accounts ORDER BY rowid').fetchall()
    heartbeat = worker.get('heartbeat')
    worker = {**worker, 'healthy': bool(worker.get('running') and heartbeat and epoch(now)-epoch(heartbeat) < max(10, worker.get('poll_seconds', 1)*3))}
    accounts = []
    for key, raw in rows:
        if account_id and account_id != key:
            continue
        state = json.loads(raw)
        item = summarize(state, now)
        if account_id:
            item.update({'curve': state['curve'][-limit:], 'fills': state['fills'][-limit:], 'decisions': state['decisions'][-limit:]})
        accounts.append(item)
    if account_id and not accounts:
        raise ValueError('Account not found')
    return {'as_of': now, 'worker': worker, 'accounts': accounts}


def control(home, account_id, action):
    if action not in ('pause', 'resume'):
        raise ValueError('Expected pause or resume')
    with database(home) as con:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT state FROM accounts WHERE id=?', (account_id,)).fetchone()
        if not row:
            raise ValueError('Account not found')
        state = json.loads(row[0])
        if state['status'] == 'failed':
            raise ValueError('Failed account cannot resume after changed history; create a new account')
        state['status'] = 'paused' if action == 'pause' else 'running'
        con.execute('UPDATE accounts SET state=? WHERE id=?', (encoded(state), account_id))
        con.commit()
    return status(home, account_id)


@contextmanager
def worker_lock(home, filename='.worker.lock'):
    path = Path(home).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    with (path/filename).open('a+b') as stream:
        try:
            if os.name == 'nt':
                import msvcrt
                stream.write(b'0'); stream.flush(); stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError(f'A service already owns {filename} in this data directory') from exc
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0); msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


def request_stop(home):
    with database(home) as con:
        set_meta(con, 'stop_worker', True); con.commit()
    return {'stop_requested': True}


def run(home, poll_seconds=1):
    poll_seconds = number(poll_seconds, 'poll_seconds', .1, 3600)
    with worker_lock(home):
        with database(home) as con:
            set_meta(con, 'stop_worker', False); con.commit()
        try:
            while True:
                with database(home) as con:
                    if get_meta(con, 'stop_worker', False):
                        break
                    set_meta(con, 'worker', {'pid': os.getpid(), 'running': True, 'heartbeat': utcnow(), 'poll_seconds': poll_seconds})
                    con.commit()
                tick(home)
                time.sleep(poll_seconds)
        finally:
            with database(home) as con:
                set_meta(con, 'worker', {'pid': os.getpid(), 'running': False, 'heartbeat': utcnow(), 'poll_seconds': poll_seconds})
                con.commit()
