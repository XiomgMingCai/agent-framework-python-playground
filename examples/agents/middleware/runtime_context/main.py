# Copyright (c) Microsoft. All rights reserved.
# Runtime Context - 运行时上下文

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, AgentMiddleware, AgentResponse
from agent_framework.openai import OpenAIChatCompletionClient


class ContextInspectorMiddleware(AgentMiddleware):
    """上下文检查中间件"""
    async def process(self, context, call_next):
        print("\n=== Runtime Context 检查 ===")

        # 检查输入消息
        print(f"输入消息数: {len(context.input_messages)}")
        if context.input_messages:
            last = context.input_messages[-1]
            print(f"最后输入类型: {type(last).__name__}")
            print(f"最后输入内容: {last.text[:50]}...")

        # 检查 metadata
        print(f"Metadata 键: {list(context.metadata.keys())}")

        # 检查 state
        print(f"State 键: {list(context.state.keys())}")

        return await call_next()


class InputAnalyzerMiddleware(AgentMiddleware):
    """输入分析中间件"""
    async def process(self, context, call_next):
        if context.input_messages:
            last_input = context.input_messages[-1].text
            word_count = len(last_input.split())

            print(f"\n=== Input Analysis ===")
            print(f"字数: {word_count}")

            # 拒绝过长输入
            if word_count > 100:
                print("输入过长，拒绝处理")
                return AgentResponse(text="输入过长，请缩短您的问题。")

        return await call_next()


class ResponseEnhancerMiddleware(AgentMiddleware):
    """响应增强中间件"""
    async def process(self, context, call_next):
        response = await call_next()

        # 添加元数据
        context.metadata["processed_by"] = "ResponseEnhancerMiddleware"
        context.metadata["model"] = getattr(response, "model", "unknown")

        print(f"\n=== Response Enhanced ===")
        print(f"响应长度: {len(response.text) if response.text else 0}")

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
        name="RuntimeContextAgent",
        instructions="你是一个有帮助的助手。",
        middleware=[
            InputAnalyzerMiddleware(),
            ContextInspectorMiddleware(),
            ResponseEnhancerMiddleware(),
        ],
    )

    print("=" * 60)
    print("  Runtime Context Demo - 运行时上下文")
    print("=" * 60)

    print("\n--- 测试: 正常对话 ---")
    response = await agent.run("你好，请介绍一下你自己")
    print(f"\n最终响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
