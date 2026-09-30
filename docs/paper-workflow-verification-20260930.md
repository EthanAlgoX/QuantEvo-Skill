# Paper workflow verification — v0.1.0

Verified on 2026-09-30 with Python 3.9 (unit tests), Python 3.12 (non-editable
package installation), and the installed Codex skill. All feeds in this report
are synthetic; this verifies mechanics, not investment performance.

## Results

| Check | Evidence |
| --- | --- |
| Install / upgrade | Canonical skill copied into Codex; previous install preserved outside the discovery directory; bundled CLI invoked outside the checkout |
| Baseline / host-AI research | Earlier report records baseline backtests and three Codex-proposed candidates, with no qualifying improvement; that result remains unchanged |
| Create accounts | Two independent SMA 10/30 accounts on the same appended feed, with exposure weights 0.50 and 0.25 |
| Forward ledger | Accounts begin with cash and zero historical profit; appended completed bars generate decisions, modeled fills, costs, and marked equity |
| Detached operation | Installed worker and website run separately from the initiating terminal; JSON `status` and bounded `watch` inspect them |
| Restart | Actual worker and website stopped and restarted with the same home; account IDs and ledger retained, feed processing continued |
| Ledger integrity | At an inspection after restart, each account had 895 forward observations and 72 fills, with no duplicate equity timestamps and no runtime errors |
| Website | Both accounts visible, selected-account equity/fills render, Chinese language and account switching work; inspected at desktop and 390 px mobile widths, no page overflow, no console warnings/errors |
| Refresh accessibility | Selected account button retains keyboard focus across automatic refresh |
| Package distribution | Non-editable package installed in a clean temporary virtual environment; CLI launched outside checkout, detached worker/server started, bundled HTML and JSON routes returned successfully |
| Automated checks | `python3 -m unittest discover -s tests -v`: 16 passed |

The live synthetic demo intentionally oscillates quickly, and the SMA strategies
lost money. Neither candidate selection nor profitability was inferred from the
paper run. Its producer is finite; after it exits the feed becomes stale while
the persistent worker remains available.

## Checks covered by automated tests

- Prior completed-bar signals and fee/slippage ledger reconciliation.
- Historical warmup excluded from account profit; no new bars add no observations.
- Repeated polls and restart preserve state without duplicate fills.
- Future rows wait; pause/resume catches up without resetting the account.
- Rewritten consumed history permanently fails the account.
- Missing feeds recover without discarding the last good ledger.
- Strategy snapshot remains fixed when the source file changes.
- Independent accounts and exclusive worker ownership.
- Detached worker/server start, JSON/HTML inspection, stop, and restart.
- Loopback Host enforcement and preserved installation backups.

## Boundaries

The implemented adapter consumes append-only, completed OHLCV CSV bars. It does
not fetch exchange data or place orders. Modeled next-bar-open fills are recorded
when the completed bar arrives. A producer must honor the timestamp/completed-bar
contract. CSV history is limited to 15 MB; account ledgers currently remain in
JSON within SQLite and grow with observations, so this initial implementation
needs retention/storage work for high-frequency, long-duration deployments.

AI proposals and interpretation belong to the host Codex/Claude Code session.
Persistent research budgets, automatic selection/final checks, built-in market
API feeds, OS startup services, and continuous host-AI scheduling remain future
work. The Python worker can run without an open conversation; `watch` streams
state and does not independently invoke an AI model.

The [earlier verification](readme-workflow-verification-20260930.md) accurately
records the prior foundation version, before paper functionality existed.
