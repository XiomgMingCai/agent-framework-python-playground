# Copyright (c) Microsoft. All rights reserved.
# Checkpoints & Resuming - 检查点与断点续传
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints

import asyncio
import tempfile

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
    InMemoryCheckpointStorage,
    FileCheckpointStorage,
    WorkflowCheckpoint,
)


# ========== 1. 基础节点 ==========

class CheckpointDemo(Executor):
    """演示检查点保存"""

    def __init__(self, id: str = "checkpoint_demo"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        ctx.set_state("processed", True)
        ctx.set_state("result", f"result_for_{text}")
        await ctx.send_message(text.upper())


@executor(id="finalize")
async def finalize(text: str, ctx: WorkflowContext[str]) -> None:
    result = ctx.get_state("result", default="none")
    await ctx.yield_output(f"{text} -> {result}")


# ========== 2. CheckpointStorage 示例 ==========

def demonstrate_storage_backends():
    """演示不同的存储后端"""
    print("\n=== CheckpointStorage 类型 ===")

    # 1. 内存存储（适合测试）
    memory_storage = InMemoryCheckpointStorage()
    print(f"1. InMemoryCheckpointStorage: {type(memory_storage).__name__}")

    # 2. 文件存储（适合生产）
    with tempfile.TemporaryDirectory() as tmpdir:
        file_storage = FileCheckpointStorage(storage_path=tmpdir)
        print(f"2. FileCheckpointStorage: {type(file_storage).__name__}")
        print(f"   存储目录: {tmpdir}")


# ========== 3. 检查点保存和恢复 ==========

async def checkpoint_save_restore():
    """演示保存和恢复检查点"""
    print("\n=== 检查点保存与恢复 ===")

    # 创建带检查点存储的工作流
    storage = InMemoryCheckpointStorage()

    demo = CheckpointDemo()

    workflow = (
        WorkflowBuilder(start_executor=demo)
        .add_edge(demo, finalize)
        .build()
    )

    # 第一次运行
    print("第一次运行...")
    result1 = await workflow.run("test_input")
    print(f"输出: {result1.get_outputs()}")

    # 获取工作流当前状态并创建检查点
    # 注意：实际应用中需要从工作流运行状态创建检查点
    print(f"工作流已创建，名称: {workflow.name}")

    # 列出存储中的检查点（演示用）
    print(f"检查点存储类型: {type(storage).__name__}")


# ========== 4. 文件存储示例 ==========

async def file_storage_demo():
    """演示文件存储"""
    print("\n=== 文件存储示例 ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = FileCheckpointStorage(storage_path=tmpdir)

        demo = CheckpointDemo()
        workflow = (
            WorkflowBuilder(start_executor=demo)
            .add_edge(demo, finalize)
            .build()
        )

        print(f"文件存储已初始化: {tmpdir}")
        print(f"工作流名称: {workflow.name}")


# ========== 5. 检查点概念说明 ==========

def explain_checkpoints():
    """说明检查点机制"""
    print("""
=== Checkpoint 机制 ===

WorkflowCheckpoint 包含:
  - workflow_id: 工作流唯一标识
  - checkpoint_id: 检查点唯一标识
  - messages: 消息历史
  - state: 状态快照
  - pending_requests: 待处理的请求
  - iteration_count: 迭代次数
  - timestamp: 时间戳

CheckpointStorage 接口:
  - save(checkpoint): 保存检查点
  - load(checkpoint_id): 加载检查点
  - delete(checkpoint_id): 删除检查点
  - list_checkpoints(): 列出所有检查点

注意: 实际的检查点保存和恢复需要工作流运行状态管理，
      完整示例请参考官方文档。
""")


async def main():
    print("=" * 60)
    print("  Workflow Checkpoints & Resuming 示例")
    print("=" * 60)

    # 存储后端演示
    demonstrate_storage_backends()

    # 检查点保存和恢复
    await checkpoint_save_restore()

    # 文件存储
    await file_storage_demo()

    # 概念说明
    explain_checkpoints()

    print("\n" + "=" * 60)
    print("  Checkpoints 示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
