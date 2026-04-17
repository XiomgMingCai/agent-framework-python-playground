# 流式输出

实时获取 Agent 响应，无需等待完整结果返回，适合长文本场景。

## 前置知识

- 已完成[环境配置](index.md)
- 了解 `async/await` 异步编程

## 示例代码

**文件：** `examples/streaming/main.py`

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

    # 流式调用
    stream = await agent.run(prompt, stream=True)

    print("Agent: ", end="", flush=True)
    async for update in stream:
        if update.contents:
            for content in update.contents:
                if content.text:
                    print(content.text, end="", flush=True)

    await stream.get_final_response()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", type=str, required=True)
    args = parser.parse_args()
    asyncio.run(main(args.prompt))
```

**运行：**

```bash
uv run examples/streaming/main.py -p "写一个快速排序算法"
```

## 核心要点

| 组件 | 说明 |
|------|------|
| `agent.run(prompt, stream=True)` | 启用流式，返回 `ResponseStream` |
| `async for update in stream` | 异步迭代每个更新块 |
| `update.contents` | 包含 `Content` 对象列表 |
| `content.text` | 文本内容，逐块获取 |
| `stream.get_final_response()` | 获取最终完整响应 |

## 流程图

```
User Input → Agent.run(stream=True) → Client → API Server
                                    ↓
                          ResponseStream
                                    ↓
                    async for update in stream
                              ↓
                    update.contents[i].text → User (实时)
                              ↓
                    get_final_response() → 完整响应
```

## 与非流式对比

| 模式 | 调用方式 | 返回 | 适用场景 |
|------|----------|------|----------|
| 非流式 | `agent.run(prompt)` | `AgentResponse.text` | 短查询、工具调用 |
| 流式 | `agent.run(prompt, stream=True)` | `ResponseStream` | 长文本、实时展示 |

!!! note "注意"
    流式输出需要客户端支持异步迭代（`async for`），确保运行环境支持 Python 3.10+ 的 `asyncio`。

## 验证

运行后观察输出是否为逐字实时显示，而非等待完整响应后才输出。
