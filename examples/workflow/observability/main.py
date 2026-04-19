# Copyright (c) Microsoft. All rights reserved.
# Observability - 工作流可观测性
# 基于: https://learn.microsoft.com/en-us/agent-framework/workflows/observability

import asyncio
import json
from datetime import datetime

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    executor,
    WorkflowEvent,
)


# ========== 1. 基础节点 ==========

class Processor(Executor):
    def __init__(self, id: str = "processor"):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.yield_output(f"processed: {text}")


@executor(id="transform")
async def transform(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.yield_output(text.upper())


# ========== 2. 事件日志记录器 ==========

class WorkflowLogger:
    """工作流事件日志记录器"""

    def __init__(self):
        self.events = []
        self.start_time = None

    def log_event(self, event: WorkflowEvent):
        timestamp = datetime.now().isoformat()
        self.events.append({
            "timestamp": timestamp,
            "type": event.type,
            "origin": str(event.origin) if event.origin else None,
            "state": str(event.state) if event.state else None,
            "data": event.data,
        })

    def get_summary(self):
        return {
            "total_events": len(self.events),
            "event_types": list(set(e["type"] for e in self.events)),
            "duration_ms": self._calculate_duration(),
        }

    def _calculate_duration(self):
        if not self.events:
            return 0
        start = datetime.fromisoformat(self.events[0]["timestamp"])
        end = datetime.fromisoformat(self.events[-1]["timestamp"])
        return (end - start).total_seconds() * 1000

    def print_timeline(self):
        print("\n=== 事件时间线 ===")
        for event in self.events:
            print(f"[{event['timestamp']}] {event['type']}")
            if event['data']:
                print(f"    data: {str(event['data'])[:50]}")


# ========== 3. 指标收集器 ==========

class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self.metrics = {
            "executor_invocations": 0,
            "executor_completions": 0,
            "executor_failures": 0,
            "outputs_produced": 0,
            "supersteps": 0,
        }

    def process_event(self, event: WorkflowEvent):
        if event.type == "executor_invoked":
            self.metrics["executor_invocations"] += 1
        elif event.type == "executor_completed":
            self.metrics["executor_completions"] += 1
        elif event.type == "executor_failed":
            self.metrics["executor_failures"] += 1
        elif event.type == "output":
            self.metrics["outputs_produced"] += 1
        elif event.type == "superstep_started":
            self.metrics["supersteps"] += 1

    def print_metrics(self):
        print("\n=== 执行指标 ===")
        for key, value in self.metrics.items():
            print(f"  {key}: {value}")


# ========== 4. 追踪器 ==========

class WorkflowTracer:
    """工作流追踪器"""

    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.trace = []

    def record(self, stage: str, data: dict):
        self.trace.append({
            "workflow_id": self.workflow_id,
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            **data,
        })

    def get_trace(self):
        return self.trace

    def print_trace(self):
        print("\n=== 执行追踪 ===")
        for entry in self.trace:
            print(f"[{entry['stage']}] {entry.get('message', '')}")
            if entry.get('executor'):
                print(f"    executor: {entry['executor']}")


# ========== 5. 可观测性集成示例 ==========

async def demonstrate_observability():
    """演示可观测性功能"""
    logger = WorkflowLogger()
    metrics = MetricsCollector()
    tracer = WorkflowTracer("wf-001")

    # 创建工作流
    processor = Processor()
    workflow = (
        WorkflowBuilder(start_executor=processor)
        .add_edge(processor, transform)
        .build()
    )

    tracer.record("init", {"message": "工作流初始化"})

    # 运行并收集事件
    print("运行工作流...")
    tracer.record("run", {"message": "开始执行"})

    result = await workflow.run("test data")

    tracer.record("complete", {
        "message": "执行完成",
        "outputs": len(result.get_outputs())
    })

    # 收集所有事件
    for event in result:
        logger.log_event(event)
        metrics.process_event(event)

    # 输出可观测性数据
    logger.print_timeline()
    metrics.print_metrics()
    tracer.print_trace()

    # 汇总
    print("\n=== 汇总 ===")
    summary = logger.get_summary()
    print(f"总事件数: {summary['total_events']}")
    print(f"事件类型: {summary['event_types']}")
    print(f"执行时长: {summary['duration_ms']:.2f}ms")

    # JSON 导出
    observability_data = {
        "workflow_id": "wf-001",
        "summary": summary,
        "metrics": metrics.metrics,
        "trace": tracer.get_trace(),
    }
    print(f"\nJSON 输出:\n{json.dumps(observability_data, indent=2, default=str)}")


# ========== 6. 事件过滤 ==========

def demonstrate_event_filtering():
    """演示事件过滤"""
    print("\n=== 事件过滤 ===")

    # 定义关注的事件类型（使用字符串字面量）
    important_types = {
        "executor_invoked",
        "executor_completed",
        "executor_failed",
        "output",
    }

    print("关注的事件类型:")
    for t in important_types:
        print(f"  - {t}")


async def main():
    print("=" * 60)
    print("  Workflow Observability 示例")
    print("=" * 60)

    # 可观测性演示
    await demonstrate_observability()

    # 事件过滤
    demonstrate_event_filtering()

    print("\n" + "=" * 60)
    print("  Observability 示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
