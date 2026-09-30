---
name: quantevo
description: "Backtest single-asset SMA strategies, organize host-AI parameter research, and run persistent CSV paper accounts with a local monitoring website and JSON status tools."
---

# QuantEvo

Use the user's already configured AI tool as the researcher. QuantEvo requires
no additional LLM endpoint or key. Instructions below apply to both Codex and
Claude Code; use the host's available file and terminal tools.

## Start

Locate this installed skill folder from the host's skill location. Set a local
`skill_dir` shell variable to its absolute path; do not assume the current
working directory is the project or a particular home directory.

```bash
python3 "$skill_dir/scripts/quantevo.py" doctor
```

Read the returned capability status. The runtime supports JSON `sma_cross`
backtests, persistent CSV paper accounts, a background worker and a loopback
monitoring website. Persistent evolution orchestration, final-evaluation
commands and built-in market API feeds are planned. Do not invent commands.

## Backtest

Read [the backtest contract](references/backtest.md). Confirm the strategy
format, instrument, bar frequency, data source, completed-bar cutoff, initial
cash and costs. Ask only for missing facts needed to execute the evaluation.
Use the user's supplied data; synthetic examples are for installation checks.

Run the bundled evaluator with an explicit annualization factor. Save output
to a new artifact path. Explain cost-adjusted return, Sharpe, drawdown, trading
activity and open inventory together, with data and engine hashes.

If the strategy format is unsupported, describe the missing adapter. Do not
silently convert an arbitrary Python strategy to an SMA example or execute it.

## Research and evolution

Read [the research contract](references/evolution.md) when optimization is
requested. Models propose hypotheses and strategy changes; tools calculate the
results. Preserve the baseline and each candidate. Keep datasets, costs and
scoring rules fixed during the study. Compare only matching evaluation windows.

The current evaluator has no built-in data splitting or finalization state.
With explicitly prepared train/validation CSVs, exploratory parameter trials
can use it, saving each proposal and result in a separate directory. Explain
that these are manually orchestrated experiments. Do not claim protected
holdouts, automatic promotion or a completed evolution service.

If the user wants production orchestration, use the research contract to
specify the missing implementation before making claims about its results.

## Forward simulation and monitoring

Read [the paper contract](references/paper.md). Confirm an absolute data-home
path, strategy version, feed path, expected bar interval and source label.
A user may deliberately paper-test the baseline or a rejected candidate;
record that choice without labeling it as a promoted research winner.

Create an account with `paper create`, run `paper run --background`, and open
`serve --background`. Use the same explicit `--home` for every command.
The CSV producer must append completed bars. A worker alone does not acquire
market data. Never treat synthetic demo feeds as real market observations.

Check `paper status` (or `/api/status`) for worker health, source freshness,
errors, positions and equity. Read details with `--id`. For a bounded inspection,
use `paper watch --count 3 --interval 2`; `--count 0` streams until interrupted.
A watch process is a data stream, not autonomous model execution. Automatic
future AI inspections require the user's host scheduling features.

History is warmup only; new observations start after account creation. Pins
include the strategy and runtime hashes. Do not silently replace the version,
edit consumed history, reset an account, or resume one that failed a history
integrity check. Report stale feeds and missing heartbeats even if equity is
unchanged. The bar execution model records modeled next-open fills after CSV
delivery; it is not an exchange execution report.

Use `paper pause` / `paper resume` for a specific account. Pause halts processing;
resume catches up on unconsumed rows and does not reset cash. Stop the worker
with `paper stop-worker`; stop the website with `serve --stop`. The processes
are independent. Preserve running processes unless the user requests stopping
or they are explicitly disposable validation services.

## Deliver

Return actual artifact paths, the evaluation settings, findings, rejected or
unsupported work, and capability limitations. No improvement is a valid
research outcome. Do not change evaluation rules to force an improvement.
