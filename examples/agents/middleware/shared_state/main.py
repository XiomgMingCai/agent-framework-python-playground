# Copyright (c) Microsoft. All rights reserved.
# Shared State - 状态共享

import asyncio
import os
import uuid

from dotenv import load_dotenv

from agent_framework import Agent, AgentMiddleware, AgentResponse
from agent_framework.openai import OpenAIChatCompletionClient


class RequestIDMiddleware(AgentMiddleware):
    """请求 ID 中间件"""
    async def process(self, context, call_next):
        request_id = str(uuid.uuid4())
        context.state["request_id"] = request_id
        print(f"[RequestID] 生成请求 ID: {request_id}")
        return await call_next()


class UserContextMiddleware(AgentMiddleware):
    """用户上下文中间件"""
    async def process(self, context, call_next):
        # 读取前置中间件设置的 request_id
        request_id = context.state.get("request_id", "unknown")
        print(f"[UserContext] 处理请求: {request_id}")

        # 添加用户上下文
        context.state["user"] = {"id": "user_123", "tier": "premium"}
        context.state["timestamp"] = str(asyncio.get_event_loop().time())

        return await call_next()


class LoggingMiddleware(AgentMiddleware):
    """日志中间件 - 读取前置中间件的数据"""
    async def process(self, context, call_next):
        request_id = context.state.get("request_id", "unknown")
        user = context.state.get("user", {})

        print(f"[Logging] 请求 {request_id}, 用户 {user.get('id', 'anonymous')}")

        result = await call_next()

        print(f"[Logging] 请求 {request_id} 完成")
        return result


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 中间件按顺序执行，前面的设置可以被后面读取
    agent = Agent(
        client=client,
        name="SharedStateAgent",
        instructions="你是一个有帮助的助手。",
        middleware=[
            RequestIDMiddleware(),    # 1. 设置 request_id
            UserContextMiddleware(),  # 2. 读取 request_id，添加 user
            LoggingMiddleware(),       # 3. 读取 request_id 和 user
        ],
    )

    print("=" * 60)
    print("  Shared State Demo - 状态共享")
    print("=" * 60)

    print("\n--- 测试 ---")
    response = await agent.run("你好")
    print(f"响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
