# Copyright (c) Microsoft. All rights reserved.
# Executors - 工作流的执行单元
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/executors

import asyncio
from typing import Any

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
    AgentExecutor,
    WorkflowExecutor,
    Agent,
)
from agent_framework.openai import OpenAIChatCompletionClient


# ========== 1. 类定义 Executor ==========

class UpperCase(Executor):
    """将输入转换为大写"""

    def __init__(self, id: str = "upper_case"):
        super().__init__(id=id)

    @handler
    async def to_upper_case(self, text: str, ctx: WorkflowContext[str]) -> None:
        """接收文本，转大写后发送到下一个节点"""
        await ctx.send_message(text.upper())


class AddPrefix(Executor):
    """添加前缀"""

    def __init__(self, id: str = "add_prefix", prefix: str = "[PREFIX] "):
        super().__init__(id=id)
        self.prefix = prefix

    @handler
    async def add_prefix(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(self.prefix + text)


# ========== 2. 函数定义 Executor ==========

@executor(id="reverse_text")
async def reverse_text(text: str, ctx: WorkflowContext[str]) -> None:
    """翻转字符串并输出"""
    await ctx.yield_output(text[::-1])


@executor(id="append_suffix")
async def append_suffix(text: str, ctx: WorkflowContext[str]) -> None:
    """添加后缀并继续传递"""
    await ctx.send_message(text + " <end>")


# ========== 3. AgentExecutor 示例 ==========

async def create_agent_executor() -> AgentExecutor:
    """创建嵌入工作流的 AgentExecutor"""
    client = OpenAIChatCompletionClient(
        api_key="dummy-key",
        base_url="http://localhost:9999",  # 不可用，仅演示结构
        model="dummy",
    )
    agent = Agent(name="WorkflowAgent", client=client, instructions="你是一个有帮助的助手")
    return AgentExecutor(agent=agent)


# ========== 4. Executor 属性说明 ==========

def explain_executor_properties():
    """演示 Executor 的重要属性"""
    ex = UpperCase()

    print("=== Executor 属性 ===")
    print(f"input_types: {ex.input_types}")
    print(f"output_types: {ex.output_types}")
    print(f"workflow_output_types: {ex.workflow_output_types}")


# ========== 5. 构建工作流示例 ==========

def create_simple_workflow():
    """构建简单工作流: UpperCase → reverse_text"""
    upper = UpperCase()
    return WorkflowBuilder(start_executor=upper).add_edge(upper, reverse_text).build()


def create_chain_workflow():
    """构建链式工作流: UpperCase → AddPrefix → append_suffix"""
    upper = UpperCase()
    prefix = AddPrefix(prefix="【标签】")
    suffix = append_suffix

    return (
        WorkflowBuilder(start_executor=upper)
        .add_edge(upper, prefix)
        .add_edge(prefix, suffix)
        .build()
    )


# ========== 6. 使用 response_handler ==========

from agent_framework import response_handler

class InteractiveExecutor(Executor):
    """演示 response_handler 的用法"""

    def __init__(self, id: str = "interactive"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        # 请求外部输入（示例中不实际使用）
        result = await ctx.request_info(
            prompt=f"请确认处理 '{text}'",
            expected_type=str,
        )
        await ctx.send_message(f"已确认: {text}")

    @response_handler
    async def handle_response(self, original_request: Any, response: Any, ctx: WorkflowContext[str]) -> None:
        """处理 request_info 的响应"""
        pass


async def main():
    print("=" * 60)
    print("  Workflow Executors 示例")
    print("=" * 60)

    # 示例 1: 简单工作流
    print("\n--- 示例 1: UpperCase → ReverseText ---")
    workflow1 = create_simple_workflow()
    events1 = await workflow1.run("hello world")
    print(f"输入: 'hello world'")
    print(f"输出: {events1.get_outputs()}")

    # 示例 2: 链式工作流
    print("\n--- 示例 2: UpperCase → AddPrefix → append_suffix ---")
    workflow2 = create_chain_workflow()
    events2 = await workflow2.run("chain test")
    print(f"输入: 'chain test'")
    print(f"输出: {events2.get_outputs()}")

    # 示例 3: Executor 属性
    print("\n--- 示例 3: Executor 属性 ---")
    explain_executor_properties()

    # 示例 4: AgentExecutor 结构
    print("\n--- 示例 4: AgentExecutor 结构 ---")
    agent_exec = await create_agent_executor()
    print(f"AgentExecutor input_types: {agent_exec.input_types}")
    print(f"AgentExecutor output_types: {agent_exec.output_types}")

    print("\n" + "=" * 60)
    print("  Executors 示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
