# Research contract — planned orchestration

This contract guides exploratory work now and the persistent research service
later. The foundation has only `doctor` and `backtest` commands.

## Inputs

An immutable study contract identifies instrument and market, dataset source
and hash, strategy baseline, engine hash, costs, frequency, cash, chronological
train/validation/final windows, warmup convention, objective, risk constraints,
allowed changes and experiment budget. Fix these before candidate evaluation.

Each model proposal records a hypothesis, parent version, changes and expected
effect. Parameter proposals must satisfy the strategy schema. Logic mutation
requires a future execution adapter with an isolation design; do not execute
arbitrary uploaded Python with the foundation.

## Selection

Evaluate baseline and candidates on identical training and validation windows.
Select using validation results subject to predeclared constraints, with an
explicit treatment of insufficient trades and undefined Sharpe. Track every
attempt and rejection. Stop at the budget, user cancellation, or a declared
no-progress condition. Do not add the final window to proposal context.

Freeze the selected candidate before evaluating the final period. Record
final inspection once; if it fails, end the study rather than tuning against
that period. Reused historical periods are historical rechecks, not fresh blind
tests. Local file separation cannot make a holdout inaccessible to a host agent
that has filesystem access; avoid promising access isolation.

## Artifacts and lifecycle

Planned records: study contract, dataset snapshot, baseline result, append-only
proposal/result pairs, selected-version hash, final result and report. Planned
states: prepared → researching → selected → finalized or rejected. Persist
state transitions, reject work after selection, and support resumption without
duplicate experiments. A candidate does not become an active simulation version
implicitly. Future forward observations may motivate a new study, whose data
cutoff and evaluation rules must be independently recorded.

## Current manual experiments

Use pre-split CSVs prepared explicitly for the study and separate JSON strategies.
Run `backtest` on baseline and candidate for each window, saving proposals and
outputs separately. This resets cash at each CSV start and includes that CSV's
warmup in metrics. It does not implement continuous portfolio carry or warmup
exclusion. Until those features exist, label results exploratory and do not
claim they reproduce private QuantEvo's research evaluation protocol.
