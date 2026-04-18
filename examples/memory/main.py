# Copyright (c) Microsoft. All rights reserved.
# Interactive Memory Demo with conversation-style output

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
        self,
        *,
        agent,  # type: ignore
        session: AgentSession | None,
        context: SessionContext,
        state: dict,
    ) -> None:
        """在调用前注入记忆上下文"""
        memories = state.get("memories", [])
        if memories:
            memory_context = "\n".join([f"- {m}" for m in memories[-5:]])  # 最近 5 条
            context.extend_instructions(
                self.source_id,
                f"🧠 相关记忆上下文：\n{memory_context}\n根据记忆上下文回答用户问题。",
            )

    async def after_run(
        self,
        *,
        agent,  # type: ignore
        session: AgentSession | None,
        context: SessionContext,
        state: dict,
    ) -> None:
        """在调用后存储对话内容"""
        memories = state.setdefault("memories", [])

        # 存储用户输入
        for msg in context.input_messages:
            text = getattr(msg, "text", "") or ""
            if isinstance(text, str) and text.strip():
                # 避免重复存储
                if not any(text[:50] in m for m in memories):
                    memories.append(f"用户: {text[:100]}")


async def main():
    load_dotenv()

    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model = os.getenv("AI_MODEL")

    if not all([api_key, base_url, model]):
        raise ValueError("请在 .env 中配置 AI_API_KEY、AI_BASE_URL、AI_MODEL")

    client = OpenAIChatCompletionClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
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
    print(f"Session ID: {session.session_id}\n")

    print("=" * 60)
    print("  Memory Agent 交互模式")
    print("  输入消息与 Agent 对话，输入 'stats' 查看统计，'exit' 退出")
    print("=" * 60)

    message_count = 0

    while True:
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

        if user_input.lower() == "stats":
            provider_state = session.state.get("memory", {})
            memories = provider_state.get("memories", [])
            print(f"\n📊 知识库统计：{{'total_memories': {len(memories)}, 'conversation_messages': {message_count}}}")
            print(f"📝 当前会话：{message_count} 条消息\n")
            continue

        message_count += 1

        print("Agent: ", end="", flush=True)
        stream = await agent.run(user_input, session=session, stream=True)
        full_response = ""

        async for update in stream:
            if update.contents:
                for content in update.contents:
                    if hasattr(content, "text") and content.text:
                        print(content.text, end="", flush=True)
                        full_response += content.text

        print(f"\n📚 已存储记忆：{user_input[:50]}...\n")

        message_count += 1


if __name__ == "__main__":
    asyncio.run(main())
