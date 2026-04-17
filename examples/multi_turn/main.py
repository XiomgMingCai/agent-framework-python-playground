import asyncio
import os
from dotenv import load_dotenv

from agent_framework import Agent, Message
from agent_framework.openai import OpenAIChatCompletionClient


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
    history: list[Message] = []

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

        # ── 将用户消息加入历史 ───────────────────────────
        history.append(
            Message(role="user", contents=[user_input])
        )

        # ── 流式调用，携带历史 ───────────────────────────
        print("Agent: ", end="", flush=True)

        full_response = ""

        stream = await agent.run(
            messages=history,   # 传入完整历史
            stream=True,
        )

        async for update in stream:
            if update.contents:
                for content in update.contents:
                    if hasattr(content, 'text') and content.text:
                        print(content.text, end="", flush=True)
                        full_response += content.text

        print()  # 换行

        # ── 将 Agent 回复加入历史 ─────────────────────────
        if full_response:
            history.append(
                Message(role="assistant", contents=[full_response])
            )

        # ── 显示当前历史轮数 ──────────────────────────────
        turns = len(history) // 2
        print(f"  [当前对话：第 {turns} 轮，共 {len(history)} 条消息]")


def _print_history(history: list[Message]):
    """打印对话历史摘要"""
    if not history:
        print("  [历史为空]")
        return

    print("\n─── 对话历史 ───")
    for i, msg in enumerate(history, 1):
        role = "You  " if msg.role == "user" else "Agent"
        # 获取文本内容
        content_text = ""
        if msg.contents:
            for c in msg.contents:
                if hasattr(c, 'text') and c.text:
                    content_text += c.text
                elif isinstance(c, str):
                    content_text += c
        # 超过 80 字符截断显示
        text = content_text if len(content_text) <= 80 else content_text[:80] + "..."
        print(f"  {i:02d}. [{role}] {text}")
    print("────────────────")


if __name__ == "__main__":
    asyncio.run(chat_loop())
