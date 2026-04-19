# Copyright (c) Microsoft. All rights reserved.
# Agent Safety - 分层安全机制

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, AgentMiddleware, AgentResponse
from agent_framework.openai import OpenAIChatCompletionClient


class InputSafetyMiddleware(AgentMiddleware):
    """输入安全过滤"""
    BLOCKED_PATTERNS = ["密码", "secret", "删除所有", "drop table"]

    async def process(self, context, call_next):
        for msg in context.input_messages:
            for pattern in self.BLOCKED_PATTERNS:
                if pattern.lower() in msg.text.lower():
                    return AgentResponse(
                        text="抱歉，我无法处理这类请求。"
                    )
        return await call_next()


class OutputSafetyMiddleware(AgentMiddleware):
    """输出安全过滤"""
    async def process(self, context, call_next):
        response = await call_next()

        # 简单检查（实际应该用更复杂的检测）
        if response.text and len(response.text) > 10000:
            return AgentResponse(
                text="响应过长，已截断。"
            )
        return response


class RateLimitMiddleware(AgentMiddleware):
    """速率限制"""
    def __init__(self):
        self.call_count = 0
        self.window_start = None

    async def process(self, context, call_next):
        import time
        current_time = time.time()

        if self.window_start is None:
            self.window_start = current_time

        # 1 分钟窗口内最多 10 次调用
        if current_time - self.window_start > 60:
            self.call_count = 0
            self.window_start = current_time

        self.call_count += 1

        if self.call_count > 10:
            return AgentResponse(
                text="请求过于频繁，请稍后再试。"
            )

        return await call_next()


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建带多层安全的 Agent
    agent = Agent(
        client=client,
        name="SafeAgent",
        instructions="你是一个乐于助人的助手。",
        middleware=[
            InputSafetyMiddleware(),
            RateLimitMiddleware(),
            OutputSafetyMiddleware(),
        ],
    )

    print("=" * 60)
    print("  Agent Safety Demo - 分层安全机制")
    print("=" * 60)

    # 测试输入安全
    print("\n--- 测试 1: 恶意输入检测 ---")
    response = await agent.run("我的密码是 123456")
    print(f"响应: {response.text}")

    # 正常对话
    print("\n--- 测试 2: 正常对话 ---")
    response = await agent.run("你好！")
    print(f"响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
