import csv
import io
import json
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/quantevo/scripts'))
from quantevo_runtime import paper
from quantevo_runtime.engine import backtest, parse_bars
from test_foundation import load_script


class PaperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home, self.feed = self.root/'home', self.root/'feed.csv'
        self.spec = json.loads((ROOT/'examples/sma-cross.json').read_text())
        self.strategy = self.root/'strategy.json'
        self.strategy.write_text(json.dumps(self.spec))
        stream = io.StringIO(); load_script('make_demo').make_demo(stream)
        self.bars = parse_bars(stream.getvalue().encode())
        self.write_feed(self.bars[:32])
        self.created = (datetime.fromisoformat(self.bars[31]['timestamp'].replace('Z','+00:00'))+timedelta(seconds=1)).isoformat()
        self.now = self.bars[-1]['timestamp']
        self.account = paper.create(self.home, self.strategy, self.feed, 'Baseline', 86400, now=self.created)
        self.id = self.account['id']

    def write_feed(self, bars):
        with self.feed.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=['timestamp','open','high','low','close','volume'])
            writer.writeheader(); writer.writerows(bars)

    def detail(self):
        return paper.status(self.home, self.id, now=self.now, limit=1000)['accounts'][0]

    def test_warmup_is_not_account_profit_and_stale_data_adds_nothing(self):
        state = self.detail()
        self.assertEqual(state['equity'], 10000)
        self.assertEqual(state['total_return'], 0)
        self.assertEqual(state['fill_count'], 0)
        self.assertEqual(state['observation_count'], 0)
        self.assertEqual(state['data_health'], 'stale')
        paper.tick(self.home, now=self.now)
        self.assertEqual(self.detail()['curve'], state['curve'])

    def test_new_bars_match_backtest_fills_and_survive_restart_without_duplicates(self):
        self.write_feed(self.bars)
        paper.tick(self.home, now=self.now)
        actual = self.detail()
        expected = backtest(self.bars, self.spec)
        self.assertAlmostEqual(actual['equity'], expected['equity'][-1]['equity'])
        self.assertAlmostEqual(actual['fees_paid'], expected['metrics']['fees_paid'])
        self.assertEqual(actual['fill_count'], len(expected['fills']))
        for left, right in zip(actual['fills'], expected['fills']):
            for key in right:
                self.assertEqual(left[key], right[key])
        paper.tick(self.home, now=self.now)  # A fresh connection models process restart.
        self.assertEqual(self.detail()['fills'], actual['fills'])
        self.assertEqual(self.detail()['curve'], actual['curve'])

    def test_rewritten_consumed_history_permanently_fails_account(self):
        changed = [dict(row) for row in self.bars[:32]]
        changed[0]['volume'] += 1
        self.write_feed(changed)
        paper.tick(self.home, now=self.now)
        self.assertEqual(self.detail()['status'], 'failed')
        self.assertEqual(self.detail()['equity'], 10000)
        with self.assertRaises(ValueError):
            paper.control(self.home, self.id, 'resume')

    def test_future_rows_wait_and_pause_resume_replays_unconsumed_completed_bars(self):
        self.write_feed(self.bars)
        paper.tick(self.home, now=self.created)
        self.assertEqual(self.detail()['observation_count'], 0)
        paper.control(self.home, self.id, 'pause')
        paper.tick(self.home, now=self.now)
        self.assertEqual(self.detail()['observation_count'], 0)
        paper.control(self.home, self.id, 'resume')
        paper.tick(self.home, now=self.now)
        self.assertEqual(self.detail()['observation_count'], len(self.bars)-32)

    def test_missing_feed_recovers_without_losing_state_and_versions_stay_pinned(self):
        self.feed.rename(self.root/'saved.csv')
        paper.tick(self.home, now=self.now)
        self.assertEqual(self.detail()['data_health'], 'error')
        self.assertEqual(self.detail()['status'], 'running')
        (self.root/'saved.csv').rename(self.feed)
        self.strategy.write_text(json.dumps({**self.spec, 'position_weight': .1}))
        paper.tick(self.home, now=self.now)
        self.assertIsNone(self.detail()['last_error'])
        self.assertEqual(self.detail()['strategy'], self.spec)

    def test_separate_accounts_are_isolated(self):
        self.strategy.write_text(json.dumps({**self.spec, 'position_weight': .1}))
        second = paper.create(self.home, self.strategy, self.feed, 'Low weight', 86400, now=self.created)
        self.write_feed(self.bars)
        paper.tick(self.home, now=self.now)
        items = paper.status(self.home, now=self.now)['accounts']
        self.assertEqual(len(items), 2)
        self.assertNotEqual(items[0]['strategy_sha256'], items[1]['strategy_sha256'])
        self.assertNotEqual(items[0]['equity'], items[1]['equity'])
        self.assertNotEqual(self.id, second['id'])

    def test_worker_lock_rejects_second_owner(self):
        with paper.worker_lock(self.home):
            with self.assertRaises(ValueError):
                with paper.worker_lock(self.home):
                    pass

    def test_background_worker_and_monitor_start_inspect_stop_and_restart(self):
        cli = ROOT/'skills/quantevo/scripts/quantevo.py'
        def run(*args, check=True):
            return subprocess.run([sys.executable, str(cli), *args], capture_output=True, text=True, check=check)
        def wait_for(predicate):
            for _ in range(50):
                if predicate():
                    return
                time.sleep(.1)
            self.fail('Service did not reach expected state')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
        try:
            run('paper','run','--home',str(self.home),'--poll-seconds','.1','--background')
            self.assertTrue(paper.status(self.home)['worker']['healthy'])
            duplicate = run('paper','run','--home',str(self.home),'--background',check=False)
            self.assertEqual(duplicate.returncode, 2)
            run('serve','--home',str(self.home),'--port',str(port),'--background')
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/status') as response:
                self.assertEqual(len(json.load(response)['accounts']), 1)
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/') as response:
                self.assertIn(b'Paper account monitor', response.read())
            hostile = urllib.request.Request(f'http://127.0.0.1:{port}/api/status', headers={'Host':'attacker.example'})
            with self.assertRaises(urllib.error.HTTPError) as raised:
                urllib.request.urlopen(hostile)
            self.assertEqual(raised.exception.code, 403)
            run('paper','stop-worker','--home',str(self.home))
            wait_for(lambda: not paper.status(self.home)['worker'].get('running'))
            run('paper','run','--home',str(self.home),'--poll-seconds','.1','--background')
            self.assertTrue(paper.status(self.home)['worker']['healthy'])
        finally:
            paper.request_stop(self.home)
            from quantevo_runtime import monitor
            monitor.stop(self.home)
            wait_for(lambda: not paper.status(self.home)['worker'].get('running'))
            def stopped():
                with paper.database(self.home) as con:
                    return not paper.get_meta(con, 'server', {}).get('running')
            wait_for(stopped)

    def test_upgrade_keeps_old_install_as_backup(self):
        installer = load_script('install_skill')
        destination = self.root/'skills'
        target = installer.install('codex', destination)
        (target/'personal-note.txt').write_text('keep me')
        installer.install('codex', destination, upgrade=True)
        backups = list((destination.parent/'skill-backups').glob('quantevo-*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0]/'personal-note.txt').read_text(), 'keep me')
        self.assertTrue((target/'scripts/quantevo_runtime/dashboard.html').exists())


if __name__ == '__main__':
    unittest.main()
