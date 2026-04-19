# Copyright (c) Microsoft. All rights reserved.
# A2A Client - 使用 A2AAgent 连接远程 A2A 服务端

import asyncio
import httpx
from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent


async def main():
    a2a_host = "http://127.0.0.1:8080"

    print("=" * 60)
    print("  A2A Client Demo - 连接 A2A 服务端")
    print("=" * 60)

    # ========== 1. 发现 Agent ==========
    print("\n--- Step 1: 发现远程 Agent ---")
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        resolver = A2ACardResolver(httpx_client=http_client, base_url=a2a_host)
        agent_card = await resolver.get_agent_card()
        print(f"发现 Agent: {agent_card.name}")
        print(f"描述: {agent_card.description}")
        print(f"版本: {agent_card.version}")
        print(f"能力: {agent_card.capabilities}")

    # ========== 2. 非流式对话 ==========
    print("\n--- Step 2: 非流式对话 ---")
    async with A2AAgent(
        name=agent_card.name,
        agent_card=agent_card,
        url=a2a_host,
    ) as agent:
        print("发送: 你好，请介绍一下你自己")
        response = await agent.run("你好，请介绍一下你自己")
        print(f"收到: {response.text}")

    # ========== 3. 流式对话 ==========
    print("\n--- Step 3: 流式对话 ---")
    async with A2AAgent(
        name=agent_card.name,
        agent_card=agent_card,
        url=a2a_host,
    ) as agent:
        print("发送: 用三句话讲一个关于星星的故事")
        print("收到: ", end="", flush=True)

        stream = agent.run("用三句话讲一个关于星星的故事", stream=True)
        async for update in stream:
            for content in update.contents:
                if hasattr(content, 'text') and content.text:
                    print(content.text, end="", flush=True)

        final = await stream.get_final_response()
        print(f"\n(共 {len(final.messages)} 条消息)")

    # ========== 4. 多轮对话 ==========
    print("\n--- Step 4: 多轮对话 (使用 contextId) ---")
    context_id = "test-context-123"

    async with A2AAgent(
        name=agent_card.name,
        agent_card=agent_card,
        url=a2a_host,
    ) as agent:
        # 第一轮
        print("轮次 1 - 发送: 我喜欢蓝色")
        response1 = await agent.run("我喜欢蓝色", context_id=context_id)
        print(f"收到: {response1.text}")

        # 第二轮（同一 contextId）
        print("轮次 2 - 发送: 为什么我会喜欢这个颜色？")
        response2 = await agent.run("为什么我会喜欢这个颜色？", context_id=context_id)
        print(f"收到: {response2.text}")

        # 第三轮
        print("轮次 3 - 发送: 这种颜色在设计中常用来表达什么？")
        response3 = await agent.run("这种颜色在设计中常用来表达什么？", context_id=context_id)
        print(f"收到: {response3.text}")

    print("\n" + "=" * 60)
    print("  A2A Client Demo 完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())