# Copyright (c) Microsoft. All rights reserved.
# Human-in-the-Loop - 人工介入机制
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop

import asyncio
from typing import Any

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
    response_handler,
)


# ========== 0. 基础节点（用于演示） ==========

class UpperCase(Executor):
    def __init__(self, id: str = "upper_case"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text.upper())


class Reverse(Executor):
    def __init__(self, id: str = "reverse"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.yield_output(text[::-1])


# ========== 1. 人工确认节点 ==========

class HumanApproval(Executor):
    """需要人工批准的节点"""

    def __init__(self, id: str = "human_approval"):
        super().__init__(id=id)

    @handler
    async def check(self, text: str, ctx: WorkflowContext[str]) -> None:
        # 请求人工确认
        approved = await ctx.request_info(
            prompt=f"请确认是否处理以下内容:\n\n{text}",
            expected_type=bool,
        )

        if approved:
            await ctx.send_message(f"已批准: {text}")
        else:
            await ctx.yield_output(f"已拒绝: {text}")


class TextAnalyzer(Executor):
    """分析文本"""

    def __init__(self, id: str = "analyzer"):
        super().__init__(id=id)

    @handler
    async def analyze(self, text: str, ctx: WorkflowContext[str]) -> None:
        word_count = len(text.split())
        char_count = len(text)

        result = f"词数: {word_count}, 字符数: {char_count}"
        await ctx.yield_output(result)


# ========== 2. 人工输入节点 ==========

class HumanInput(Executor):
    """请求人工输入"""

    def __init__(self, id: str = "human_input"):
        super().__init__(id=id)

    @handler
    async def request_input(self, prompt_text: str, ctx: WorkflowContext[str]) -> None:
        # 请求人工输入
        user_input = await ctx.request_info(
            prompt=prompt_text,
            expected_type=str,
        )

        await ctx.send_message(user_input)


class ConditionalRouter(Executor):
    """基于人工选择的条件路由"""

    def __init__(self, id: str = "router"):
        super().__init__(id=id)

    @handler
    async def route(self, text: str, ctx: WorkflowContext[str]) -> None:
        # 请求选择
        choice = await ctx.request_info(
            prompt=f"请选择处理方式:\n1. 大写\n2. 小写\n3. 反转",
            expected_type=int,
        )

        # 根据选择路由
        if choice == 1:
            await ctx.send_message(text.upper(), edge_name="upper")
        elif choice == 2:
            await ctx.send_message(text.lower(), edge_name="lower")
        else:
            await ctx.send_message(text[::-1], edge_name="reverse")


# ========== 3. 函数 Executor ==========

@executor(id="process_upper")
async def process_upper(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.yield_output(text.upper())


@executor(id="process_lower")
async def process_lower(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.yield_output(text.lower())


@executor(id="process_reverse")
async def process_reverse(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.yield_output(text[::-1])


# ========== 4. 工作流示例 ==========

def create_approval_workflow():
    """带审批的工作流"""
    approval = HumanApproval()
    analyzer = TextAnalyzer()

    return (
        WorkflowBuilder(start_executor=approval)
        .add_edge(approval, analyzer)
        .build()
    )


def create_simple_workflow():
    """简单的选择工作流（演示用）"""
    # 注意：SwitchCaseEdgeGroup 需要 Case 对象，详见 edges 示例
    # 这里使用简单的线性工作流演示
    upper = UpperCase()
    reverse = Reverse()

    return (
        WorkflowBuilder(start_executor=upper)
        .add_edge(upper, reverse)
        .build()
    )


def create_input_workflow():
    """人工输入工作流"""
    input_node = HumanInput()

    return (
        WorkflowBuilder(start_executor=input_node)
        .add_edge(input_node, process_upper)
        .build()
    )


# ========== 5. 模拟人工响应 ==========

class MockHumanResponse:
    """模拟人工响应（用于演示）"""

    def __init__(self, responses: list):
        self.responses = responses
        self.index = 0

    async def get_response(self, prompt: str, expected_type: type) -> Any:
        if self.index < len(self.responses):
            response = self.responses[self.index]
            self.index += 1
            print(f"\n[模拟人工] prompt: {prompt[:50]}...")
            print(f"[模拟人工] 返回: {response}")
            return response
        return None


# ========== 6. 演示说明 ==========

def explain_human_in_the_loop():
    """说明 Human-in-the-Loop 机制"""
    print("""
=== Human-in-the-Loop 机制 ===

ctx.request_info() 方法:
  - 暂停工作流执行
  - 等待外部输入（人工/系统）
  - 返回输入后继续执行

典型应用场景:
  1. 审批流程：重要操作需要人工确认
  2. 人工输入：需要用户补充信息
  3. 异常处理：出现问题时人工介入
  4. 质量控制：人工审核 AI 输出

注意事项:
  - request_info 是异步的
  - 需要配套的 response_handler 处理响应
  - 可以返回任意类型（由 expected_type 指定）
""")


async def demo_without_actual_human():
    """演示（不实际等待人工输入）"""
    print("\n=== 演示说明 ===")
    print("实际运行需要人工介入，以下为结构演示：")

    # 显示工作流结构
    print("\n1. 审批工作流结构:")
    print("   Input → HumanApproval(request_info) → TextAnalyzer → Output")

    print("\n2. 选择工作流结构:")
    print("   Input → ConditionalRouter(request_info)")
    print("           ├─ upper → process_upper → Output")
    print("           ├─ lower → process_lower → Output")
    print("           └─ reverse → process_reverse → Output")


async def main():
    print("=" * 60)
    print("  Workflow Human-in-the-Loop 示例")
    print("=" * 60)

    # 机制说明
    explain_human_in_the_loop()

    # 演示说明
    await demo_without_actual_human()

    # 工作流结构展示
    print("\n=== 工作流结构 ===")

    print("\n--- 审批工作流 ---")
    wf1 = create_approval_workflow()
    print(f"执行器数: {len(wf1.executors)}")
    print(f"边组数: {len(wf1.edge_groups)}")

    print("\n--- 选择工作流（简化版） ---")
    wf2 = create_simple_workflow()
    print(f"执行器数: {len(wf2.executors)}")
    print(f"边组数: {len(wf2.edge_groups)}")

    print("\n--- 人工输入工作流 ---")
    wf3 = create_input_workflow()
    print(f"执行器数: {len(wf3.executors)}")
    print(f"边组数: {len(wf3.edge_groups)}")

    print("\n" + "=" * 60)
    print("  Human-in-the-Loop 示例完成")
    print("  注意: 实际运行需要通过 response_handler 处理人工响应")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
