# Forward simulation contract — planned

No paper-account command, feed adapter or website is implemented yet.

A future account pins a strategy version, market/instrument, feed source,
execution model, costs, initial cash and start time. Historical bars warm up
indicators; they must not contribute pre-start profit to the forward account.

A worker polls or subscribes to completed bars and valid quotes. It persists
cash, positions, consumed timestamps, pending decisions, fills, equity and
errors. Reject rewritten history and deduplicate repeated events. Recover the
same account after restart instead of creating a new one. Do not fabricate
quotes, fills or equity observations when data is stale or unavailable.

Use the same strategy signal definitions across backtest and paper adapters;
record differences between next-open historical fills and observable forward
execution. Start with an appended CSV adapter, then add real market providers.
Polling CSVs is only meaningful if a separate producer writes completed bars.

The local website reads the account state and shows equity, positions, fills,
version, data freshness and worker status. It requires no LLM configuration.
The worker continues independently of browser and AI sessions; computer sleep
or worker shutdown interrupts processing. A later website control action must
go through the same lifecycle API as the CLI.
