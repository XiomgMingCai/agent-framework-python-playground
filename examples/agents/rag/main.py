# Copyright (c) Microsoft. All rights reserved.
# RAG - 检索增强生成

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent, ContextProvider, SessionContext
from agent_framework.openai import OpenAIChatCompletionClient


class SimpleRAGProvider(ContextProvider):
    """简化版 RAG Provider"""

    def __init__(self, documents: list[str]):
        super().__init__("rag")
        self.documents = documents

    async def before_run(self, *, agent, session, context: SessionContext, state: dict):
        # 从用户输入提取查询
        if not context.input_messages:
            return

        query = context.input_messages[-1].text if context.input_messages else ""

        # 检索相似文档（简化版：关键词匹配）
        relevant_docs = self._retrieve(query, top_k=2)

        # 注入检索结果到 Context
        if relevant_docs:
            context.extend_instructions(
                self.source_id,
                f"基于以下参考信息回答用户问题：\n{relevant_docs}\n如果参考信息不相关，请基于你的知识回答。"
            )

    def _retrieve(self, query: str, top_k: int) -> str:
        """简化版检索：关键词匹配"""
        if not query:
            return ""

        keywords = query.split()[:5]
        scored = []
        for doc in self.documents:
            score = sum(1 for kw in keywords if kw in doc)
            if score > 0:
                scored.append((score, doc))

        scored.sort(reverse=True)
        results = [doc for _, doc in scored[:top_k]]
        return "\n---\n".join(results)


# 知识库
KNOWLEDGE_BASE = [
    "Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年创建。",
    "Python 以其简洁易读的语法著称，适合初学者学习编程。",
    "Microsoft Agent Framework 是微软开发的 Agent 开发框架，支持 Python 和 JavaScript。",
    "Agent Framework 中的 ContextProvider 允许自定义上下文管理。",
    "Workflow 是 Agent Framework 中编排多步骤任务的核心概念。",
]


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建带 RAG 的 Agent
    agent = Agent(
        client=client,
        name="RAGAgent",
        instructions="你是一个问答助手。基于提供的参考信息回答问题，保持简洁。",
        context_providers=[SimpleRAGProvider(KNOWLEDGE_BASE)],
    )

    print("=" * 60)
    print("  RAG Demo - 检索增强生成")
    print("=" * 60)

    # 问题 1：关于 Python
    print("\n--- 问题 1: Python 是谁创建的？---")
    response = await agent.run("Python 是谁创建的？")
    print(f"Agent: {response.text}")

    # 问题 2：关于 Agent Framework
    print("\n--- 问题 2: Agent Framework 是什么？---")
    response = await agent.run("Agent Framework 是什么？")
    print(f"Agent: {response.text}")

    # 问题 3：不在知识库中的问题
    print("\n--- 问题 3: 今天天气怎么样？（知识库外）---")
    response = await agent.run("今天天气怎么样？")
    print(f"Agent: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
