# Copyright (c) Microsoft. All rights reserved.
# Memory Compaction - 内存压缩

import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

from agent_framework import Agent, Memory
from agent_framework.openai import OpenAIChatCompletionClient


class CompactionStrategy:
    """压缩策略：合并历史消息为摘要"""

    def __init__(self, threshold: int = 5):
        self.threshold = threshold

    async def should_compact(self, messages: list) -> bool:
        return len(messages) >= self.threshold

    async def compact(self, messages: list) -> dict:
        """将多条消息压缩为摘要"""
        # 简化实现：提取关键信息
        summary = {
            "type": "compacted",
            "original_count": len(messages),
            "time_range": f"{messages[0].get('time', 'unknown')} - {messages[-1].get('time', 'unknown')}",
            "topics": self._extract_topics(messages),
        }
        return summary

    def _extract_topics(self, messages: list) -> list:
        """提取话题"""
        topics = set()
        for msg in messages:
            content = msg.get("content", "")
            # 简化：取第一条消息的开头几个词
            if content:
                topics.add(content[:20] + "...")
        return list(topics)[:3]


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建压缩策略
    compaction = CompactionStrategy(threshold=5)

    print("=" * 60)
    print("  Memory Compaction Demo - 内存压缩")
    print("=" * 60)

    # 模拟消息历史
    messages = [
        {"content": "我想了解 Python 编程", "time": "10:00"},
        {"content": "Python 是一种高级语言", "time": "10:01"},
        {"content": "它有什么特点？", "time": "10:02"},
        {"content": "语法简洁易读", "time": "10:03"},
        {"content": "适合初学者", "time": "10:04"},
    ]

    print(f"\n--- 原始消息数: {len(messages)} ---")
    for msg in messages:
        print(f"  {msg['time']}: {msg['content']}")

    # 检查是否需要压缩
    should_compact = await compaction.should_compact(messages)
    print(f"\n需要压缩: {should_compact}")

    if should_compact:
        summary = await compaction.compact(messages)
        print(f"\n--- 压缩结果 ---")
        print(f"类型: {summary['type']}")
        print(f"原始消息数: {summary['original_count']}")
        print(f"时间范围: {summary['time_range']}")
        print(f"话题: {summary['topics']}")


if __name__ == "__main__":
    asyncio.run(main())
