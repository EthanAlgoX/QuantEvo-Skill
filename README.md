<div align="center">

# QuantEvo Skill

**Bring strategy research to the AI tools you already use.**

Backtest · Evolve · Paper trade

[English](README.md) | [简体中文](README.zh-CN.md)

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square)
![Codex and Claude Code](https://img.shields.io/badge/Works_with-Codex_%26_Claude_Code-24292F?style=flat-square)
![Paper ready v0.1.0](https://img.shields.io/badge/Release-v0.1.0-18715B?style=flat-square)

[Quick start](#quick-start) · [What's available](#whats-available) · [Roadmap](#roadmap) · [Documentation](#documentation)

</div>

![QuantEvo workflow: backtest, AI-assisted research, and persistent paper monitoring.](assets/workflow.svg)

QuantEvo Skill is a local strategy research skill for **Codex and Claude Code**. Use your existing AI setup to understand a strategy, run deterministic evaluations, and develop testable optimization ideas. There is no additional LLM API configuration inside QuantEvo.

The long-term workflow connects reproducible backtests, iterative strategy evolution, and persistent paper accounts with a local monitoring dashboard.

> **v0.1.0:** backtest single-asset SMA strategies, explore candidates with your AI, and run persistent CSV paper accounts with a bilingual local dashboard. No extra LLM API or Node.js setup is required. No real orders are placed.

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
| Forward paper accounts | ✅ Available | Append-only completed CSV bars, pinned strategy, SQLite state, restart recovery |
| Local monitoring dashboard | ✅ Available | Multiple accounts, equity, positions, fills, feed / worker health, English / Chinese |

Run `doctor` to inspect the installed version's machine-readable capabilities.

## Quick start

**Requirements:** Python 3.9+ and a configured Codex or Claude Code. The five-step status below was checked on **2026-09-30** using a fresh GitHub clone and an installed Codex skill.

| Step | Verified outcome |
| --- | --- |
| 1. Install the skill | Passed: installed to Codex and ran its bundled tools outside the checkout |
| 2. Test a strategy | Passed: example strategy schema accepted; unsupported formats remain rejected |
| 3. Backtest | Passed: synthetic CSV produced metrics, fills, equity, and provenance |
| 4. Evolve with your AI | Manual exploration verified: this Codex session proposed and evaluated three candidates; none qualified |
| 5. Run a paper account | Passed: installed worker, two persistent accounts, local website, JSON monitoring, and restart recovery |

The workflow is available with **host-AI parameter exploration** and an **append-only CSV feed**. The initial [research verification](docs/readme-workflow-verification-20260930.md) records the earlier release; the [paper verification](docs/paper-workflow-verification-20260930.md) covers v0.1.0.

### 1. Install the skill

```bash
git clone https://github.com/EthanAlgoX/QuantEvo-Skill.git
cd QuantEvo-Skill
python3 scripts/install_skill.py --client codex

skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/quantevo"
python3 "$skill_dir/scripts/quantevo.py" doctor
```

For Claude Code, use `--client claude` and set `skill_dir="$HOME/.claude/skills/quantevo"`. An existing skill is preserved by default. To update it, add `--upgrade`; the installer retains a backup in the sibling `skill-backups` directory outside the skills directory. Stop active workers before upgrading: accounts pin runtime hashes, so a changed engine requires its original runtime or a new account. A custom destination can be supplied with `--destination /absolute/path/to/skills`.

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

### 5. Run persistent paper accounts and the local website

A research run may find no improvement. You can still explicitly choose the baseline or a rejected candidate for a workflow trial; creating an account does not declare it a research winner.

Use a **new** demo feed path, and keep the same absolute `paper_home` for every command:

```bash
paper_home="$PWD/.quantevo"
mkdir -p "$paper_home"
python3 scripts/demo_feed.py --output "$paper_home/demo-feed.csv" --updates 0

python3 "$skill_dir/scripts/quantevo.py" paper create \
  --home "$paper_home" --strategy examples/sma-cross.json \
  --feed "$paper_home/demo-feed.csv" --name "SMA baseline (synthetic)" \
  --interval-seconds 1 --source-label "Synthetic workflow demo"
python3 "$skill_dir/scripts/quantevo.py" paper run --home "$paper_home" --background
python3 "$skill_dir/scripts/quantevo.py" serve --home "$paper_home" --port 8765 --background

# Append 120 completed synthetic bars over approximately two minutes.
python3 scripts/demo_feed.py --output "$paper_home/demo-feed.csv" --append --updates 120
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). The read-only website refreshes every three seconds and shows all accounts, worker health, feed freshness, equity, positions, fees, drawdown, and recent fills. Switch between English and Chinese. Create another account with another name or strategy to compare it on the same feed.

The demo producer stops after 120 updates. The worker continues running and the feed becomes **stale**. This is synthetic workflow data. For actual market observation, supply your own continuously appended, completed OHLCV CSV and set `--interval-seconds` to its expected bar interval. A built-in market API adapter is not included.

Existing bars only warm up the strategy. P&L begins with bars after account creation. Simulated fills use the next supplied bar's open and are recorded when that completed bar arrives; they are modeled fills, not exchange executions. Editing consumed history fails the account rather than silently rewriting its ledger.

Inspect the backend from Codex or Claude Code without opening the website:

```bash
python3 "$skill_dir/scripts/quantevo.py" paper status --home "$paper_home"
python3 "$skill_dir/scripts/quantevo.py" paper watch --home "$paper_home" --count 3 --interval 2
```

Ask your AI: “Read the installed QuantEvo skill, inspect these paper accounts using this absolute home path, and report stale data, stopped workers, errors, positions, and performance.” JSON is also available at `/api/status` and `/api/accounts/<id>`. `watch` streams snapshots; continuous AI inspection requires scheduling in your host tool. The Python worker runs independently of the conversation, but is not an OS startup service.

Stop the worker and website separately; their SQLite accounts remain available for restart:

```bash
python3 "$skill_dir/scripts/quantevo.py" paper stop-worker --home "$paper_home"
python3 "$skill_dir/scripts/quantevo.py" serve --home "$paper_home" --stop
```

Use `paper pause --home "$paper_home" --id <id>` or `paper resume` to control one account. Resume processes any unconsumed bars. See the [paper contract](skills/quantevo/references/paper.md) for the execution and recovery rules.

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
- [x] **Paper trading:** append-only CSV feeds, pinned strategies, persistent accounts, restart recovery.
- [ ] **Market feeds:** built-in market data adapters.
- [x] **Monitoring:** bilingual local dashboard and JSON inspection of forward account health.
- [ ] **Distribution:** broader strategy adapters, release documentation, and a published license.

Evolution will use the host AI to propose changes and deterministic tools to evaluate them. A study can end with **no improvement**. Paper workers run independently of the AI conversation and pin the strategy version they execute.

## Documentation

| Guide | Content |
| --- | --- |
| [Skill entry point](skills/quantevo/SKILL.md) | Shared host-agent workflow |
| [Backtest contract](skills/quantevo/references/backtest.md) | Implemented format, execution, and metric rules |
| [Evolution contract](skills/quantevo/references/evolution.md) | Planned research lifecycle and manual exploration boundaries |
| [Paper contract](skills/quantevo/references/paper.md) | Implemented CSV accounts, background processes, dashboard, and monitoring |
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
