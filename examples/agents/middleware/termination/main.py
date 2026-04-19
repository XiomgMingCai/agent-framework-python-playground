# Copyright (c) Microsoft. All rights reserved.
# Termination - 优雅停止

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, AgentMiddleware, AgentResponse
from agent_framework.openai import OpenAIChatCompletionClient


class TimeoutMiddleware(AgentMiddleware):
    """超时终止"""
    def __init__(self, timeout_seconds: int = 5):
        self.timeout = timeout_seconds

    async def process(self, context, call_next):
        try:
            result = await asyncio.wait_for(
                call_next(),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            print("[Termination] 执行超时")
            return AgentResponse(
                text="抱歉，请求超时了。"
            )


class MaxIterationsMiddleware(AgentMiddleware):
    """最大迭代次数终止"""
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.iteration_count = 0

    async def process(self, context, call_next):
        self.iteration_count += 1
        print(f"[Termination] 迭代 #{self.iteration_count}/{self.max_iterations}")

        if self.iteration_count > self.max_iterations:
            print("[Termination] 达到最大迭代次数")
            return AgentResponse(
                text="已达到最大处理次数。"
            )

        return await call_next()


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建带终止中间件的 Agent
    agent = Agent(
        client=client,
        name="TerminationAgent",
        instructions="你是一个有帮助的助手。",
        middleware=[
            MaxIterationsMiddleware(max_iterations=2),
        ],
    )

    print("=" * 60)
    print("  Termination Demo - 优雅停止")
    print("=" * 60)

    print("\n--- 测试 ---")
    response = await agent.run("你好")
    print(f"响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
