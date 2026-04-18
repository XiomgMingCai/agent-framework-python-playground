# Memory & Persistence

通过 ContextProvider 为 Agent 添加持久化记忆，实现跨对话的信息存储与检索。

## 前置知识

- 已完成[多轮对话](multi-turn.md)
- 了解 ContextProvider 接口（`before_run`/`after_run`）
- 了解 Session 与 SessionContext 的区别

## 核心概念

```
User Input → Agent (with ContextProvider)
                   ↓
              before_run()
                   ↓
           SessionContext.extend_instructions()
                   ↓
              Model Invocation (流式输出)
                   ↓
              after_run()
                   ↓
         存储对话信息 → Session.state 持久化
```

## 示例代码

**文件：** `examples/memory/main.py`

```python
import asyncio
import os
from dotenv import load_dotenv

from agent_framework import Agent, AgentSession, ContextProvider, SessionContext
from agent_framework.openai import OpenAIChatCompletionClient


class MemoryProvider(ContextProvider):
    """通用记忆 Provider，存储对话中的关键信息"""

    DEFAULT_SOURCE_ID = "memory"

    def __init__(self):
        super().__init__(self.DEFAULT_SOURCE_ID)

    async def before_run(
        self, *, agent, session, context: SessionContext, state: dict
    ) -> None:
        """在调用前注入记忆上下文"""
        memories = state.get("memories", [])
        if memories:
            memory_context = "\n".join([f"- {m}" for m in memories[-5:]])
            context.extend_instructions(
                self.source_id,
                f"🧠 相关记忆上下文：\n{memory_context}\n根据记忆上下文回答用户问题。",
            )

    async def after_run(
        self, *, agent, session, context: SessionContext, state: dict
    ) -> None:
        """在调用后存储对话内容"""
        memories = state.setdefault("memories", [])
        for msg in context.input_messages:
            text = getattr(msg, "text", "") or ""
            if isinstance(text, str) and text.strip():
                if not any(text[:50] in m for m in memories):
                    memories.append(f"用户: {text[:100]}")


async def main():
    load_dotenv()
    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    agent = Agent(
        client=client,
        name="MemoryAgent",
        instructions=(
            "你是一个友好的助手，擅长记住用户的重要信息和偏好。\n"
            "当用户提供重要信息时，应该回复类似 '我记住了...' 的确认。\n"
            "使用友好的回复风格，适当使用表情符号。"
        ),
        context_providers=[MemoryProvider()],
    )

    session = agent.create_session()

    while True:
        user_input = input("\nYou : ").strip()
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "stats":
            memories = session.state.get("memory", {}).get("memories", [])
            print(f"\n📊 知识库统计：{{'total_memories': {len(memories)}}}\n")
            continue

        print("Agent: ", end="", flush=True)
        stream = await agent.run(user_input, session=session, stream=True)
        async for update in stream:
            if update.contents:
                for content in update.contents:
                    if hasattr(content, "text") and content.text:
                        print(content.text, end="", flush=True)
        print(f"\n📚 已存储记忆：{user_input[:50]}...\n")


if __name__ == "__main__":
    asyncio.run(main())
```

## 运行

```bash
uv run examples/memory/main.py
```

## 交互示例

```
You : Python 是什么时候发布的？
Agent: Python 是由 Guido van Rossum 开发的，它的第一个公开发行版本发布于 1991 年 2 月 20 日 🎂...
📚 已存储记忆：Python 是什么时候发布的？...

You : 我最喜欢的颜色是蓝色
Agent: 我记住了，你最喜欢的颜色是蓝色！💙 以后我会记得你喜欢这种清新又宁静的颜色哦~
📚 已存储记忆：我最喜欢的颜色是蓝色...

You : 你还记得我喜欢什么颜色吗？
Agent: 当然记得啦！你最喜欢的颜色是蓝色 💙~ 像晴朗的天空一样漂亮的蓝色呢！
📚 已存储记忆：你还记得我喜欢什么颜色吗？...

You : stats
📊 知识库统计：{'total_memories': 3, 'conversation_messages': 6}

You : exit
```

## 核心要点

| 组件 | 说明 |
|------|------|
| `ContextProvider` | 上下文提供者基类，通过 `before_run`/`after_run` 干预 Agent 行为 |
| `SessionContext.extend_instructions()` | 向 Agent 注入个性化指令 |
| `Session.state` | Session 级别的持久化字典，由 Provider 读写 |
| `agent.create_session()` | 创建新 Session，用于跨调用共享状态 |
| 流式输出 | `stream=True` 实时显示 Agent 回复 |

## ContextProvider 生命周期

```
1. before_run()
   - 在模型调用前执行
   - 从 Session.state 读取已有记忆
   - 通过 context.extend_instructions() 注入记忆上下文

2. 模型调用 (流式)
   - Agent 根据记忆上下文生成个性化回复
   - 实时流式输出到终端

3. after_run()
   - 在模型调用后执行
   - 从 context.input_messages 提取新信息
   - 将信息写入 Session.state 持久化
```

## 交互命令

| 命令 | 说明 |
|------|------|
| `exit` | 退出对话 |
| `stats` | 查看知识库统计信息 |

!!! note "提示"
    一个 Agent 可以同时使用多个 ContextProvider，按注册顺序执行 `before_run`，倒序执行 `after_run`。
