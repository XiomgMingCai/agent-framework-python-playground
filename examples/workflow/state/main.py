# Copyright (c) Microsoft. All rights reserved.
# State Management - 工作流状态管理
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/state

import asyncio

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
)


# ========== 1. 基础节点 ==========

class Counter(Executor):
    """计数器：每次调用累加"""

    def __init__(self, id: str = "counter"):
        super().__init__(id=id)

    @handler
    async def count(self, _: str, ctx: WorkflowContext[int]) -> None:
        # 获取当前计数
        count = ctx.get_state("count", default=0)

        # 累加
        new_count = count + 1
        ctx.set_state("count", new_count)

        # 发送到下一个节点
        await ctx.send_message(new_count)


class Accumulator(Executor):
    """累加器：收集多个值求和"""

    def __init__(self, id: str = "accumulator"):
        super().__init__(id=id)

    @handler
    async def accumulate(self, value: int, ctx: WorkflowContext[int]) -> None:
        # 获取当前总和
        total = ctx.get_state("total", default=0)

        # 累加
        new_total = total + value
        ctx.set_state("total", new_total)

        # 发送到下一个节点
        await ctx.send_message(new_total)


class Finalizer(Executor):
    """最终处理：产出最终状态"""

    def __init__(self, id: str = "finalizer"):
        super().__init__(id=id)

    @handler
    async def finalize(self, value: int, ctx: WorkflowContext[int]) -> None:
        # 获取最终状态
        count = ctx.get_state("count", default=0)
        total = ctx.get_state("total", default=0)

        result = {
            "final_value": value,
            "counter": count,
            "total": total,
        }

        await ctx.yield_output(result)


# ========== 2. 函数 Executor ==========

@executor(id="double")
async def double(num: int, ctx: WorkflowContext[int]) -> None:
    # 获取当前值并更新
    current = ctx.get_state("current_value", default=0)
    ctx.set_state("current_value", current + num)

    # 翻倍
    await ctx.send_message(num * 2)


@executor(id="show_state")
async def show_state(num: int, ctx: WorkflowContext[int]) -> None:
    # 显示当前状态
    current = ctx.get_state("current_value", default=0)
    print(f"  [show_state] current_value = {current}, received = {num}")

    await ctx.send_message(num)


# ========== 3. State 的 superstep 语义 ==========

def explain_superstep_semantics():
    """解释 State 的 superstep 语义"""
    print("\n=== State Superstep 语义 ===")
    print("""
在同一个 superstep 内:
  - set_state() 设置的值，在当前 superstep 内其他 Executor 看不到
  - 只能 get_state() 到上一个 superstep 提交的值

跨 superstep:
  - 每个 superstep 结束时，状态会自动提交
  - 下一个 superstep 开始时，所有 Executor 看到的是上一轮提交的值

这确保了:
  1. 同一 superstep 内的多个 Executor 不会互相干扰
  2. 状态变更在超步边界同步
""")


# ========== 4. 工作流示例 ==========

def create_counter_workflow():
    """计数器工作流: Counter → Accumulator → Finalizer"""
    counter = Counter()
    accumulator = Accumulator()
    finalizer = Finalizer()

    return (
        WorkflowBuilder(start_executor=counter)
        .add_edge(counter, accumulator)
        .add_edge(accumulator, finalizer)
        .build()
    )


def create_state_demo_workflow():
    """状态演示工作流: double → show_state"""
    return (
        WorkflowBuilder(start_executor=double)
        .add_edge(double, show_state)
        .build()
    )


async def main():
    print("=" * 60)
    print("  Workflow State Management 示例")
    print("=" * 60)

    # 解释 superstep 语义
    explain_superstep_semantics()

    # 示例 1: 计数器工作流
    print("\n--- 示例 1: 计数器工作流 ---")
    wf1 = create_counter_workflow()
    result1 = await wf1.run("increment")
    print(f"最终结果: {result1.get_outputs()}")

    # 示例 2: 状态可见性演示
    print("\n--- 示例 2: 状态可见性演示 ---")
    wf2 = create_state_demo_workflow()
    print("运行: double → show_state (发送值 5)")
    result2 = await wf2.run(5)
    print(f"最终输出: {result2.get_outputs()}")

    # 示例 3: 多次运行观察状态累积
    print("\n--- 示例 3: 状态累积演示 ---")
    print("连续运行 3 次，观察 counter 值的变化:")
    for i in range(3):
        result = await wf1.run("increment")
        outputs = result.get_outputs()
        if outputs:
            print(f"  第 {i+1} 次: counter = {outputs[0]['counter']}, total = {outputs[0]['total']}")

    print("\n" + "=" * 60)
    print("  State Management 示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
