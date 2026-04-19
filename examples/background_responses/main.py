# Copyright (c) Microsoft. All rights reserved.
# Background Responses - 模拟后台响应模式
#
# 注意：background 和 continuation_token 是 OpenAI Responses API 的专属功能，
# OpenAIChatCompletionClient（Chat Completions API）不支持。
# 本示例使用 asyncio 模拟相同模式，在 Chat Completions API 上可正常运行。

import asyncio
import os
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient


async def run_in_background(agent: Agent, query: str, session):
    """在后台运行查询，模拟 Responses API 的 background 模式"""
    # 创建一个 future 代表后台任务
    async def background_task():
        response = await agent.run(query, session=session)
        return response

    task = asyncio.create_task(background_task())
    return task


async def demo_background_task():
    """模拟后台响应：使用 asyncio 实现后台任务"""

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    agent = Agent(
        client=client,
        name="Researcher",
        instructions="你是一个有帮助的研究助手。",
    )

    session = agent.create_session()

    print("--- 模拟后台任务 ---")
    query = "详细解释量子纠缠原理，包括贝尔不等式的意义"

    # 启动后台任务
    print(f"启动后台任务: {query[:20]}...")
    task = await run_in_background(agent, query, session)

    # 模拟主线程继续执行其他工作
    print("主线程继续执行其他工作...")
    await asyncio.sleep(1)
    print("主线程工作完成")

    # 等待后台任务完成并获取结果
    print("等待后台任务完成...")
    while not task.done():
        await asyncio.sleep(1)
        print(f"  [仍在运行中...]")

    response = task.result()
    print(f"\n后台任务完成！\n响应: {response.text[:100]}...")


async def demo_streaming_with_simulated_breakpoint():
    """流式响应 + 模拟断点续传"""

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    agent = Agent(
        client=client,
        name="StoryTeller",
        instructions="你是一个讲故事的高手。",
    )

    session = agent.create_session()

    print("\n--- 流式响应 + 模拟断点续传 ---")

    query = "用三句话讲一个关于机器人的温馨故事"

    print("开始流式接收:")
    stream = agent.run(query, stream=True, session=session)

    received_text = ""
    chunk_count = 0
    async for update in stream:
        if update.text:
            print(update.text, end="", flush=True)
            received_text += update.text
        chunk_count += 1
        # 模拟收到几个 chunk 后中断（类似网络断开）
        if chunk_count >= 2:
            print("\n[模拟网络中断，保存已接收内容]")
            break

    # 模拟从断点继续：重新发送完整 query
    print(f"\n[模拟恢复：使用已保存的 context 继续生成]")
    print("继续生成:")
    stream2 = agent.run(query, stream=True, session=session)

    async for update in stream2:
        if update.text:
            print(update.text, end="", flush=True)


async def main():
    load_dotenv()

    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model = os.getenv("AI_MODEL")

    if not all([api_key, base_url, model]):
        raise ValueError("请在 .env 中配置 AI_API_KEY、AI_BASE_URL、AI_MODEL")

    print("=" * 60)
    print("  Background Responses Demo - 后台响应处理")
    print("=" * 60)

    await demo_background_task()
    await demo_streaming_with_simulated_breakpoint()


if __name__ == "__main__":
    asyncio.run(main())