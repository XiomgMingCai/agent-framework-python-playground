# Copyright (c) Microsoft. All rights reserved.
# Observability - 可观测性

import asyncio
import os
import time
from datetime import datetime

from dotenv import load_dotenv

from agent_framework import Agent, AgentMiddleware, AgentContext
from agent_framework.openai import OpenAIChatCompletionClient


class AgentLogger:
    """日志记录器"""
    def __init__(self):
        self.events = []

    def log(self, event_type: str, data: dict):
        self.events.append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            **data
        })

    def print_logs(self):
        print("\n=== 事件日志 ===")
        for event in self.events:
            print(f"[{event['timestamp']}] {event['type']}")


class MetricsCollector:
    """指标收集器"""
    def __init__(self):
        self.counters = {
            "runs": 0,
            "total_tokens": 0,
            "errors": 0,
        }

    def record(self, metric: str, value: int = 1):
        self.counters[metric] = self.counters.get(metric, 0) + value

    def print_metrics(self):
        print("\n=== 指标统计 ===")
        for key, value in self.counters.items():
            print(f"  {key}: {value}")


class ObservabilityMiddleware(AgentMiddleware):
    """可观测性中间件"""
    def __init__(self, logger, metrics):
        self.logger = logger
        self.metrics = metrics

    async def process(self, context: AgentContext, call_next):
        self.metrics.record("runs")
        self.logger.log("run_started", {"input_count": len(context.input_messages)})

        start_time = time.time()
        try:
            await call_next()
            elapsed = time.time() - start_time
            self.logger.log("run_completed", {"elapsed_ms": elapsed * 1000})
        except Exception as e:
            self.metrics.record("errors")
            self.logger.log("run_error", {"error": str(e)})
            raise


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建可观测性组件
    logger = AgentLogger()
    metrics = MetricsCollector()

    # 创建带中间件的 Agent
    agent = Agent(
        client=client,
        name="ObservableAgent",
        instructions="你是一个有帮助的助手。",
        middleware=[ObservabilityMiddleware(logger, metrics)],
    )

    print("=" * 60)
    print("  Observability Demo - 可观测性")
    print("=" * 60)

    # 运行 Agent
    print("\n--- 运行 Agent ---")
    response = await agent.run("你好")
    print(f"响应: {response.text}")

    # 打印可观测性数据
    logger.print_logs()
    metrics.print_metrics()


if __name__ == "__main__":
    asyncio.run(main())
