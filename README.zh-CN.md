<div align="center">

# QuantEvo Skill

**让你已有的 AI 工具，具备策略研究能力。**

回测 · 自进化 · 模拟运行

[English](README.md) | [简体中文](README.zh-CN.md)

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square)
![Codex and Claude Code](https://img.shields.io/badge/Works_with-Codex_%26_Claude_Code-24292F?style=flat-square)
![Paper ready v0.1.0](https://img.shields.io/badge/Release-v0.1.0-18715B?style=flat-square)

[快速开始](#快速开始) · [功能状态](#功能状态) · [路线图](#路线图) · [文档导航](#文档导航)

</div>

![QuantEvo 工作流：回测、AI 辅助研究、持久化模拟与本地监控。](assets/workflow.svg)

QuantEvo Skill 是面向 **Codex 和 Claude Code** 的本地策略研究技能。沿用你已有的 AI 配置，理解策略、执行确定性的评测，并提出可检验的优化假设。QuantEvo 内部无需再配置一套 LLM API。

项目目标是打通可复现回测、策略自进化和持续模拟账户，并通过本地网站查看运行状态。

> **v0.1.0：** 支持单标的 SMA 回测、宿主 AI 参数探索、持久化 CSV 模拟账户及双语本地监控网站。不需要额外配置 LLM API 或 Node.js，不发送真实订单。

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
| 前向模拟账户 | ✅ 可用 | 追加已收盘 CSV、固定策略、SQLite 持久化、重启恢复 |
| 本地监控网站 | ✅ 可用 | 多账户、净值、持仓、成交、行情与后台健康、中英文切换 |

运行 `doctor` 可查看已安装版本的机器可读能力清单。

## 快速开始

**环境要求：** Python 3.9+，以及已配置的 Codex 或 Claude Code。下表流程已于 **2026-09-30** 通过从 GitHub 重新克隆、实际安装 Codex skill 的方式核查。

| 步骤 | 实测结果 |
| --- | --- |
| 1. 安装 skill | 通过：已安装到 Codex，安装后的工具可在仓库外运行 |
| 2. 测试策略 | 通过：示例通过策略格式校验；不支持的格式仍会被拒绝 |
| 3. 回测 | 通过：合成 CSV 生成了指标、成交、净值和来源指纹 |
| 4. 用自己的 AI 自进化 | 已验证手动探索：当前 Codex 提出并评测了三个候选，均未通过筛选 |
| 5. 模拟运行 | 通过：安装后的后台、两个持久化账户、本地网站、JSON 检测和重启恢复 |

目前可以完成使用**宿主 AI 探索参数**、通过**追加 CSV 行情**模拟运行的流程。[初始研究验证](docs/readme-workflow-verification-20260930.md)记录旧版本；[模拟运行验证](docs/paper-workflow-verification-20260930.md)覆盖 v0.1.0。

### 1. 安装 skill

```bash
git clone https://github.com/EthanAlgoX/QuantEvo-Skill.git
cd QuantEvo-Skill
python3 scripts/install_skill.py --client codex

skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/quantevo"
python3 "$skill_dir/scripts/quantevo.py" doctor
```

Claude Code 用户改用 `--client claude`，并设置 `skill_dir="$HOME/.claude/skills/quantevo"`。已有同名技能默认保留。更新时加 `--upgrade`，安装器会在技能目录之外的同级 `skill-backups` 目录保留备份。升级前先停止后台：账户固定运行代码哈希，引擎发生变化时需使用原运行版本或新建账户。可用 `--destination /absolute/path/to/skills` 自定义技能父目录。

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

### 5. 启动持久化模拟账户和本地网站

研究没有找到改进时，也可以明确选择基线或被淘汰的候选进行流程测试。创建模拟账户不表示它通过了研究筛选。

示例行情文件需使用**新路径**，所有命令保持相同的绝对 `paper_home`：

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

# 约两分钟内追加 120 根已收盘合成 K 线。
python3 scripts/demo_feed.py --output "$paper_home/demo-feed.csv" --append --updates 120
```

打开 [http://127.0.0.1:8765](http://127.0.0.1:8765)。只读网站每三秒刷新，展示所有策略账户、后台健康、数据新鲜度、净值、仓位、费用、回撤和最近成交，支持中英文切换。使用其他名称或策略再创建账户，可以共用行情进行对比。

合成行情生成器追加 120 次后退出。后台继续运行，行情会显示**过期**。这只是流程测试数据；观察真实市场时，需要自行持续追加已收盘 OHLCV CSV，并把 `--interval-seconds` 设置为预计 K 线间隔。首版不含内置市场 API 适配器。

建账户时的历史数据只预热，不计历史盈亏；账户创建之后的新 K 线才开始记账。模拟成交按下一根输入 K 线的开盘价建模，在收到其完整已收盘数据时记录，不是交易所成交。修改已消费的历史会使账户失败，不能悄悄重写账本。

无需打开网站，也可以让 Codex 或 Claude Code 检测后台：

```bash
python3 "$skill_dir/scripts/quantevo.py" paper status --home "$paper_home"
python3 "$skill_dir/scripts/quantevo.py" paper watch --home "$paper_home" --count 3 --interval 2
```

向 AI 提出：“读取安装后的 QuantEvo skill，通过这个绝对 home 路径检查模拟账户，报告行情过期、后台停止、错误、持仓与收益情况。”网站也提供 `/api/status` 和 `/api/accounts/<id>` JSON。`watch` 只输出状态快照；持续由 AI 检查需要宿主工具的调度。Python 后台独立于对话持续运行，首版不提供开机自启动服务。

后台和网站分别停止，SQLite 账户会保留供重启恢复：

```bash
python3 "$skill_dir/scripts/quantevo.py" paper stop-worker --home "$paper_home"
python3 "$skill_dir/scripts/quantevo.py" serve --home "$paper_home" --stop
```

单账户可用 `paper pause --home "$paper_home" --id <id>` 和 `paper resume` 控制；恢复后处理未消费 K 线。成交与恢复规则详见[模拟运行合同](skills/quantevo/references/paper.md)。

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
- [x] **模拟运行：** 追加式 CSV、固定策略、持久化账户与重启恢复。
- [ ] **市场行情：** 内置市场数据适配器。
- [x] **本地监控：** 双语网站与 JSON 检测，展示前向账户及运行健康。
- [ ] **发行完善：** 扩展策略接口、完善发行文档与正式许可证。

自进化由宿主 AI 提出修改，程序负责评测；**没有找到改进**也应是有效结果。模拟后台进程独立于 AI 对话运行，并固定所执行的策略版本。

## 文档导航

| 文档 | 内容 |
| --- | --- |
| [技能入口](skills/quantevo/SKILL.md) | 两个客户端共用的研究流程 |
| [回测合同](skills/quantevo/references/backtest.md) | 已实现的格式、成交与指标规则 |
| [自进化合同](skills/quantevo/references/evolution.md) | 规划中的研究生命周期及手动探索边界 |
| [模拟运行合同](skills/quantevo/references/paper.md) | 已实现的 CSV 账户、后台、网站与检测规则 |
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
