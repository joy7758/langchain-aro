<!-- language-switch:start -->
[English](./README.md) | [中文](./README.zh-CN.md)
<!-- language-switch:end -->

# 朗查阿罗

LangChain 中间件用于执行完整性、审计跟踪和可验证代理运行。

## 它是什么

`langchain-aro` 是一个早期的 MVP，用于从 LangChain 风格的运行中捕获最小回调流，并将其转换为可在以后导出、散列和验证的便携式工件。

它并不试图取代追踪系统或可观察平台。它专注于执行完整性：生成可导出、散列和验证的可移植运行工件。

当前 MVP 根据真实的 `langchain-core` 回调流程进行验证。
通过 GitHub Actions 在 Python 3.11 和 3.12 上进行测试。

## 为什么执行完整性很重要

代理跟踪在系统运行时非常有用，但仅跟踪并不能为您提供可移植的完整性工件。如果需要在原始运行时之外审查、重播或比较运行，则需要对所发生的情况进行稳定的表示，并需要一种方法来验证它是否未被更改。

该项目解决了这个更小、更具体的问题：

* 捕获最小运行日志
* 将其序列化为便携式工件
* 计算稳定的执行哈希
* 稍后验证工件

## 它如何适合堆栈

`POP -> AOP -> ARO -> Token Governor`

`langchain-aro` 是 ARO 层面向 LangChain 的入口点，在此处生成和验证执行工件。

## 建筑学

```text
LangChain Runtime
       |
       v
ARO Middleware
       |
       v
Run Journal
       |
       v
Execution Hash
       |
       v
Verifiable Artifact
```

`langchain-aro` 是可观测系统的补充。它不会取代跟踪或运行时监控。它提供执行完整性工件。

## MVP 特点

* 运行日志
* 执行散列
* 工件导出
* 重播验证

## 快速入门

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python examples/basic_run.py
python examples/replay_verify.py
pytest
```

这些示例使用一个小型模拟链，因此即使没有完整的 LangChain 安装，仓库仍然可以运行。

## 最小 API 示例

```python
from langchain_aro import ARORecorder, verify_artifact

recorder = ARORecorder(project="demo", output_dir="artifacts")

result = chain.invoke(
    {"input": "hello"},
    config={"callbacks": [recorder.callback_handler()]},
)

artifact = recorder.finalize()
report = verify_artifact(artifact.path)
```

## 工件格式

默认情况下，工件导出到 `artifacts/run.json`。当前的 MVP 模式故意很小：

```json
{
  "version": "0.1.0",
  "project": "demo",
  "run_id": "8b7e0d6c-6fd8-4e2d-bf20-9ee73870c5f7",
  "created_at": "2026-03-08T00:00:00Z",
  "events": [
    {
      "type": "run_started",
      "timestamp": "2026-03-08T00:00:00Z",
      "payload": {
        "serialized": {
          "name": "MockChain"
        }
      }
    }
  ],
  "execution_hash": "..."
}
```

## 验证流程

1. 将最小回调序列捕获到日志中。
2. 将日志导出为 `run.json` 工件。
3. 从规范 JSON 重新计算执行哈希。
4. 比较存储的哈希并报告工件是否仍然有效。

## 路线图

* 在不失去最小 MVP 形状的情况下扩大回调覆盖范围
* 添加更丰富的工件导出选项，例如 JSONL
* 支持签名和更强大的来源元数据
* 待LangChain中间件路径稳定后添加更多框架适配器
