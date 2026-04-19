# Copyright (c) Microsoft. All rights reserved.
# Result Overrides - 结果覆盖

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, AgentMiddleware, AgentResponse
from agent_framework.openai import OpenAIChatCompletionClient


class CacheMiddleware(AgentMiddleware):
    """缓存覆盖"""
    def __init__(self):
        self.cache = {}

    async def process(self, context, call_next):
        # 用输入消息作为缓存键
        cache_key = str(context.input_messages[-1].text) if context.input_messages else ""

        if cache_key in self.cache:
            print(f"[Cache] 命中缓存: {cache_key[:30]}...")
            return self.cache[cache_key]

        response = await call_next()

        # 存入缓存
        self.cache[cache_key] = response
        print(f"[Cache] 存入缓存: {len(self.cache)} 条")

        return response


class FallbackMiddleware(AgentMiddleware):
    """Fallback 覆盖"""
    async def process(self, context, call_next):
        try:
            return await call_next()
        except Exception as e:
            print(f"[Fallback] 捕获异常: {e}")
            return AgentResponse(
                text="抱歉，服务暂时不可用，请稍后再试。"
            )


class ConditionalOverrideMiddleware(AgentMiddleware):
    """条件覆盖"""
    async def process(self, context, call_next):
        response = await call_next()

        # 特定输入返回固定响应
        if context.input_messages:
            last_input = context.input_messages[-1].text.lower()
            if "天气" in last_input:
                return AgentResponse(text="抱歉，我无法访问天气数据。")

        return response


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    agent = Agent(
        client=client,
        name="OverrideAgent",
        instructions="你是一个有帮助的助手。",
        middleware=[
            CacheMiddleware(),
            ConditionalOverrideMiddleware(),
        ],
    )

    print("=" * 60)
    print("  Result Overrides Demo - 结果覆盖")
    print("=" * 60)

    # 测试缓存
    print("\n--- 测试 1: 缓存 ---")
    response = await agent.run("你好")
    print(f"响应: {response.text}")

    print("\n--- 测试 2: 缓存命中 ---")
    response = await agent.run("你好")  # 同样的输入
    print(f"响应: {response.text}")

    # 测试条件覆盖
    print("\n--- 测试 3: 条件覆盖 ---")
    response = await agent.run("今天天气如何？")
    print(f"响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
