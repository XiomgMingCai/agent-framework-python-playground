# Copyright (c) Microsoft. All rights reserved.
# Agents in Workflows - 在工作流中嵌入 Agent
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/agents-in-workflows

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
    AgentExecutor,
    Agent,
)
from agent_framework.openai import OpenAIChatCompletionClient


# ========== 1. 准备 Agent Client ==========

def create_client():
    load_dotenv()
    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model = os.getenv("AI_MODEL")

    if not all([api_key, base_url, model]):
        print("警告: 环境变量未配置，跳过实际 API 调用")
        return None

    return OpenAIChatCompletionClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )


# ========== 2. 预处理 Executor ==========

class TextPreprocessor(Executor):
    """预处理输入文本"""

    def __init__(self, id: str = "preprocessor"):
        super().__init__(id=id)

    @handler
    async def preprocess(self, text: str, ctx: WorkflowContext[str]) -> None:
        # 清理和标准化文本
        cleaned = text.strip().replace("\n", " ")
        await ctx.send_message(cleaned)


# ========== 3. AgentExecutor 工作流 ==========

async def create_agent_workflow():
    """创建带有 Agent 的工作流"""
    client = create_client()

    if client is None:
        return None

    # 创建 Agent
    agent = Agent(
        client=client,
        name="WorkflowAI",
        instructions="你是一个助手，负责将用户输入翻译成英文。只需返回翻译结果，不要其他解释。",
    )

    # 创建 AgentExecutor
    agent_executor = AgentExecutor(agent=agent)

    # 构建工作流
    preprocessor = TextPreprocessor()

    workflow = (
        WorkflowBuilder(start_executor=preprocessor)
        .add_edge(preprocessor, agent_executor)
        .build()
    )

    return workflow


# ========== 4. 简单 Agent Executor ==========

def simple_agent_executor_demo():
    """演示简单的 AgentExecutor 用法"""
    print("\n--- AgentExecutor 演示 ---")

    client = create_client()
    if client is None:
        print("跳过: 环境变量未配置")
        return

    agent = Agent(
        client=client,
        name="SimpleAgent",
        instructions="用一句话介绍自己。",
    )

    agent_executor = AgentExecutor(agent=agent)

    # 直接运行 AgentExecutor - 通过 workflow 运行
    print("通过 Workflow 调用 AgentExecutor...")

    # 创建简单工作流
    workflow = (
        WorkflowBuilder(start_executor=agent_executor)
        .build()
    )

    print(f"工作流已创建: {workflow.name}")
    print(f"AgentExecutor 准备就绪: {agent_executor.id}")
    print("注意: 实际运行需要通过 workflow.run() 调用，这里仅演示结构")


# ========== 5. 多 Agent 协作 ==========

async def multi_agent_workflow():
    """演示多 Agent 协作工作流"""
    print("\n--- 多 Agent 协作演示 ---")

    client = create_client()
    if client is None:
        print("跳过: 环境变量未配置")
        return

    # Agent 1: 翻译成英文
    translator = Agent(
        client=client,
        name="Translator",
        instructions="将用户输入翻译成英文，只返回翻译结果。",
    )

    # Agent 2: 总结英文文本
    summarizer = Agent(
        client=client,
        name="Summarizer",
        instructions="将输入的英文文本总结为一句话。",
    )

    translator_executor = AgentExecutor(agent=translator)
    summarizer_executor = AgentExecutor(agent=summarizer)

    # 构建工作流: translator → summarizer
    workflow = (
        WorkflowBuilder(start_executor=translator_executor)
        .add_edge(translator_executor, summarizer_executor)
        .build()
    )

    print("运行多 Agent 工作流: 翻译 → 总结")
    result = await workflow.run("今天天气真好，适合出去散步")

    print(f"最终输出: {result.get_outputs()}")


# ========== 6. AgentExecutor 属性 ==========

def show_agent_executor_properties():
    """显示 AgentExecutor 的属性"""
    print("\n--- AgentExecutor 属性 ---")

    client = create_client()
    if client is None:
        print("跳过: 环境变量未配置")
        return

    agent = Agent(client=client, name="TestAgent", instructions="测试")
    agent_exec = AgentExecutor(agent=agent)

    print(f"AgentExecutor ID: {agent_exec.id}")
    print(f"input_types: {agent_exec.input_types}")
    print(f"output_types: {agent_exec.output_types}")
    print(f"workflow_output_types: {agent_exec.workflow_output_types}")
    print(f"agent: {agent_exec.agent.name}")


async def main():
    print("=" * 60)
    print("  Agents in Workflows 示例")
    print("=" * 60)

    # AgentExecutor 直接调用
    simple_agent_executor_demo()

    # 多 Agent 协作
    await multi_agent_workflow()

    # AgentExecutor 属性
    show_agent_executor_properties()

    print("\n" + "=" * 60)
    print("  Agents in Workflows 示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
