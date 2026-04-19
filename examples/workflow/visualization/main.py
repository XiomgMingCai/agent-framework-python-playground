# Copyright (c) Microsoft. All rights reserved.
# Visualization - 工作流可视化
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/visualization

import asyncio

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
    WorkflowViz,
)


# ========== 1. 基础节点 ==========

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


class Reverse(Executor):
    def __init__(self, id: str = "reverse"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.yield_output(text[::-1])


@executor(id="triple")
async def triple(num: int, ctx: WorkflowContext[int]) -> None:
    await ctx.send_message(num * 3)


@executor(id="square")
async def square(num: int, ctx: WorkflowContext[int]) -> None:
    await ctx.send_message(num * num)


# ========== 2. ASCII 可视化 ==========

def ascii_visualization():
    """简单的 ASCII 可视化"""
    print("\n=== ASCII 可视化 ===")

    # 线性工作流
    print("\n线性工作流 (UpperCase → Reverse):")
    print("""
    ┌─────────────┐
    │  Input      │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  UpperCase  │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  Reverse    │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   Output    │
    └─────────────┘
    """)

    # 分支工作流
    print("\n分支工作流 (Number → Triple & Square):")
    print("""
    ┌─────────────┐
    │   Input     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  Number     │
    └──┬──────┬───┘
       │      │
       ▼      ▼
  ┌────────┐ ┌────────┐
  │ Triple │ │ Square │
  └───┬────┘ └───┬────┘
      │          │
      ▼          ▼
    Output    Output
    """)


# ========== 3. WorkflowViz 示例 ==========

def demonstrate_workflow_viz():
    """演示 WorkflowViz 类的使用"""
    print("\n=== WorkflowViz 演示 ===")

    # 创建工作流
    upper = UpperCase()
    reverse = Reverse()

    workflow = (
        WorkflowBuilder(start_executor=upper)
        .add_edge(upper, reverse)
        .build()
    )

    # 创建可视化对象
    viz = WorkflowViz(workflow=workflow)

    print(f"WorkflowViz 创建成功")
    print(f"  workflow_id: {workflow.id}")
    print(f"  节点数: {len(workflow.executors)}")
    print(f"  边组数: {len(workflow.edge_groups)}")

    # 节点信息
    print("\n节点列表:")
    for exec_id, executor in workflow.executors.items():
        print(f"  - {exec_id} ({type(executor).__name__})")

    # 边信息
    print("\n边列表:")
    for edge_group in workflow.edge_groups:
        for edge in edge_group.edges:
            print(f"  - {edge.source_id} → {edge.target_id}")


# ========== 4. Mermaid 图表生成 ==========

def generate_mermaid():
    """生成 Mermaid 图表代码"""
    print("\n=== Mermaid 图表生成 ===")

    # 创建工作流
    upper = UpperCase()
    lower = LowerCase()
    reverse = Reverse()

    workflow = (
        WorkflowBuilder(start_executor=upper)
        .add_edge(upper, lower)
        .add_edge(lower, reverse)
        .build()
    )

    # 生成 Mermaid 代码
    mermaid_lines = ["flowchart TD"]

    # 添加节点
    for exec_id in workflow.executors.keys():
        node_id = exec_id.replace("-", "_")
        mermaid_lines.append(f"    {node_id}[{exec_id}]")

    # 添加边
    for edge_group in workflow.edge_groups:
        for edge in edge_group.edges:
            from_id = edge.source_id.replace("-", "_")
            to_id = edge.target_id.replace("-", "_")
            mermaid_lines.append(f"    {from_id} --> {to_id}")

    mermaid_code = "\n".join(mermaid_lines)

    print("Mermaid 图表代码:")
    print("```mermaid")
    print(mermaid_code)
    print("```")


# ========== 5. DOT 图表生成 ==========

def generate_dot():
    """生成 DOT 图表代码"""
    print("\n=== DOT 图表生成 ===")

    # 创建工作流
    upper = UpperCase()
    reverse = Reverse()

    workflow = (
        WorkflowBuilder(start_executor=upper)
        .add_edge(upper, reverse)
        .build()
    )

    # 生成 DOT 代码
    dot_lines = ["digraph workflow {", "    rankdir=TB;"]

    for exec_id in workflow.executors.keys():
        dot_lines.append(f'    "{exec_id}" [label="{exec_id}"];')

    for edge_group in workflow.edge_groups:
        for edge in edge_group.edges:
            dot_lines.append(f'    "{edge.source_id}" -> "{edge.target_id}";')

    dot_lines.append("}")

    dot_code = "\n".join(dot_lines)

    print("DOT 图表代码:")
    print("```dot")
    print(dot_code)
    print("```")


# ========== 6. JSON 结构导出 ==========

def export_json_structure():
    """导出工作流结构为 JSON"""
    print("\n=== JSON 结构导出 ===")

    import json

    upper = UpperCase()
    lower = LowerCase()
    reverse = Reverse()

    workflow = (
        WorkflowBuilder(start_executor=upper)
        .add_edge(upper, lower)
        .add_edge(lower, reverse)
        .build()
    )

    # 构建 JSON 结构
    edges_list = []
    for edge_group in workflow.edge_groups:
        for edge in edge_group.edges:
            edges_list.append({"from": edge.source_id, "to": edge.target_id})

    structure = {
        "workflow_id": workflow.id,
        "nodes": [
            {
                "id": exec_id,
                "type": type(executor).__name__,
            }
            for exec_id, executor in workflow.executors.items()
        ],
        "edges": edges_list,
    }

    print("JSON 结构:")
    print(json.dumps(structure, indent=2))


async def main():
    print("=" * 60)
    print("  Workflow Visualization 示例")
    print("=" * 60)

    # ASCII 可视化
    ascii_visualization()

    # WorkflowViz 演示
    demonstrate_workflow_viz()

    # Mermaid 生成
    generate_mermaid()

    # DOT 生成
    generate_dot()

    # JSON 导出
    export_json_structure()

    print("\n" + "=" * 60)
    print("  Visualization 示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
