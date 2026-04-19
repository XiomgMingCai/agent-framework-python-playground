# Copyright (c) Microsoft. All rights reserved.
# Context Providers - 上下文提供者

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, ContextProvider, SessionContext
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


async def chat_loop():
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
            "你是一个友好的助手，擅长记住用户的重要信息和偏好。"
            "当用户提供重要信息时，应该回复类似 '我记住了...' 的确认。"
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
    asyncio.run(chat_loop())
