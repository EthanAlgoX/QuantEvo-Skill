# README workflow verification — 2026-09-30

**Outcome: steps 1–3 work, step 4 works as manual Codex parameter research,
and step 5 is unavailable. This release does not complete the full workflow.**

## Setup and evidence

Tested public commit `e27079dc5a97ec5a38e4c4da5dbf19ce03008651` from a
fresh HTTPS clone, using Python 3.9.6 and the current Codex desktop session.
Installed with `scripts/install_skill.py --client codex` into the actual
Codex skills directory. Explicitly read the installed SKILL.md and research
contract, then invoked its bundled evaluator outside the clone.

This proves installation and explicit use of the skill. Automatic discovery
after a client reload was not tested. No second Codex process or extra model
API was used: the active Codex session supplied the hypotheses and orchestration.

All market data was the project's generated synthetic fixture. Results below
are installation and research-workflow checks, not real-market performance.
Machine-readable evidence: [summary and proposals](verification/readme-workflow-20260930.json).

## 1. Installation

Passed. The installer copied a self-contained skill into Codex's skills folder.
The installed `doctor` command correctly listed CSV backtesting as available
and persistent research, final evaluation, forward workers and a dashboard as
planned. The installed CLI's help listed only `doctor` and `backtest`.

## 2. Strategy check

Passed. The example's JSON and `sma_cross` schema were accepted by the installed
runtime's `validate_strategy`. Schema and range rejection remain covered by the
foundation tests. There is no separate CLI strategy-validation command;
`json.tool` checks syntax and `backtest` validates inputs before evaluation.

## 3. Backtest

Passed. The 400-bar fixture with fast/slow 10/30, position weight 0.5, cash
10,000, fees 10 bps, slippage 5 bps and annualization 365 produced JSON with
the expected metrics, fills, equity and source fingerprints. The full-sample
result had 9 fills and 4 closed trades. Output-overwrite protection remains
covered by tests.

## 4. Host-AI parameter research

Manually executed by Codex through the installed skill. Before evaluating
candidates, saved a contract with a three-proposal budget and chronological
row ranges: training [0,240), validation [240,320), final [320,400).
The objective was validation Sharpe improvement greater than 0.05, subject to
drawdown no worse than -15% and at least one closed validation trade. Each
window reset cash and included its own warmup, matching the existing evaluator.

Codex supplied these candidates before observing their evaluation results:

| Version | Fast / slow | Hypothesis | Validation Sharpe | Closed validation trades |
| --- | --- | --- | ---: | ---: |
| Baseline | 10 / 30 | Original strategy | 8.5180 | 0 |
| Faster response | 5 / 20 | Reduce crossover lag; test turnover costs | 8.1391 | 0 |
| Smoother trend | 10 / 45 | Filter shorter oscillations | 6.4285 | 0 |
| Balanced response | 8 / 25 | Reduce lag with a moderate window change | 8.1776 | 0 |

All candidates failed the declared criteria. Selection was saved as
`selected: null`; no final evaluation was run and no original strategy was
replaced. No criteria were loosened to force success. The absence of closed
validation trades also limits interpretation of the apparent Sharpe values.

This verifies manual proposal → evaluation → comparison. It does not verify a
persistent evolution service, automatic budgeting, inaccessible holdouts or
restart recovery. Synthetic generation is inspectable, so these data cannot
be described as an independently blinded test.

## 5. Forward simulation

Unavailable. The installed CLI has no paper-account entry point, market-data
worker, persisted account lifecycle or website. No simulated account was
started. A historical backtest or repeated recalculation would not establish
forward-simulation behavior, so none was presented as a substitute.

## Documentation corrections

Both README versions now follow installation → strategy check → backtest →
host-AI exploration → forward-simulation status. Commands use the installed
helper, explain the shell variable and explicit skill loading, and state that
step 5 cannot execute. The previous installation-after-backtest order has been
removed. Runtime capabilities have not been expanded by this documentation fix.

## 中文结论

已实际安装并调用技能，策略校验和回测通过。当前 Codex 提出了三个带假设的
参数候选，调用安装后的工具评测并记录；没有合格改进，所以没有进行最终
评测或替换原策略。模拟运行缺少实现，无法执行。双语 README 已据此修正，
不会把这次核查描述成完整五步闭环通过。
