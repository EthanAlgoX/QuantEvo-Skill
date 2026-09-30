<div align="center">

# QuantEvo Skill

**让你已有的 AI 工具，具备策略研究能力。**

回测 · 自进化 · 模拟运行

[English](README.md) | [简体中文](README.zh-CN.md)

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square)
![Codex and Claude Code](https://img.shields.io/badge/Works_with-Codex_%26_Claude_Code-24292F?style=flat-square)
![Foundation v0.0.1](https://img.shields.io/badge/Stage-Foundation_v0.0.1-D97706?style=flat-square)

[快速开始](#快速开始) · [功能状态](#功能状态) · [路线图](#路线图) · [文档导航](#文档导航)

</div>

![QuantEvo 工作流：回测已可用，自进化与前向模拟正在规划中。](assets/workflow.svg)

QuantEvo Skill 是面向 **Codex 和 Claude Code** 的本地策略研究技能。沿用你已有的 AI 配置，理解策略、执行确定性的评测，并提出可检验的优化假设。QuantEvo 内部无需再配置一套 LLM API。

项目目标是打通可复现回测、策略自进化和持续模拟账户，并通过本地网站查看运行状态。

> **当前版本：** 已支持本地 CSV 上的单标的 SMA 交叉策略回测。持久化自进化、前向模拟和监控网站尚在规划中。基础版本不发送真实订单。

## 为什么使用 QuantEvo？

策略假设需要能检查的评测证据。QuantEvo 把 AI 研究对话连接到可执行工具，让每个结果都有明确口径。

| 原则 | 使用方式 |
| --- | --- |
| **沿用自己的 AI** | 通过已配置的 Codex 或 Claude Code 进行研究。 |
| **用程序计算** | Python 计算成交、费用、净值与评测指标。 |
| **保留可核查证据** | JSON 结果包含参数、成交、净值及输入的 SHA256 指纹。 |
| **从本地开始** | 内置评测器不需要网络或第三方运行依赖。 |
| **检验优化效果** | 研究设计保留基线、固定评测规则与候选历史。 |

本地执行不等于模型在本地推理：AI 工具向模型提供方发送什么，仍取决于该工具自身的配置。

## 功能状态

| 能力 | 状态 | 当前范围 |
| --- | --- | --- |
| Codex / Claude Code 技能安装 | ✅ 可用 | 一份共享 skill，附带 Python 工具 |
| 策略回测 | ✅ 可用 | JSON `sma_cross`、单标的、仅做多、本地 OHLCV CSV |
| 成本与评测证据 | ✅ 可用 | 手续费、滑点、夏普率、回撤、成交、净值及输入哈希 |
| AI 辅助参数探索 | 🧪 手动编排 | 宿主 AI 提出修改；用户准备数据分段并分别保存结果 |
| 持久化策略自进化 | 🗓 规划中 | 实验预算、试验历史、候选选择与最终检查 |
| 前向模拟账户 | 🗓 规划中 | 行情接入、固定版本、持久化与重启恢复 |
| 本地监控网站 | 🗓 规划中 | 净值、持仓、成交及行情与后台进程状态 |

运行 `doctor` 可查看已安装版本的机器可读能力清单。

## 快速开始

**环境要求：** Python 3.9+，以及已配置的 Codex 或 Claude Code。下表流程已于 **2026-09-30** 通过从 GitHub 重新克隆、实际安装 Codex skill 的方式核查。

| 步骤 | 实测结果 |
| --- | --- |
| 1. 安装 skill | 通过：已安装到 Codex，安装后的工具可在仓库外运行 |
| 2. 测试策略 | 通过：示例通过策略格式校验；不支持的格式仍会被拒绝 |
| 3. 回测 | 通过：合成 CSV 生成了指标、成交、净值和来源指纹 |
| 4. 用自己的 AI 自进化 | 已验证手动探索：当前 Codex 提出并评测了三个候选，均未通过筛选 |
| 5. 模拟运行 | **暂不可用：** 尚无模拟账户命令、行情后台或监控网站 |

**当前版本无法完成完整的五步流程。** 可以安装、回测，并使用自己的 AI 探索参数；前向模拟仍需实现。详见[流程验证报告](docs/readme-workflow-verification-20260930.md)。

### 1. 安装 skill

```bash
git clone https://github.com/EthanAlgoX/QuantEvo-Skill.git
cd QuantEvo-Skill
python3 scripts/install_skill.py --client codex

skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/quantevo"
python3 "$skill_dir/scripts/quantevo.py" doctor
```

Claude Code 用户改用 `--client claude`，并设置 `skill_dir="$HOME/.claude/skills/quantevo"`。已有同名技能会保留并停止安装；复用前请用 `doctor` 检查版本。可用 `--destination /absolute/path/to/skills` 自定义技能父目录。

必要时在客户端重新加载技能。对已经打开的对话，可以明确要求 AI 通过绝对路径读取安装后的 `SKILL.md`；仅复制文件成功，不代表已经验证客户端能自动发现技能。

### 2. 准备并测试策略

先使用内置 SMA 示例：

```bash
python3 -m json.tool examples/sma-cross.json
python3 scripts/make_demo.py --output demo.synthetic.csv
```

`json.tool` 检查 JSON 语法；回测引擎还会在计算前校验策略格式、参数范围与 OHLCV 数据。生成的日线是**合成数据**，仅用于验证流程，不是实际市场证据。

以下示例请在仓库根目录执行，并使用尚不存在的输出路径。`skill_dir` 变量属于当前终端会话，新开终端后需要重新设置。

### 3. 通过安装后的 skill 做回测

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

打开 `demo.backtest.json` 查看设置、指标、成交、净值与哈希。已有结果文件会保留，重复运行请使用新路径。安装后的工具自带运行代码；在其他目录使用时，传入绝对输入与输出路径即可。

### 4. 让 Codex 或 Claude Code 探索参数

在现有 AI 对话中提供安装后的 skill **绝对路径**、策略文件和 CSV，并提出任务：

> 读取安装后的 QuantEvo SKILL.md。对这个合成示例按时间准备训练与验证数据，先不要查看最终区间。固定初始资金 10,000、手续费 10 bps、滑点 5 bps、年化参数 365。先定义筛选条件，再提出最多三个带书面假设的 SMA 参数候选，调用安装后的评测工具，保存基线、提案及每次结果。没有合格改进就如实报告。不要把历史回测当作前向模拟。

**宿主 AI** 负责提出修改并组织工具调用。QuantEvo 不会再调用其他模型 API，也没有 `evolve` 命令。这是手动参数研究，各数据分段会重置账户，指标包含预热。持久化预算、自动选择与最终检查、隔离留出数据等能力尚未实现。

本次核查中，Codex 对相同区间评测了三个假设，没有找到合格改进；结果与限制已记入验证报告。这验证的是手动研究工具流程，不代表策略有效性。

### 5. 前向模拟——当前不可用

当前版本没有可用的模拟账户创建或启动命令，流程在这里停止。历史回测净值不能替代前向模拟。账户持久化、行情接入、后台进程和本地网站仍是路线图中的功能，详见[模拟运行合同](skills/quantevo/references/paper.md)。

### 可选：安装命令行工具

在你的 Python 环境中执行：

```bash
python3 -m pip install -e .
quantevo doctor
```

Python 包安装的是 CLI；技能仍需通过上面的安装脚本单独安装。

## 使用自己的策略与行情

基础版本接受以下 JSON 策略格式：

```json
{
  "schema": "quantevo.strategy.v1",
  "kind": "sma_cross",
  "fast": 10,
  "slow": 30,
  "position_weight": 0.5
}
```

提供按时间升序排列、带时区的已收盘 OHLCV CSV：

```csv
timestamp,open,high,low,close,volume
2026-01-01T00:00:00Z,100,103,99,102,1500
2026-01-02T00:00:00Z,102,104,100,101,1700
```

这两行仅展示格式；实际回测至少需要 `slow + 2` 行。

| 设置 | 基础版本行为 |
| --- | --- |
| 信号与成交 | 已收盘 K 线产生 SMA 交叉信号 → 下一根输入 K 线开盘成交 |
| 账户模型 | 单标的、仅做多、允许小数持仓；`position_weight` 决定入场金额 |
| 成本 | 计入手续费与不利方向滑点 |
| 年化口径 | 显式设置 `--periods-per-year`：股票日线通常 252，加密日线 365，加密小时线 8760 |
| 指标与期末持仓 | 指标包含预热阶段；期末持仓按最后收盘价计值，不强制平仓 |
| 尚不支持 | 任意 Python 策略、杠杆、资金费率、部分成交与公司行动 |

解读年化指标前需要检查不规则采样与缺失 K 线。评测器报告回撤，但不会执行回撤上限风控。详细规则见[回测合同](skills/quantevo/references/backtest.md)。

## 路线图

- [x] **基础工具：** 可移植 skill、CSV 校验、确定性回测与 JSON 证据。
- [ ] **自进化研究：** 固定研究合同、持久化实验、预算、候选选择与最终评测。
- [ ] **模拟运行：** 先接追加式 CSV，再接市场行情源与可恢复账户。
- [ ] **本地监控：** 展示研究结果、前向账户表现与运行健康状态。
- [ ] **发行完善：** 扩展策略接口、完善发行文档与正式许可证。

自进化由宿主 AI 提出修改，程序负责评测；**没有找到改进**也应是有效结果。模拟后台进程将独立于 AI 对话运行，并固定所执行的策略版本。

## 文档导航

| 文档 | 内容 |
| --- | --- |
| [技能入口](skills/quantevo/SKILL.md) | 两个客户端共用的研究流程 |
| [回测合同](skills/quantevo/references/backtest.md) | 已实现的格式、成交与指标规则 |
| [自进化合同](skills/quantevo/references/evolution.md) | 规划中的研究生命周期及手动探索边界 |
| [模拟运行合同](skills/quantevo/references/paper.md) | 规划中的前向模拟行为 |
| [架构与实施路线](docs/architecture.md) | 模块职责及实施顺序 |
| [ai-berkshire 参考分析](docs/reference-ai-berkshire.md) | 工作流与工具分工的参考依据 |

## 参与贡献

欢迎贡献策略适配器、研究记录、行情接入、测试和双语文档。开发前请阅读[项目架构](docs/architecture.md)和[共享开发规则](AGENTS.md)。

修改运行工具后执行：

```bash
python3 -m unittest discover -s tests -v
```

请保持英文和中文 README 内容对应，清楚区分已实现功能与路线图。

## 致谢与许可证

参考了 [ai-berkshire](https://github.com/xbtlin/ai-berkshire) 用 skill 组织研究流程、用可执行工具支持计算的设计。QuantEvo 采用独立实现。

目前尚未确定正式许可证。仓库已公开，发行许可证仍在路线图中。
