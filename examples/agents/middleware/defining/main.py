# Copyright (c) Microsoft. All rights reserved.
# Defining Middleware - 定义中间件

import asyncio
import os
import time

from dotenv import load_dotenv

from agent_framework import Agent, AgentMiddleware, FunctionMiddleware
from agent_framework.openai import OpenAIChatCompletionClient


class LoggingMiddleware(AgentMiddleware):
    """日志记录中间件"""

    async def process(self, context, call_next):
        print(f"[Agent] Before run: {len(context.input_messages)} messages")
        await call_next()
        print(f"[Agent] After run")


class TimingMiddleware(FunctionMiddleware):
    """工具调用计时中间件"""

    async def process(self, context, call_next):
        start = time.time()
        print(f"[Function] Calling {context.tool_name}...")
        await call_next()
        elapsed = time.time() - start
        print(f"[Function] {context.tool_name} took {elapsed:.3f}s")


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建带中间件的 Agent
    agent = Agent(
        client=client,
        name="MiddlewareAgent",
        instructions="你是一个有帮助的助手。",
        middleware=[LoggingMiddleware(), TimingMiddleware()],
    )

    print("=" * 60)
    print("  Defining Middleware Demo - 中间件定义")
    print("=" * 60)

    print("\n--- 调用 Agent ---")
    response = await agent.run("你好")
    print(f"\n响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
