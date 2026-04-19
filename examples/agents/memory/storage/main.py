# Copyright (c) Microsoft. All rights reserved.
# Memory Storage - 存储后端

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, Memory
from agent_framework.openai import OpenAIChatCompletionClient


class InMemoryStorage:
    """内存存储（开发测试用）"""
    def __init__(self):
        self.data = {}

    async def add(self, key: str, value: str):
        self.data[key] = value

    async def get(self, key: str) -> str:
        return self.data.get(key)

    async def search(self, query: str) -> list:
        # 简化搜索：关键词匹配
        results = [
            (k, v) for k, v in self.data.items()
            if query.lower() in v.lower()
        ]
        return results


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建内存存储
    storage = InMemoryStorage()

    # 存储一些数据
    await storage.add("user_prefs", "用户偏好：简洁回答")
    await storage.add("user_lang", "中文")
    await storage.add("user_theme", "深色模式")

    print("=" * 60)
    print("  Memory Storage Demo - 存储后端")
    print("=" * 60)

    # 读取数据
    print("\n--- 读取数据 ---")
    prefs = await storage.get("user_prefs")
    print(f"用户偏好: {prefs}")

    lang = await storage.get("user_lang")
    print(f"语言: {lang}")

    # 搜索数据
    print("\n--- 搜索 '用户' ---")
    results = await storage.search("用户")
    for key, value in results:
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
