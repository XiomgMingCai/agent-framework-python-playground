# Copyright (c) Microsoft. All rights reserved.
# Edges - 执行单元之间的连接
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/edges

import asyncio
from typing import Literal

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
    Edge,
    Case,
    Default,
    SingleEdgeGroup,
    FanOutEdgeGroup,
    FanInEdgeGroup,
    SwitchCaseEdgeGroup,
)


# ========== 1. 基础节点定义 ==========

class NumberProducer(Executor):
    """生成数字"""

    def __init__(self, id: str = "number_producer"):
        super().__init__(id=id)

    @handler
    async def produce(self, _: str, ctx: WorkflowContext[int]) -> None:
        await ctx.send_message(42)


class TextProcessor(Executor):
    """文本处理器"""

    def __init__(self, id: str = "text_processor"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.yield_output(f"处理: {text}")


class UpperCase(Executor):
    def __init__(self, id: str = "upper_case"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text.upper())


class LowerCase(Executor):
    def __init__(self, id: str = "lower_case"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text.lower())


class ReverseText(Executor):
    def __init__(self, id: str = "reverse"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.yield_output(text[::-1])


class AggregateResults(Executor):
    """聚合多个输入"""

    def __init__(self, id: str = "aggregator"):
        super().__init__(id=id)

    @handler
    async def aggregate(self, results: list, ctx: WorkflowContext[list]) -> None:
        await ctx.yield_output(results)


# ========== 2. 函数 Executor ==========

@executor(id="triple")
async def triple(num: int, ctx: WorkflowContext[int]) -> None:
    await ctx.send_message(num * 3)


@executor(id="square")
async def square(num: int, ctx: WorkflowContext[int]) -> None:
    await ctx.send_message(num * num)


@executor(id="to_string")
async def to_string(num: int, ctx: WorkflowContext[int]) -> None:
    await ctx.send_message(str(num))


@executor(id="concat")
async def concat(a: str, ctx: WorkflowContext[str]) -> None:
    await ctx.yield_output(a)


# ========== 3. SingleEdgeGroup 示例 ==========

def create_single_edge_workflow():
    """一对一连接: UpperCase → ReverseText"""
    upper = UpperCase()
    reverse = ReverseText()

    return WorkflowBuilder(start_executor=upper).add_edge(upper, reverse).build()


# ========== 4. FanOutEdgeGroup 示例 ==========

def create_fan_out_workflow():
    """一对多广播: Number → Triple AND Square"""
    producer = NumberProducer()

    return (
        WorkflowBuilder(start_executor=producer)
        .add_fan_out_edges(producer, [triple, square])
        .build()
    )


# ========== 5. FanInEdgeGroup 示例 ==========

def create_fan_in_workflow():
    """多对一汇聚: UpperCase → concat AND LowerCase → concat"""
    upper = UpperCase()
    lower = LowerCase()

    # FanIn: 多个节点的输出汇聚到一个节点
    # 注意: FanIn 需要所有源节点输出相同类型
    return (
        WorkflowBuilder(start_executor=upper)
        .add_edge(upper, lower)
        .add_fan_in_edges([upper, lower], concat)
        .build()
    )


def demonstrate_fan_in_structure():
    """演示 FanIn 结构（不实际运行）"""
    print("\n--- FanInEdgeGroup 结构说明 ---")
    print("""
    FanInEdgeGroup: 多个源 → 一个目标

    ┌────────────┐
    │  UpperCase  │──────┐
    └────────────┘      │
                        ▼
                   ┌─────────┐
                   │  Concat  │ → 输出
                   └─────────┘
                        ▲
    ┌────────────┐      │
    │  LowerCase  │──────┘
    └────────────┘

    特点:
    - 多个源节点输出汇聚到单个目标节点
    - 适用于聚合操作（求和、平均、拼接等）
    """)


# ========== 6. SwitchCaseEdgeGroup 示例 ==========

def demonstrate_switch_case_structure():
    """演示 SwitchCase 结构（不实际运行）"""
    print("\n--- SwitchCaseEdgeGroup 结构说明 ---")
    print("""
    SwitchCaseEdgeGroup: 条件路由

    ┌──────────────────┐
    │  ConditionalRouter │
    │ (根据条件选择分支)  │
    └────────┬─────────┘
             │
       ┌─────┴─────┬────────┐
       ▼           ▼        ▼
    ┌──────┐  ┌──────┐  ┌─────────┐
    │ > 50 │  │ <= 50 │  │ Default │
    └───┬──┘  └───┬──┘  └───┬─────┘
        ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ Triple │ │ Square │ │ToString│
    └────────┘ └────────┘ └────────┘

    特点:
    - 根据条件动态选择下一个执行节点
    - 支持默认分支
    - 条件可以是任意布尔函数
    """)


# ========== 7. 边的属性访问 ==========

def demonstrate_edge_properties():
    """演示如何访问边的属性"""
    upper = UpperCase()
    reverse = ReverseText()

    workflow = WorkflowBuilder(start_executor=upper).add_edge(upper, reverse).build()

    # 获取边信息
    print(f"工作流名称: {workflow.name}")
    print(f"执行器数量: {len(workflow.executors)}")
    print(f"边组数量: {len(workflow.edge_groups)}")

    for executor_id in workflow.executors:
        print(f"  执行器: {executor_id}")


async def main():
    print("=" * 60)
    print("  Workflow Edges 示例")
    print("=" * 60)

    # 示例 1: SingleEdge (一对一)
    print("\n--- 示例 1: SingleEdge (一对一) ---")
    wf1 = create_single_edge_workflow()
    events1 = await wf1.run("hello")
    print(f"输入: 'hello' → 输出: {events1.get_outputs()}")

    # 示例 2: FanOut (一对多)
    print("\n--- 示例 2: FanOutEdgeGroup (一对多广播) ---")
    wf2 = create_fan_out_workflow()
    events2 = await wf2.run("")
    print(f"输入: 42 (数字) → 输出: {events2.get_outputs()}")

    # 示例 3: FanIn (多对一)
    print("\n--- 示例 3: FanInEdgeGroup (多对一汇聚) ---")
    demonstrate_fan_in_structure()

    # 示例 4: SwitchCase (条件路由)
    print("\n--- 示例 4: SwitchCaseEdgeGroup (条件路由) ---")
    demonstrate_switch_case_structure()

    # 示例 5: 边属性
    print("\n--- 示例 5: 边属性 ---")
    demonstrate_edge_properties()

    print("\n" + "=" * 60)
    print("  Edges 示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
