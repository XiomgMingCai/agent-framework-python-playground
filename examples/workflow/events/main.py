# Copyright (c) Microsoft. All rights reserved.
# Events - 工作流事件模型
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/events

import asyncio

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
    WorkflowEvent,
    WorkflowEventType,
    WorkflowEventSource,
    WorkflowRunState,
    WorkflowErrorDetails,
    WorkflowRunResult,
)


# ========== 1. 基础节点 ==========

class SimpleProcessor(Executor):
    def __init__(self, id: str = "processor"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.yield_output(f"processed: {text}")


@executor(id="echo")
async def echo(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.yield_output(text)


# ========== 2. 事件类型演示 ==========

def demonstrate_event_types():
    """演示各种 WorkflowEvent 类型"""
    print("=== WorkflowEvent 类型 ===\n")

    # started 事件
    started = WorkflowEvent.started()
    print(f"started: {started.type} | origin: {started.origin}")

    # status 事件
    status = WorkflowEvent.status(state=WorkflowRunState.IN_PROGRESS)
    print(f"status: {status.type} | state: {status.state}")

    # emit 事件 (data)
    emit_event = WorkflowEvent.emit("processor", "some data")
    print(f"emit: {emit_event.type} | executor: {emit_event.executor_id} | data: {emit_event.data}")

    # output 事件
    output = WorkflowEvent.output("processor", "result")
    print(f"output: {output.type} | executor: {output.executor_id} | output: {output.data}")

    # warning 事件
    warning = WorkflowEvent.warning("注意：某些数据未处理")
    print(f"warning: {warning.type} | message: {warning.data}")

    # error 事件
    error = WorkflowEvent.error(Exception("处理失败"))
    print(f"error: {error.type} | error: {error.data}")

    # failed 事件
    failed = WorkflowEvent.failed(
        details=WorkflowErrorDetails(error_type="FATAL", message="致命错误")
    )
    print(f"failed: {failed.type} | state: {failed.state}")


# ========== 3. 事件迭代 ==========

def demonstrate_event_iteration():
    """演示如何遍历工作流事件"""
    print("\n=== 事件迭代 ===\n")

    processor = SimpleProcessor()

    workflow = (
        WorkflowBuilder(start_executor=processor)
        .add_edge(processor, echo)
        .build()
    )

    return workflow


# ========== 4. WorkflowRunResult 方法 ==========

async def demonstrate_run_result():
    """演示 WorkflowRunResult 的方法"""
    print("\n=== WorkflowRunResult 方法 ===\n")

    processor = SimpleProcessor()

    workflow = WorkflowBuilder(start_executor=processor).build()

    # 运行工作流
    result: WorkflowRunResult = await workflow.run("test data")

    print(f"事件数量: {len(result)}")

    # 获取输出（通过遍历查找 output 事件）
    outputs = [e.data for e in result if e.type == "output"]
    print(f"输出列表: {outputs}")

    print("\n--- 所有事件 ---")
    for i, event in enumerate(result):
        print(f"  [{i}] {event.type}")
        if event.data is not None:
            print(f"       data: {event.data}")


# ========== 5. WorkflowEventType 枚举 ==========

def list_event_types():
    """列出所有事件类型"""
    print("\n=== WorkflowEventType 枚举值 ===")
    for et in WorkflowEventType:
        print(f"  {et}")


# ========== 6. WorkflowRunState 枚举 ==========

def list_run_states():
    """列出所有运行状态"""
    print("\n=== WorkflowRunState 枚举值 ===")
    for rs in WorkflowRunState:
        print(f"  {rs}")


async def main():
    print("=" * 60)
    print("  Workflow Events 示例")
    print("=" * 60)

    # 事件类型演示
    demonstrate_event_types()

    # 事件迭代
    workflow = demonstrate_event_iteration()
    print("\n--- 工作流执行事件 ---")
    events = await workflow.run("hello")
    for i, event in enumerate(events):
        print(f"  事件 {i}: {event.type}")
        if hasattr(event, 'state') and event.state:
            print(f"          state: {event.state}")
        if event.data is not None:
            print(f"          data: {event.data}")

    # WorkflowRunResult 方法
    await demonstrate_run_result()

    # 枚举值
    list_event_types()
    list_run_states()

    print("\n" + "=" * 60)
    print("  Events 示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
