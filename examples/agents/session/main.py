# Copyright (c) Microsoft. All rights reserved.
# Session - 多轮对话

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, Message
from agent_framework.openai import OpenAIChatCompletionClient


async def chat_loop():
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
        name="ChatAgent",
        instructions=(
            "你是一个友好的助手，能够记住对话历史并保持上下文连贯。"
        ),
    )

    # 对话历史
    history: list[Message] = []

    print("=" * 50)
    print("  多轮对话 Demo  (输入 'exit' 退出, 'clear' 清空历史)")
    print("=" * 50)

    while True:
        user_input = input("\nYou : ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "clear":
            history.clear()
            print("[对话历史已清空]")
            continue

        # 将用户消息加入历史
        history.append(Message(role="user", contents=[user_input]))

        # 流式调用，携带历史
        print("Agent: ", end="", flush=True)
        full_response = ""

        stream = await agent.run(messages=history, stream=True)

        async for update in stream:
            if update.contents:
                for content in update.contents:
                    if hasattr(content, 'text') and content.text:
                        print(content.text, end="", flush=True)
                        full_response += content.text

        print()

        if full_response:
            history.append(Message(role="assistant", contents=[full_response]))

        turns = len(history) // 2
        print(f"  [当前对话：第 {turns} 轮，共 {len(history)} 条消息]")


if __name__ == "__main__":
    asyncio.run(chat_loop())
