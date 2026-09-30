<div align="center">

# QuantEvo Skill

**Bring strategy research to the AI tools you already use.**

Backtest · Evolve · Paper trade

[English](README.md) | [简体中文](README.zh-CN.md)

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square)
![Codex and Claude Code](https://img.shields.io/badge/Works_with-Codex_%26_Claude_Code-24292F?style=flat-square)
![Foundation v0.0.1](https://img.shields.io/badge/Stage-Foundation_v0.0.1-D97706?style=flat-square)

[Quick start](#quick-start) · [What's available](#whats-available) · [Roadmap](#roadmap) · [Documentation](#documentation)

</div>

![QuantEvo workflow: backtesting is available; evolution and forward paper trading are planned.](assets/workflow.svg)

QuantEvo Skill is a local strategy research skill for **Codex and Claude Code**. Use your existing AI setup to understand a strategy, run deterministic evaluations, and develop testable optimization ideas. There is no additional LLM API configuration inside QuantEvo.

The long-term workflow connects reproducible backtests, iterative strategy evolution, and persistent paper accounts with a local monitoring dashboard.

> **Current release:** single-asset SMA crossover backtesting on local CSV data. Persistent evolution, forward paper trading, and the dashboard are planned. The foundation does not place real orders.

## Why QuantEvo?

A strategy idea becomes useful when you can inspect how it was tested. QuantEvo connects the AI research conversation to executable tools and explicit evidence.

| Principle | What it means in practice |
| --- | --- |
| **Use your own AI** | Research runs through your configured Codex or Claude Code session. |
| **Calculate with tools** | Python computes fills, costs, equity, and metrics. |
| **Keep evidence inspectable** | JSON results include settings, fills, equity, and SHA256 input fingerprints. |
| **Start locally** | The included evaluator works without network access or third-party runtime dependencies. |
| **Make improvement testable** | The research design preserves baselines, fixed evaluation rules, and candidate history. |

Local execution does not mean local model inference: your AI tool's own settings govern what it sends to its model provider.

## What's available

| Capability | Status | Scope |
| --- | --- | --- |
| Codex / Claude Code skill installation | ✅ Available | One shared skill with bundled Python tools |
| Strategy backtesting | ✅ Available | JSON `sma_cross`, one asset, long-only, local OHLCV CSV |
| Costs and evaluation evidence | ✅ Available | Fees, slippage, Sharpe, drawdown, fills, equity, input hashes |
| AI-assisted parameter exploration | 🧪 Manual | Host AI proposes changes; users prepare data windows and save separate results |
| Persistent strategy evolution | 🗓 Planned | Experiment budgets, trial history, candidate selection, final checks |
| Forward paper accounts | 🗓 Planned | Feed ingestion, pinned versions, persistent state, restart recovery |
| Local monitoring dashboard | 🗓 Planned | Equity, positions, fills, and feed / worker status |

Run `doctor` to inspect the installed version's machine-readable capabilities.

## Quick start

**Requirements:** Python 3.9+. An already configured Codex or Claude Code is needed to use the skill; the CLI works independently.

### 1. Get the project

```bash
git clone https://github.com/EthanAlgoX/QuantEvo-Skill.git
cd QuantEvo-Skill
python3 skills/quantevo/scripts/quantevo.py doctor
```

### 2. Run a sample backtest

The following series is **synthetic**, generated solely to verify installation. Run these commands from the repository root with unused output paths.

```bash
python3 scripts/make_demo.py --output demo.synthetic.csv

python3 skills/quantevo/scripts/quantevo.py backtest \
  --strategy examples/sma-cross.json \
  --data demo.synthetic.csv \
  --initial-cash 10000 \
  --fee-bps 10 \
  --slippage-bps 5 \
  --periods-per-year 365 \
  --output demo.backtest.json
```

Inspect `demo.backtest.json` for the settings, metrics, fills, equity curve, and provenance. Existing output files are preserved; choose new paths when rerunning.

### 3. Install the skill

Choose your client, or install for both:

```bash
python3 scripts/install_skill.py --client codex
python3 scripts/install_skill.py --client claude
```

| Client | Default installation directory |
| --- | --- |
| Codex | `~/.codex/skills/quantevo` (honors `CODEX_HOME`) |
| Claude Code | `~/.claude/skills/quantevo` |

An existing skill is preserved and installation stops. Use `--destination /absolute/path/to/skills` to choose another skills parent directory. Reload the skill in your client after installation.

Then ask your AI tool:

> Use QuantEvo to evaluate my SMA strategy against this daily CSV. Report fees, Sharpe, maximum drawdown, and trading activity. Explain the evaluation settings and suggest a testable parameter change.

### Optional: install the CLI

Inside your Python environment:

```bash
python3 -m pip install -e .
quantevo doctor
```

The Python package installs the CLI. Install the skill separately using the commands above.

## Bring your own strategy and data

The foundation accepts this JSON strategy format:

```json
{
  "schema": "quantevo.strategy.v1",
  "kind": "sma_cross",
  "fast": 10,
  "slow": 30,
  "position_weight": 0.5
}
```

Provide completed OHLCV bars in an ascending, timezone-aware CSV:

```csv
timestamp,open,high,low,close,volume
2026-01-01T00:00:00Z,100,103,99,102,1500
2026-01-02T00:00:00Z,102,104,100,101,1700
```

These two rows illustrate the format. A backtest needs at least `slow + 2` rows.

| Setting | Foundation behavior |
| --- | --- |
| Signal / execution | Completed-bar SMA crossover → next supplied bar's open |
| Portfolio | One asset, long-only, fractional inventory; entry size set by `position_weight` |
| Costs | Fees and adverse slippage included |
| Annualization | Explicit `--periods-per-year`: typically 252 for stock daily, 365 for crypto daily, 8760 for crypto hourly |
| Metrics / ending inventory | Includes warmup in the sample; final inventory is marked to the last close, without forced liquidation |
| Unsupported | Arbitrary Python strategies, leverage, funding, partial fills, and corporate actions |

Review irregular or missing bars before interpreting annualized metrics. The evaluator reports drawdown; it does not enforce a risk ceiling. See the [full backtest contract](skills/quantevo/references/backtest.md).

## Roadmap

- [x] **Foundation:** portable skill, CSV validation, deterministic backtests, JSON evidence.
- [ ] **Evolution:** fixed research contracts, persistent trials, budgets, selection, and final evaluation.
- [ ] **Paper trading:** append-only CSV feeds, then market data adapters and restartable accounts.
- [ ] **Monitoring:** local dashboard for research results and forward account health.
- [ ] **Distribution:** broader strategy adapters, release documentation, and a published license.

Evolution will use the host AI to propose changes and deterministic tools to evaluate them. A study can end with **no improvement**. Paper workers will run independently of the AI conversation and pin the strategy version they execute.

## Documentation

| Guide | Content |
| --- | --- |
| [Skill entry point](skills/quantevo/SKILL.md) | Shared host-agent workflow |
| [Backtest contract](skills/quantevo/references/backtest.md) | Implemented format, execution, and metric rules |
| [Evolution contract](skills/quantevo/references/evolution.md) | Planned research lifecycle and manual exploration boundaries |
| [Paper contract](skills/quantevo/references/paper.md) | Planned forward simulation behavior |
| [Architecture and roadmap](docs/architecture.md) · 中文 | Component responsibilities and implementation sequence |
| [ai-berkshire reference notes](docs/reference-ai-berkshire.md) · 中文 | Observations behind the workflow/tool separation |

## Contributing

Contributions to strategy adapters, research records, feed handling, tests, and bilingual documentation are welcome. Start with [the architecture](docs/architecture.md) and [shared development rules](AGENTS.md).

Validate runtime changes with:

```bash
python3 -m unittest discover -s tests -v
```

Keep English and Chinese README content aligned, and clearly distinguish implemented behavior from roadmap items.

## Acknowledgments and license

Inspired by [ai-berkshire](https://github.com/xbtlin/ai-berkshire)'s approach to packaging research workflows as skills backed by executable tools. QuantEvo's implementation is independent.

A license has not been selected yet. The repository is public; release licensing remains on the roadmap.
