# Copyright (c) Microsoft. All rights reserved.
# Exception Handling - 异常处理

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, AgentMiddleware, AgentResponse
from agent_framework.openai import OpenAIChatCompletionClient


class ErrorHandlingMiddleware(AgentMiddleware):
    """异常处理中间件"""

    async def process(self, context, call_next):
        try:
            return await call_next()
        except ValueError as e:
            # 值错误：可修复
            print(f"[ErrorHandling] ValueError: {e}")
            return AgentResponse(text=f"输入值错误: {e}")
        except TimeoutError as e:
            # 超时错误：可重试
            print(f"[ErrorHandling] TimeoutError: {e}")
            return AgentResponse(text="请求超时，请重试。")
        except Exception as e:
            # 未知错误：记录并转换
            print(f"[ErrorHandling] Unexpected: {type(e).__name__}: {e}")
            return AgentResponse(text="抱歉，发生未知错误。")


class MetricsMiddleware(AgentMiddleware):
    """指标收集中间件"""
    def __init__(self):
        self.counters = {"success": 0, "error": 0}

    async def process(self, context, call_next):
        try:
            result = await call_next()
            self.counters["success"] += 1
            return result
        except Exception:
            self.counters["error"] += 1
            raise
        finally:
            print(f"[Metrics] success={self.counters['success']}, error={self.counters['error']}")


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    agent = Agent(
        client=client,
        name="ExceptionAgent",
        instructions="你是一个有帮助的助手。",
        middleware=[
            MetricsMiddleware(),
            ErrorHandlingMiddleware(),
        ],
    )

    print("=" * 60)
    print("  Exception Handling Demo - 异常处理")
    print("=" * 60)

    print("\n--- 测试: 正常对话 ---")
    response = await agent.run("你好")
    print(f"响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
