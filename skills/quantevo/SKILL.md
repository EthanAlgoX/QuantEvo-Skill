---
name: quantevo
description: "Evaluate single-asset SMA strategies on local OHLCV CSV data and organize reproducible strategy research. Use for strategy backtests, optimization experiments, and planning forward paper simulations."
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

Read the returned capability status. This foundation implements CSV backtests
for JSON `sma_cross` strategies only. Persistent evolution orchestration,
final-evaluation commands, a forward worker and a website are planned. State
this boundary if the user's request needs them; do not invent executable commands.

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

## Forward simulation

Read [the forward simulation contract](references/paper.md) when requested.
The foundation cannot start a forward account yet. A historical equity curve
must be described as a backtest. Plan the worker and data adapter, or implement
them when requested. Simulated account execution stays independent of the host
AI conversation, with a pinned strategy version and restartable state.

## Deliver

Return actual artifact paths, the evaluation settings, findings, rejected or
unsupported work, and capability limitations. No improvement is a valid
research outcome. Do not change evaluation rules to force an improvement.
