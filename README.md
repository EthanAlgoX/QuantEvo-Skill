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

**Requirements:** Python 3.9+ and a configured Codex or Claude Code. The five-step status below was checked on **2026-09-30** using a fresh GitHub clone and an installed Codex skill.

| Step | Verified outcome |
| --- | --- |
| 1. Install the skill | Passed: installed to Codex and ran its bundled tools outside the checkout |
| 2. Test a strategy | Passed: example strategy schema accepted; unsupported formats remain rejected |
| 3. Backtest | Passed: synthetic CSV produced metrics, fills, equity, and provenance |
| 4. Evolve with your AI | Manual exploration verified: this Codex session proposed and evaluated three candidates; none qualified |
| 5. Run a paper account | **Unavailable:** no paper account command, feed worker, or monitoring website exists yet |

**The full five-step workflow is not supported by this release.** You can install, backtest, and explore parameters with your AI. Forward simulation still needs implementation. See the [verification report](docs/readme-workflow-verification-20260930.md).

### 1. Install the skill

```bash
git clone https://github.com/EthanAlgoX/QuantEvo-Skill.git
cd QuantEvo-Skill
python3 scripts/install_skill.py --client codex

skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/quantevo"
python3 "$skill_dir/scripts/quantevo.py" doctor
```

For Claude Code, use `--client claude` and set `skill_dir="$HOME/.claude/skills/quantevo"`. An existing skill is preserved and installation stops; inspect its version with `doctor` before reusing it. A custom destination can be supplied with `--destination /absolute/path/to/skills`.

Reload skills in your client if needed. In an already running conversation, explicitly ask the AI to read the installed `SKILL.md` using its absolute path; a successful file copy alone does not prove automatic skill discovery.

### 2. Prepare and test a strategy

Use the included SMA example first:

```bash
python3 -m json.tool examples/sma-cross.json
python3 scripts/make_demo.py --output demo.synthetic.csv
```

`json.tool` checks JSON syntax. The backtest engine also validates the strategy schema, parameter ranges, and OHLCV data before evaluation. The generated daily series is **synthetic**, used only to test the workflow; it is not real market evidence.

Run the following examples from the repository root with unused output paths. The `skill_dir` variable belongs to the same shell session; set it again in a new terminal.

### 3. Run the installed skill's backtest

```bash
python3 "$skill_dir/scripts/quantevo.py" backtest \
  --strategy examples/sma-cross.json \
  --data demo.synthetic.csv \
  --initial-cash 10000 \
  --fee-bps 10 \
  --slippage-bps 5 \
  --periods-per-year 365 \
  --output demo.backtest.json
```

Inspect `demo.backtest.json` for settings, metrics, fills, equity, and hashes. Existing output files are preserved; choose new paths when rerunning. The installed helper is self-contained; from another directory, supply absolute input/output paths.

### 4. Ask Codex or Claude Code to explore parameters

Provide the installed skill's **absolute path**, your strategy, and your CSV to your existing AI conversation:

> Read the installed QuantEvo SKILL.md. On this synthetic example, prepare chronological training and validation windows and leave the final window uninspected. Fix cash at 10,000, fees at 10 bps, slippage at 5 bps, and annualization at 365. Propose up to three SMA parameter candidates with written hypotheses, call the installed evaluator, and save the baseline, proposals, and every result. Define the selection criteria before running candidates. Report no improvement if none qualifies. Do not call a historical backtest a forward simulation.

The **host AI** proposes changes and orchestrates tool calls. QuantEvo does not call another model API and has no `evolve` command. This is manual parameter research, with window portfolios reset and warmup included. Persistent budgets, automatic selection/finalization, and protected holdouts are not implemented.

During our check, Codex evaluated three hypotheses on identical windows and found no qualifying improvement. The result and limitations are documented in the verification report. This confirms the manual tool workflow, not strategy effectiveness.

### 5. Forward simulation — not available yet

There is no supported command to create or start a paper account in this release. Stop here: a backtest equity curve cannot substitute for forward simulation. Account persistence, feed ingestion, a background worker, and the local website are roadmap items. See the [paper contract](skills/quantevo/references/paper.md).

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
