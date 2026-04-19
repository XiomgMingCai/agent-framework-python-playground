# Copyright (c) Microsoft. All rights reserved.
# Agent vs Run Scope - 中间件作用域

import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

from agent_framework import Agent, AgentMiddleware, AgentResponse
from agent_framework.openai import OpenAIChatCompletionClient


class AgentScopeMiddleware(AgentMiddleware):
    """Agent 作用域：跨调用共享状态"""
    def __init__(self):
        self.call_count = 0
        self.start_time = datetime.now()

    async def process(self, context, call_next):
        self.call_count += 1
        print(f"[AgentScope] 调用 #{self.call_count}")
        print(f"[AgentScope] 运行时间: {datetime.now() - self.start_time}")
        return await call_next()


class RunScopeMiddleware(AgentMiddleware):
    """Run 作用域：每次调用独立"""
    def __init__(self):
        self.run_id = 0

    async def process(self, context, call_next):
        self.run_id += 1
        print(f"[RunScope] 独立 Run ID: {self.run_id}")
        return await call_next()


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建 Agent
    agent = Agent(
        client=client,
        name="ScopeAgent",
        instructions="你是一个有帮助的助手。",
        middleware=[
            AgentScopeMiddleware(),  # 跨调用共享
            RunScopeMiddleware(),     # 每次独立
        ],
    )

    print("=" * 60)
    print("  Agent vs Run Scope Demo")
    print("=" * 60)

    # 第一次调用
    print("\n--- 第一次调用 ---")
    await asyncio.sleep(0.1)  # 确保时间差异
    response = await agent.run("你好")
    print(f"响应: {response.text[:50]}...")

    # 第二次调用
    print("\n--- 第二次调用 ---")
    await asyncio.sleep(0.1)
    response = await agent.run("今天天气如何？")
    print(f"响应: {response.text[:50]}...")


if __name__ == "__main__":
    asyncio.run(main())
