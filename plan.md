# 下一步 Microsoft Agent Framework 1.0 Python 练习项目 主题是多轮对话 (Multi-Turn Conversation)

让 Agent 记住对话历史，支持连续上下文的多轮交互。

## 前置知识

- 已完成[工具调用](tool_use.md)
- 了解 Python `list` 与异步编程基础

## 核心概念

```
第1轮: User → Agent → Response
                ↓
         保存对话历史
                ↓
第2轮: User → Agent (携带历史) → Response
                ↓
         更新对话历史
                ↓
第3轮: User → Agent (携带历史) → Response
```

## 示例代码

**文件：** `examples/multi_turn/main.py`

```python
import asyncio
import os
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework.messages import ChatMessage, MessageRole


async def chat_loop():
    load_dotenv()

    api_key  = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model    = os.getenv("AI_MODEL")

    if not all([api_key, base_url, model]):
        raise ValueError("请在 .env 中配置 AI_API_KEY、AI_BASE_URL、AI_MODEL")

    client = OpenAIChatCompletionClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    agent = Agent(
        client=client,
        name="ChatAgent",
        instructions=(
            "你是一个友好的助手，能够记住对话历史并保持上下文连贯。\n"
            "回答时可以引用之前的对话内容。"
        ),
    )

    # ── 对话历史 ──────────────────────────────────────────
    history: list[ChatMessage] = []

    print("=" * 50)
    print("  多轮对话 Demo  (输入 'exit' 退出, 'clear' 清空历史)")
    print("=" * 50)

    while True:
        # 获取用户输入
        try:
            user_input = input("\nYou : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[对话结束]")
            break

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("[对话结束]")
            break

        if user_input.lower() == "clear":
            history.clear()
            print("[对话历史已清空]")
            continue

        if user_input.lower() == "history":
            _print_history(history)
            continue

        # ── 将用户消息加入历史 ────────────────────────────
        history.append(
            ChatMessage(role=MessageRole.USER, content=user_input)
        )

        # ── 流式调用，携带历史 ────────────────────────────
        print("Agent: ", end="", flush=True)

        full_response = ""

        stream = await agent.run(
            messages=history,   # 传入完整历史
            stream=True,
        )

        async for update in stream:
            if update.contents:
                for content in update.contents:
                    if content.text:
                        print(content.text, end="", flush=True)
                        full_response += content.text

        print()  # 换行

        # ── 将 Agent 回复加入历史 ─────────────────────────
        history.append(
            ChatMessage(role=MessageRole.ASSISTANT, content=full_response)
        )

        # ── 显示当前历史轮数 ──────────────────────────────
        turns = len(history) // 2
        print(f"  [当前对话：第 {turns} 轮，共 {len(history)} 条消息]")


def _print_history(history: list[ChatMessage]):
    """打印对话历史摘要"""
    if not history:
        print("  [历史为空]")
        return

    print("\n─── 对话历史 ───")
    for i, msg in enumerate(history, 1):
        role  = "You  " if msg.role == MessageRole.USER else "Agent"
        # 超过 80 字符截断显示
        text  = msg.content if len(msg.content) <= 80 else msg.content[:80] + "..."
        print(f"  {i:02d}. [{role}] {text}")
    print("────────────────")


if __name__ == "__main__":
    asyncio.run(chat_loop())
```

## 运行

```bash
uv run examples/multi_turn/main.py
```

## 交互示例

```
==================================================
  多轮对话 Demo  (输入 'exit' 退出, 'clear' 清空历史)
==================================================

You : 我叫李明，是一名 Python 开发者
Agent: 你好，李明！很高兴认识你。作为一名 Python 开发者，
       你在做什么类型的项目呢？
  [当前对话：第 1 轮，共 2 条消息]

You : 我在学习 AI Agent 开发
Agent: 太棒了，李明！AI Agent 开发是目前非常热门的方向。
       结合你的 Python 背景，学习 Agent 框架应该会很顺手。
  [当前对话：第 2 轮，共 4 条消息]

You : 你还记得我的名字吗？
Agent: 当然记得！你叫李明，是一名 Python 开发者，
       目前正在学习 AI Agent 开发。
  [当前对话：第 3 轮，共 6 条消息]

You : history
─── 对话历史 ───
  01. [You  ] 我叫李明，是一名 Python 开发者
  02. [Agent] 你好，李明！很高兴认识你。作为一名 Python 开发者，你在做什...
  03. [You  ] 我在学习 AI Agent 开发
  04. [Agent] 太棒了，李明！AI Agent 开发是目前非常热门的方向。结合你的 ...
  05. [You  ] 你还记得我的名字吗？
  06. [Agent] 当然记得！你叫李明，是一名 Python 开发者，目前正在学习 AI ...
────────────────

You : clear
[对话历史已清空]

You : 你还记得我的名字吗？
Agent: 抱歉，我没有关于你名字的信息，
       能告诉我你怎么称呼吗？
  [当前对话：第 1 轮，共 2 条消息]

You : exit
[对话结束]
```

## 核心要点

| 组件 | 说明 |
|------|------|
| `ChatMessage` | 单条消息对象，包含 `role` 与 `content` |
| `MessageRole.USER` | 用户消息角色 |
| `MessageRole.ASSISTANT` | Agent 消息角色 |
| `history: list[ChatMessage]` | 本地维护的对话历史列表 |
| `agent.run(messages=history)` | 传入完整历史，Agent 感知上下文 |

## 历史管理策略

### 无限历史（默认）
```python
# 所有消息都保留
history.append(ChatMessage(...))
```

### 滑动窗口（控制 Token 消耗）
```python
MAX_TURNS = 10  # 最多保留 10 轮

def trim_history(history: list, max_turns: int) -> list:
    """只保留最近 N 轮对话"""
    max_messages = max_turns * 2  # 每轮 = user + assistant
    if len(history) > max_messages:
        return history[-max_messages:]
    return history

# 调用前裁剪
trimmed = trim_history(history, MAX_TURNS)
stream = await agent.run(messages=trimmed, stream=True)
```

### 系统摘要（长对话压缩）
```python
async def summarize_history(agent, history: list) -> str:
    """将历史压缩为摘要"""
    summary_prompt = "请用 100 字以内总结以下对话内容：\n"
    for msg in history:
        role = "用户" if msg.role == MessageRole.USER else "助手"
        summary_prompt += f"{role}：{msg.content}\n"

    result = await agent.run(summary_prompt)
    return result.text

# 历史过长时压缩
if len(history) > 20:
    summary = await summarize_history(agent, history[:-4])
    compressed = [
        ChatMessage(role=MessageRole.SYSTEM, content=f"对话摘要：{summary}")
    ]
    history = compressed + history[-4:]  # 摘要 + 最近 2 轮
```

## 消息结构

```python
# 完整的消息结构
ChatMessage(
    role=MessageRole.USER,       # USER / ASSISTANT / SYSTEM
    content="消息内容",           # 文本内容
)

# 对话历史示例
history = [
    ChatMessage(role=MessageRole.USER,      content="你好"),
    ChatMessage(role=MessageRole.ASSISTANT, content="你好！有什么可以帮你？"),
    ChatMessage(role=MessageRole.USER,      content="我叫李明"),
    ChatMessage(role=MessageRole.ASSISTANT, content="你好，李明！"),
]
```

## 与单轮对话对比

| 特性 | 单轮对话 | 多轮对话 |
|------|----------|----------|
| 上下文记忆 | ❌ 每次独立 | ✅ 携带历史 |
| Token 消耗 | 低 | 随轮次增加 |
| 连贯性 | ❌ 无法引用前文 | ✅ 可引用前文 |
| 适用场景 | 单次查询 | 交互式对话 |
