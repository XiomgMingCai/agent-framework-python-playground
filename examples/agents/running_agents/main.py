# Copyright (c) Microsoft. All rights reserved.
# Running Agents - 运行 Agent

import asyncio
import os
import argparse

from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient


async def demo_streaming(prompt: str):
    """演示流式输出"""
    print("\n=== 流式输出演示 ===\n")

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL")
    )

    agent = Agent(
        client=client,
        name="StreamingAgent",
        instructions="You are a helpful assistant. Use Chinese to respond."
    )

    print(f"User: {prompt}")
    print("Agent: ", end="", flush=True)

    stream = await agent.run(prompt, stream=True)

    async for update in stream:
        if update.contents:
            for content in update.contents:
                if content.text:
                    print(content.text, end="", flush=True)

    await stream.get_final_response()
    print()


async def demo_non_streaming(prompt: str):
    """演示非流式输出"""
    print("\n=== 非流式输出演示 ===\n")

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL")
    )

    agent = Agent(
        client=client,
        name="NonStreamingAgent",
        instructions="You are a helpful assistant. Use Chinese to respond."
    )

    print(f"User: {prompt}")
    result = await agent.run(prompt)
    print(f"Agent: {result.text}")


async def main():
    parser = argparse.ArgumentParser(description="Running Agents Demo")
    parser.add_argument("-p", "--prompt", type=str, required=True, help="输入提示")
    parser.add_argument("--streaming", action="store_true", help="使用流式输出")
    args = parser.parse_args()

    load_dotenv()

    if args.streaming:
        await demo_streaming(args.prompt)
    else:
        await demo_non_streaming(args.prompt)


if __name__ == "__main__":
    asyncio.run(main())
