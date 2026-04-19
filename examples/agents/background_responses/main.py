# Copyright (c) Microsoft. All rights reserved.
# Background Responses - 后台响应处理

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient


async def run_in_background(agent, query, session):
    """将 agent.run() 放入后台任务执行"""
    return asyncio.create_task(agent.run(query, session=session))


async def demo_background_task():
    """演示后台任务"""
    print("\n=== 模拟后台任务 ===\n")

    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    agent = Agent(client=client, name="Researcher", instructions="你是研究助手。")
    session = agent.create_session()

    query = "详细解释量子纠缠原理"

    # 1. 启动后台任务
    print(f"启动后台任务: {query[:20]}...")
    task = await run_in_background(agent, query, session)

    # 2. 主线程继续执行其他工作（不阻塞）
    print("主线程继续执行其他工作...")
    await asyncio.sleep(1)

    # 3. 轮询等待后台任务完成
    print("等待后台任务完成...")
    while not task.done():
        await asyncio.sleep(1)
        print(f"  [仍在运行中...]")

    # 4. 获取结果
    response = task.result()
    print(f"\n后台任务完成！")
    print(f"响应: {response.text[:100]}...")


async def demo_streaming_with_breakpoint():
    """演示流式响应 + 模拟断点续传"""
    print("\n=== 流式响应 + 模拟断点续传 ===\n")

    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    agent = Agent(client=client, name="StoryTeller", instructions="你是一个讲故事的人。")
    session = agent.create_session()

    query = "用三句话讲一个关于机器人的温馨故事"

    # 开始流式接收
    print("开始流式接收:")
    stream = agent.run(query, stream=True, session=session)
    received = ""
    chunk_count = 0

    async for update in stream:
        if update.text:
            print(update.text, end="", flush=True)
            received += update.text
        chunk_count += 1
        # 模拟收到几个 chunk 后网络中断
        if chunk_count >= 2:
            print("\n[模拟网络中断，保存已接收内容]")
            break

    # 从断点继续
    print("[模拟恢复，继续生成...]")
    stream2 = agent.run(query, stream=True, session=session)
    async for update in stream2:
        if update.text:
            print(update.text, end="", flush=True)


async def main():
    print("=" * 60)
    print("  Background Responses Demo - 后台响应处理")
    print("=" * 60)

    await demo_background_task()
    await demo_streaming_with_breakpoint()


if __name__ == "__main__":
    asyncio.run(main())
