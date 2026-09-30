# CSV paper accounts — implemented v0.1.0

Single-asset SMA accounts persist in `<home>/paper.sqlite3`. Each account pins
its strategy JSON, strategy hash and runtime hashes, a source path/label,
initial cash, fees, slippage, expected bar interval and start time.

## Start

Set `skill_dir` to the installed skill path and `paper_home` to an absolute data
home. Provide a CSV with at least `slow + 2` completed, increasing, timezone-aware
bars. For this adapter, timestamps identify completed-bar events. History is
indicator warmup, with zero pre-start profit. Initial future timestamps fail.

```bash
python3 "$skill_dir/scripts/quantevo.py" paper create \
  --home "$paper_home" --strategy /absolute/path/strategy.json \
  --feed /absolute/path/completed-bars.csv --name "SMA baseline" \
  --interval-seconds 3600 --source-label "My hourly CSV producer"
python3 "$skill_dir/scripts/quantevo.py" paper run --home "$paper_home" --background
python3 "$skill_dir/scripts/quantevo.py" serve --home "$paper_home" --port 8765 --background
```

The worker does not fetch market data. Another producer must append completed
rows to the CSV. Built-in market API feeds are planned. Synthetic demonstration
feeds test the workflow only. Do not promise activity without a running producer.

## Execution and integrity

Only appended bars with timestamps after account creation affect account
returns. Earlier appended history is consumed as additional warmup. Future rows
wait until their timestamp. Signals use the prior two completed SMA observations.
The next supplied bar's open is a modeled fill with adverse slippage and fees,
recorded after that bar is delivered. It is bar-based forward simulation, not
observable live order execution; the CSV producer's timestamp contract matters.

Cash starts at 10,000 by default; no pre-start inventory or profits carry over.
Ledger decisions, fills and equity persist transactionally. Repeated polls do
not duplicate events. Restart catches up pending rows. A consumed-prefix hash
rejects rewritten or validly truncated history and permanently fails the account.
Missing/partially-written files retain the last good state and can recover.
Runtime hash changes also fail an account instead of silently changing execution.

`pause` stops processing only; `resume` catches up. It does not ignore paused
market events or reset the account. Failed integrity accounts cannot resume.
One worker owns each data home; multiple accounts can share a feed. Closing
browser/AI sessions does not stop detached services. Computer sleep and service
shutdown still interrupt processing; this CLI does not install an OS boot daemon.

## Monitoring

```bash
python3 "$skill_dir/scripts/quantevo.py" paper status --home "$paper_home"
python3 "$skill_dir/scripts/quantevo.py" paper status --home "$paper_home" --id ACCOUNT_ID
python3 "$skill_dir/scripts/quantevo.py" paper watch --home "$paper_home" --count 3 --interval 2
```

Status reports account state, data age, errors, equity, inventory, return,
fees and worker heartbeat. A feed becomes stale after three declared bar
intervals (minimum five seconds). No new bars means no new equity observations.
`watch --count 0` streams until interrupted; it does not wake or run an AI model.
AI scheduling is managed by the host tool, when requested by the user.

The website is read-only, binds to `127.0.0.1`, and refreshes every three seconds.
It displays all accounts, a selected account's latest 300 equity observations,
recent fills, version identity, feed freshness and worker health. It supports
English and Chinese and requires no frontend build or internet connection.
JSON routes: `/api/status` and `/api/accounts/ACCOUNT_ID`.

## Stop and restart

```bash
python3 "$skill_dir/scripts/quantevo.py" paper stop-worker --home "$paper_home"
python3 "$skill_dir/scripts/quantevo.py" serve --home "$paper_home" --stop
```

Account controls: `paper pause --home ... --id ...`, `paper resume --home ... --id ...`.
Restart the worker or monitor with the same home. Background logs are `worker.log`
and `server.log`. Active accounts pin runtime files; upgrade skill before creating
accounts, or preserve the previous installation to run existing pinned accounts.

Limits: CSV 15 MB, one asset per account, long-only fractional inventory, no
exchange orders or funding/corporate-action model. The producer and interval
conventions determine quote freshness. Ledgers grow as JSON within SQLite; retention
and storage optimization are future work for high-frequency, long-duration runs.
OS service management and market API
adapters are not included yet.
