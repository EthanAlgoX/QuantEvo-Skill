# ai-berkshire 参考分析

查看日期：2026-09-30。固定参考提交：
[`55be4f77ba9c1aeb0cfb98c0eed78babc2433706`](https://github.com/xbtlin/ai-berkshire/tree/55be4f77ba9c1aeb0cfb98c0eed78babc2433706)。

## 查看范围与观察

查看了 README、AGENTS.md、investment-research 的两种客户端版本、
技能生成脚本、两种客户端安装脚本和 momentum_backtest.py。
本次是结构与代码阅读，没有验证其投资业绩，也没有执行其金融数据工具。

| 文件 | 观察 |
| --- | --- |
| [skills/investment-research.md](https://github.com/xbtlin/ai-berkshire/blob/55be4f77ba9c1aeb0cfb98c0eed78babc2433706/skills/investment-research.md) | 投研流程写成 Markdown，要求调用计算工具 |
| [scripts/sync-codex-skills.py](https://github.com/xbtlin/ai-berkshire/blob/55be4f77ba9c1aeb0cfb98c0eed78babc2433706/scripts/sync-codex-skills.py) | 自动生成带元数据和适配说明的 Codex skill |
| [AGENTS.md](https://github.com/xbtlin/ai-berkshire/blob/55be4f77ba9c1aeb0cfb98c0eed78babc2433706/AGENTS.md) | 规定共享工具和兼容要求 |
| [scripts/install-codex-skills.sh](https://github.com/xbtlin/ai-berkshire/blob/55be4f77ba9c1aeb0cfb98c0eed78babc2433706/scripts/install-codex-skills.sh) | 生成后复制到客户端技能目录 |
| [tools/momentum_backtest.py](https://github.com/xbtlin/ai-berkshire/blob/55be4f77ba9c1aeb0cfb98c0eed78babc2433706/tools/momentum_backtest.py) | 独立 Python 工具，含特定研究样本 |

它的主要定位是 AI 投研工作流。上述入口不能被视为已经实现自动交易、
通用策略进化或持续模拟账户的证据。

## 本项目的设计判断

借鉴流程与计算工具分工、统一流程来源、明确计算校验步骤和文件化输出。
我们直接维护标准技能目录，用同一份 SKILL.md 安装到两个客户端，
从而减少生成与同步成本。工具随技能安装，避免依赖作者机器上的仓库路径。

本项目还需要单独实现研究状态机和持续模拟服务。评分、版本和生命周期
约束在程序中执行。公开包使用通用示例，个人策略与账户不作为发行素材。

仅借鉴架构，未复制参考仓库代码或报告。本地实现是独立的 SMA 回测基础，
不声称复现该项目的方法论或任何策略业绩。
