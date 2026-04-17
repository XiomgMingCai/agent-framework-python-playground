# Microsoft Agent Framework 1.0 Python 练习项目

基于 [agent_framework](https://github.com/microsoft/agent-framework) 的 Python 学习项目，练习 Agent 的核心功能。

## 环境配置

在 `.env` 文件中配置 API：

```env
AI_API_KEY=your-api-key
AI_BASE_URL=https://api.siliconflow.cn/v1
AI_MODEL=Qwen/Qwen3.5-35B-A3B
```

> 支持任意 OpenAI Chat Completions 兼容 API（如 SiliconFlow、DeepSeek 等）

## 示例目录

| 目录 | 说明 |
|------|------|
| `examples/basic/` | 基础示例，非流式对话 |
| `examples/streaming/` | 流式输出示例 |

## 快速开始

```bash
# 基础对话
uv run examples/basic/main.py -p "你好"

# 流式输出
uv run examples/streaming/main.py -p "你好"
```

## 核心概念

- **Agent** — AI Agent 实例，基于 Chat Client 构建
- **Client** — 底层通信客户端（本项目使用 `OpenAIChatCompletionClient`）
- **流式 vs 非流式** — `agent.run(prompt)` 非流式，`agent.run(prompt, stream=True)` 流式

## 关键 API

```python
from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

# 创建 Client
client = OpenAIChatCompletionClient(api_key=..., base_url=..., model=...)

# 创建 Agent
agent = Agent(client=client, instructions="你的指令")

# 非流式调用
result = await agent.run("用户输入")
print(result.text)

# 流式调用
stream = await agent.run("用户输入", stream=True)
async for update in stream:
    if update.contents:
        for content in update.contents:
            if content.text:
                print(content.text, end="", flush=True)
```
