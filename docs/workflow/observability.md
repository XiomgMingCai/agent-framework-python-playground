# Observability

## Item 22: Collect Logs, Metrics, and Traces Together

可观测性三要素：Logs（发生了什么）、Metrics（发生了多少次）、Traces（执行路径）。三者缺一不可。

## 三要素

| 要素 | 关注点 | 实现 |
|------|--------|------|
| **Logs** | 事件时间线 | 记录每个事件的时间和类型 |
| **Metrics** | 数值统计 | 计数 executor_invocations 等 |
| **Traces** | 执行链路 | 追踪 stage 之间的流转 |

## 实现示例

```python
class WorkflowLogger:
    """Logs"""
    def log_event(self, event: WorkflowEvent):
        self.events.append({
            "timestamp": datetime.now().isoformat(),
            "type": event.type,
            "origin": event.origin,
            "data": event.data,
        })

class MetricsCollector:
    """Metrics"""
    def process_event(self, event: WorkflowEvent):
        if event.type == "executor_invoked":
            self.metrics["executor_invocations"] += 1
        elif event.type == "output":
            self.metrics["outputs_produced"] += 1

class WorkflowTracer:
    """Traces"""
    def record(self, stage: str, data: dict):
        self.trace.append({
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            **data,
        })
```

## 收集方式

```python
result = await workflow.run(input)

for event in result:
    logger.log_event(event)
    metrics.process_event(event)
```

## Things to Remember

- **Logs = 时间线**：记录"发生了什么"
- **Metrics = 计数**：统计"发生了多少次"
- **Traces = 链路**：追踪"执行路径"
- **event.origin**：标识事件来自框架还是 Executor
- **遍历 result**：直接 `for event in result` 收集所有事件
