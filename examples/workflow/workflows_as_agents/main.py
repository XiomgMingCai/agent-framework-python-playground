# Copyright (c) Microsoft. All rights reserved.
# Workflows as Agents - 将工作流作为 Agent 使用
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/as-agents

import asyncio

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
    WorkflowAgent,
    AgentExecutor,
)


# ========== 1. 工作流定义 ==========

class TextPreprocessor(Executor):
    def __init__(self, id: str = "preprocessor"):
        super().__init__(id=id)

    @handler
    async def preprocess(self, text: str, ctx: WorkflowContext[str]) -> None:
        cleaned = text.strip().replace("\n", " ")
        await ctx.send_message(cleaned)


@executor(id="analyzer")
async def analyzer(text: str, ctx: WorkflowContext[str]) -> None:
    word_count = len(text.split())
    await ctx.yield_output(f"词数: {word_count}")


def create_analysis_workflow():
    """创建文本分析工作流"""
    preprocessor = TextPreprocessor()

    return (
        WorkflowBuilder(start_executor=preprocessor)
        .add_edge(preprocessor, analyzer)
        .build()
    )


# ========== 2. 使用 AgentExecutor 的工作流 ==========

class SimpleTextAgent:
    """简单的文本处理 Agent 实现（满足 SupportsAgentRun 协议）"""

    def __init__(self):
        self.id = "simple_text_agent"
        self.name = "SimpleTextAgent"
        self.description = "简单的文本处理 Agent"

    def create_session(self):
        """创建会话（AgentExecutor 需要）"""
        return None

    async def run(self, messages=None, *, stream=False, session=None, **kwargs):
        from agent_framework import Message, Content, AgentResponse
        # 简单处理：提取文本内容并统计
        texts = []
        if messages:
            for msg in messages:
                for c in msg.contents:
                    if hasattr(c, 'text'):
                        texts.append(c.text)
        combined = " ".join(texts) if texts else ""
        word_count = len(combined.split())
        response_text = f"处理了 {len(texts)} 条消息，共 {word_count} 个词"

        return AgentResponse(
            messages=[Message(
                contents=[Content.from_text(response_text)],
                role="assistant",
                author_name="SimpleTextAgent"
            )],
            response_id="resp_001"
        )


def create_agent_executor_workflow():
    """创建使用 AgentExecutor 的工作流（可被 WorkflowAgent 包装）"""
    text_agent = SimpleTextAgent()
    agent_executor = AgentExecutor(agent=text_agent, id="text_agent_executor")

    workflow = (
        WorkflowBuilder(start_executor=agent_executor)
        .build()
    )

    return workflow, agent_executor


# ========== 3. WorkflowAgent 示例 ==========

def demonstrate_workflow_agent():
    """演示 WorkflowAgent"""
    print("\n--- WorkflowAgent 演示 ---")

    # 创建使用 AgentExecutor 的工作流
    workflow, agent_exec = create_agent_executor_workflow()

    # 包装为 Agent
    agent = WorkflowAgent(workflow=workflow, name="AnalysisAgent")

    print(f"Agent 名称: {agent.name}")
    print(f"Agent 类型: {type(agent).__name__}")
    print(f"底层工作流: {agent.workflow.name}")

    # 检查是否支持 run 方法
    print(f"支持 run: {hasattr(agent, 'run')}")
    print(f"支持 invoke: {hasattr(agent, 'invoke')}")

    # 注意：实际运行需要 LLM 提供者，这里只演示结构


# ========== 3. 工作流作为 Agent 的优势 ==========

def explain_workflow_as_agent():
    """说明工作流作为 Agent 的优势"""
    print("""
=== Workflow as Agent 的优势 ===

1. 统一接口
   - Workflow 和 Agent 使用相同接口
   - 便于在 Multi-Agent 系统中组合

2. 层次化组合
   ┌─────────────────────────────────┐
   │  Orchestrator Agent            │
   │  ├─ WorkflowAgent (分析流程)   │
   │  ├─ WorkflowAgent (审批流程)   │
   │  └─ Agent (LLM 对话)            │
   └─────────────────────────────────┘

3. 复用现有工作流
   - 已有的工作流可以直接作为 Agent 使用
   - 无需修改原有逻辑

4. 混合调用
   - 工作流可以调用其他 Agent
   - Agent 也可以调用工作流
""")


# ========== 4. 在 Multi-Agent 中使用 ==========

def multi_agent_with_workflow():
    """演示在多 Agent 系统中使用 WorkflowAgent"""
    print("\n--- Multi-Agent 系统中使用 ---")

    # 创建使用 AgentExecutor 的工作流
    analysis_wf, agent_exec = create_agent_executor_workflow()
    workflow_agent = WorkflowAgent(workflow=analysis_wf, name="AnalysisWorkflow")

    # 检查属性
    print(f"WorkflowAgent.name: {workflow_agent.name}")

    # 模拟调用
    print("\n模拟调用工作流 Agent:")
    print(f"  输入: 'hello world'")
    print(f"  输出: 处理了 1 条消息，共 2 个词")


# ========== 5. 与普通 Agent 对比 ==========

def compare_agent_types():
    """对比 WorkflowAgent 和普通 Agent"""
    print("\n--- Agent 类型对比 ---")

    print("""
| 特性         | Agent          | WorkflowAgent        |
|--------------|----------------|----------------------|
| 用途         | LLM 对话       | 执行工作流           |
| 实现         | LLM + Prompt   | Executor 图          |
| 调用方式     | run()          | run()                |
| 输出类型     | 文本响应       | WorkflowRunResult    |
| 状态管理     | Session        | Checkpoint           |
| 适用场景     | 问答、生成     | 多步骤处理流程       |
""")


async def main():
    print("=" * 60)
    print("  Workflows as Agents 示例")
    print("=" * 60)

    # 机制说明
    explain_workflow_as_agent()

    # WorkflowAgent 演示
    demonstrate_workflow_agent()

    # Multi-Agent 使用
    multi_agent_with_workflow()

    # 类型对比
    compare_agent_types()

    print("\n" + "=" * 60)
    print("  Workflows as Agents 示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
