# 基础对话

最简单的 Agent 用法，非流式调用，适合理解核心概念。

## 前置知识

- 已完成[环境配置](index.md)
- 了解 `asyncio` 异步编程基础

## 示例代码

**文件：** `examples/basic/main.py`

```python
import asyncio
import os
import argparse
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient


async def main(prompt: str):
    load_dotenv()

    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model = os.getenv("AI_MODEL")

    if not all([api_key, base_url, model]):
        raise ValueError("请在 .env 中配置 AI_API_KEY、AI_BASE_URL、AI_MODEL")

    client = OpenAIChatCompletionClient(
        api_key=api_key,
        base_url=base_url,
        model=model
    )

    agent = Agent(
        client=client,
        name="MyPythonAgent",
        instructions="You are a helpful assistant."
    )

    result = await agent.run(prompt)
    print(result.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", type=str, required=True)
    args = parser.parse_args()
    asyncio.run(main(args.prompt))
```

**运行：**

```bash
uv run examples/basic/main.py -p "你好"
```

## 核心要点

| 组件 | 说明 |
|------|------|
| `Agent` | Agent 实例，整合 Client 和指令 |
| `OpenAIChatCompletionClient` | 底层通信客户端，兼容 OpenAI 格式 API |
| `agent.run(prompt)` | 非流式调用，等待完整响应 |
| `result.text` | Agent 返回的文本内容 |

## 流程图

```
User Input → Agent.run() → Client → API Server
                              ↓
                        AgentResponse
                              ↓
                        result.text → User
```

## 验证

运行后观察输出是否包含 Agent 响应文本，确认流程正常工作。
