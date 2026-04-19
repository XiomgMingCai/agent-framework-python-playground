# Copyright (c) Microsoft. All rights reserved.
# Declarative Workflows - YAML 格式工作流定义
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/declarative

import asyncio

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
)


# ========== 1. 定义执行器 ==========

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


@executor(id="reverse")
async def reverse(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.yield_output(text[::-1])


# ========== 2. YAML 定义示例 ==========

YAML_WORKFLOW = """
name: text_processing_workflow
version: "1.0"

executors:
  upper_case:
    type: class
    class: UpperCase
    config:
      id: upper_case

  lower_case:
    type: class
    class: LowerCase
    config:
      id: lower_case

  reverse:
    type: function
    function: reverse
    config:
      id: reverse

edges:
  - from: upper_case
    to: reverse

start: upper_case
"""

YAML_WORKFLOW_WITH_SWITCH = """
name: conditional_workflow
version: "1.0"

executors:
  router:
    type: class
    class: ConditionalRouter
    config:
      id: router

  upper:
    type: function
    function: reverse  # 复用
    config:
      id: process_upper

  lower:
    type: function
    function: reverse
    config:
      id: process_lower

edges:
  - from: router
    to: upper
    edge_name: to_upper

  - from: router
    to: lower
    edge_name: to_lower

start: router
"""


# ========== 3. 手动构建等效工作流 ==========

def create_equivalent_workflow():
    """从 YAML 定义手动构建等效工作流"""
    upper = UpperCase()

    return (
        WorkflowBuilder(start_executor=upper)
        .add_edge(upper, reverse)
        .build()
    )


# ========== 4. YAML 解析说明 ==========

def explain_yaml_parsing():
    """说明 YAML 解析流程"""
    print("""
=== Declarative Workflow 流程 ===

1. YAML 定义
   ┌─────────────────────────┐
   │ name: my_workflow       │
   │ executors:              │
   │   upper: UpperCase     │
   │ edges:                 │
   │   - from: upper        │
   │     to: reverse        │
   └─────────────────────────┘

2. YAML 解析器加载
   → 解析 executor 定义
   → 解析边连接
   → 解析起始节点

3. 动态实例化
   → UpperCase(id="upper")
   → reverse function executor

4. 构建工作流
   → WorkflowBuilder
   → add_edge connections
   → build()

5. 执行
   → workflow.run(input)
""")


# ========== 5. Executor 注册表 ==========

class ExecutorRegistry:
    """模拟 Executor 注册表"""

    def __init__(self):
        self._executors = {}

    def register(self, name: str, executor_cls):
        self._executors[name] = executor_cls

    def get(self, name: str):
        return self._executors.get(name)

    def create(self, name: str, config: dict = None):
        cls = self.get(name)
        if cls is None:
            raise ValueError(f"Executor '{name}' not found")
        return cls(**(config or {}))


def demonstrate_registry():
    """演示注册表机制"""
    print("\n=== Executor 注册表演示 ===")

    registry = ExecutorRegistry()

    # 注册
    registry.register("upper_case", UpperCase)
    registry.register("lower_case", LowerCase)
    registry.register("reverse", reverse)

    # 创建
    upper = registry.create("upper_case", {"id": "my_upper"})
    print(f"创建 upper_case: {upper.id}")

    # YAML 中的 executor 映射
    yaml_mapping = {
        "upper_case": {"class": "UpperCase", "config": {"id": "upper"}},
        "reverse": {"function": "reverse", "config": {"id": "rev"}},
    }

    print("\nYAML executor 映射示例:")
    for name, spec in yaml_mapping.items():
        if "class" in spec:
            print(f"  {name}: class={spec['class']}, config={spec['config']}")
        elif "function" in spec:
            print(f"  {name}: function={spec['function']}, config={spec['config']}")


async def main():
    print("=" * 60)
    print("  Workflow Declarative Workflows 示例")
    print("=" * 60)

    # YAML 结构说明
    explain_yaml_parsing()

    # 注册表演示
    demonstrate_registry()

    # 实际运行
    print("\n=== 实际工作流执行 ===")

    print("\n1. 基础 YAML 等效工作流:")
    wf1 = create_equivalent_workflow()
    result1 = await wf1.run("hello")
    print(f"   输入: 'hello' → 输出: {result1.get_outputs()}")

    print("\n" + "=" * 60)
    print("  Declarative Workflows 示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
