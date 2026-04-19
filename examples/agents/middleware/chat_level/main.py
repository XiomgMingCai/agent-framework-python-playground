# Copyright (c) Microsoft. All rights reserved.
# Chat-Level Middleware - 消息级别中间件

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, AgentMiddleware, AgentResponse
from agent_framework.openai import OpenAIChatCompletionClient


class InputFilterMiddleware(AgentMiddleware):
    """输入过滤：敏感词替换"""

    async def process(self, context, call_next):
        for msg in context.input_messages:
            original = msg.text
            # 敏感词替换
            msg.text = msg.text.replace("密码", "***")
            if msg.text != original:
                print(f"[过滤] '{original}' -> '{msg.text}'")
        return await call_next()


class OutputTransformMiddleware(AgentMiddleware):
    """输出转换：添加格式"""

    async def process(self, context, call_next):
        response = await call_next()
        if response.text:
            # 添加引用格式
            response.text = f"> {response.text}"
        return response


class AuditLogMiddleware(AgentMiddleware):
    """审计日志：记录对话"""

    async def process(self, context, call_next):
        print(f"[审计] 输入消息数: {len(context.input_messages)}")
        if context.input_messages:
            print(f"[审计] 最后输入: {context.input_messages[-1].text[:50]}...")
        response = await call_next()
        print(f"[审计] 输出长度: {len(response.text) if response.text else 0}")
        return response


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建带 Chat-Level 中间件的 Agent
    agent = Agent(
        client=client,
        name="ChatMiddlewareAgent",
        instructions="你是一个有帮助的助手。",
        middleware=[
            InputFilterMiddleware(),
            AuditLogMiddleware(),
            OutputTransformMiddleware(),
        ],
    )

    print("=" * 60)
    print("  Chat-Level Middleware Demo - 消息级别")
    print("=" * 60)

    # 测试输入过滤
    print("\n--- 测试 1: 输入过滤 ---")
    response = await agent.run("我的密码是 123456")
    print(f"响应: {response.text}")

    # 正常对话
    print("\n--- 测试 2: 正常对话 ---")
    response = await agent.run("你好")
    print(f"响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
