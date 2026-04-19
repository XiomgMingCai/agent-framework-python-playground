# Copyright (c) Microsoft. All rights reserved.
# Multimodal - 多模态输入输出

import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建支持多模态的 Agent
    agent = Agent(
        client=client,
        name="MultimodalAgent",
        instructions="你是一个视觉助手，可以描述图像内容。",
    )

    print("=" * 60)
    print("  Multimodal Demo - 多模态支持")
    print("=" * 60)

    # 文本输入（基础对话）
    print("\n--- 测试 1: 文本对话 ---")
    response = await agent.run("你好，你是什么类型的 Agent？")
    print(f"Agent: {response.text}")

    # 多模态输入示例（伪代码，实际需要图片URL）
    # 在实际环境中，可以使用图像URL
    print("\n--- 多模态输入说明 ---")
    print("多模态消息格式:")
    print('  message = {')
    print('      "role": "user",')
    print('      "content": [')
    print('          {"type": "text", "text": "描述这张图片"},')
    print('          {"type": "image_url", "url": "https://..."}')
    print('      ]')
    print('  }')

    # 响应结构说明
    print("\n--- 响应结构说明 ---")
    print("多模态响应可能包含:")
    print("  - response.text: 文本响应")
    print("  - response.image: 图像数据（如有）")
    print("  - response.audio: 音频数据（如有）")


if __name__ == "__main__":
    asyncio.run(main())
