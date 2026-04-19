# Item 11: Collect Logs, Metrics, and Traces Together

## 问题

你的 Agent 在生产环境出了问题，但你只能靠猜：

```python
# 出问题了，你只能
result = await agent.run(user_input)
print(result.text)  # "抱歉，我无法处理"

# 但为什么无法处理？不知道
# 是模型的问题？工具的问题？输入的问题？中间件的问题？
```

或者你想知道 Agent 的性能如何，但没有任何数据：

```python
# Agent 跑了一天
# 你只知道"它工作着"，但不知道：
# - 调用了多少次？
# - 平均响应时间是多少？
# - 哪些工具被调用了？
# - 有多少次错误？
```

## 深入解释

**可观测性（Observability）三要素**：

```
┌─────────────────────────────────────────────────────────────┐
│                    可观测性 = 你知道发生了什么                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📝 Logs（事件日志）                                        │
│     关注点：发生了什么？                                      │
│     例子：2024-01-15 14:30:25 Agent.run() 被调用           │
│                                                              │
│  📊 Metrics（指标）                                          │
│     关注点：发生了多少次？                                     │
│     例子：过去 1 小时调用了 1523 次，平均响应时间 1.2s       │
│                                                              │
│  🔗 Traces（链路追踪）                                       │
│     关注点：执行路径是什么？                                  │
│     例子：UserInput → Agent → Tool1 → Tool2 → Response     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**心智模型**：Logs 是**事后验尸**（出了事再看），Metrics 是**实时仪表盘**（随时看），Traces 是**手术刀**（精确定位问题在哪一步）。

## 推荐做法

### 基础实现

```python
from datetime import datetime
from agent_framework import Agent, Middleware

class AgentLogger:
    """Logs：记录事件"""

    def __init__(self, log_file: str = "agent.log"):
        self.log_file = open(log_file, "a", encoding="utf-8")

    def log(self, level: str, event: str, data: dict = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "event": event,
            **(data or {})
        }
        self.log_file.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.log_file.flush()

    def close(self):
        self.log_file.close()


class MetricsCollector:
    """Metrics：收集指标"""

    def __init__(self):
        self.counters = {
            "agent_runs": 0,
            "tool_calls": 0,
            "errors": 0,
        }
        self.histogram = []  # 响应时间

    def record_run(self, duration: float):
        self.counters["agent_runs"] += 1
        self.histogram.append(duration)

    def record_tool_call(self):
        self.counters["tool_calls"] += 1

    def record_error(self):
        self.counters["errors"] += 1

    def get_stats(self) -> dict:
        avg_duration = sum(self.histogram) / len(self.histogram) if self.histogram else 0
        return {
            **self.counters,
            "avg_duration_ms": avg_duration * 1000,
        }


class AgentTracer:
    """Traces：追踪执行链路"""

    def __init__(self):
        self.spans = []  # (parent_id, name, start, end)

    def start_span(self, name: str, parent_id: str = None) -> str:
        span_id = f"span_{len(self.spans)}"
        self.spans.append({
            "id": span_id,
            "parent_id": parent_id,
            "name": name,
            "start": datetime.now(),
            "end": None,
        })
        return span_id

    def end_span(self, span_id: str):
        for span in self.spans:
            if span["id"] == span_id:
                span["end"] = datetime.now()
                break

    def get_trace_tree(self) -> list:
        """构建链路树"""
        result = []
        for span in self.spans:
            duration = None
            if span["start"] and span["end"]:
                duration = (span["end"] - span["start"]).total_seconds() * 1000
            result.append({
                **span,
                "duration_ms": duration,
                "start": span["start"].isoformat() if span["start"] else None,
                "end": span["end"].isoformat() if span["end"] else None,
            })
        return result
```

### Middleware 集成

```python
class ObservabilityMiddleware(Middleware):
    """可观测性中间件"""

    def __init__(self, logger: AgentLogger, metrics: MetricsCollector, tracer: AgentTracer):
        self.logger = logger
        self.metrics = metrics
        self.tracer = tracer

    async def on_agent_start(self, agent, input_data, context):
        span_id = self.tracer.start_span("agent_run")
        self.logger.log("INFO", "agent_start", {"span_id": span_id})
        return span_id

    async def on_agent_end(self, agent, output, context, span_id: str):
        self.tracer.end_span(span_id)
        self.logger.log("INFO", "agent_end", {"span_id": span_id})

    async def on_tool_call(self, tool_name: str, args: dict, context):
        self.metrics.record_tool_call()
        self.logger.log("INFO", "tool_call", {"tool": tool_name, "args": args})
        span_id = self.tracer.start_span(f"tool_{tool_name}")
        return span_id

    async def on_tool_end(self, tool_name: str, result, context, span_id: str):
        self.tracer.end_span(span_id)
        self.logger.log("INFO", "tool_end", {"tool": tool_name, "result": str(result)[:200]})

    async def on_error(self, error: Exception, context):
        self.metrics.record_error()
        self.logger.log("ERROR", "agent_error", {"error": str(error)})


# 使用
logger = AgentLogger()
metrics = MetricsCollector()
tracer = AgentTracer()

agent = Agent(
    client=client,
    middleware=[ObservabilityMiddleware(logger, metrics, tracer)],
)
```

## 好 vs 坏对比

```python
# 坏做法：没有任何可观测性
agent = Agent(client=client)
result = await agent.run(user_input)  # 出了问题无法追溯

# 好做法：全链路可观测
agent = Agent(
    client=client,
    middleware=[ObservabilityMiddleware(logger, metrics, tracer)],
)
# 可以：
# - 从 Logs 看到发生了什么
# - 从 Metrics 看到调用统计
# - 从 Traces 看到执行路径
```

## 扩展讨论

### 与标准可观测性工具集成

```python
# 1. OpenTelemetry 集成
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class OTelMiddleware(Middleware):
    async def on_agent_start(self, agent, input_data, context):
        span = tracer.start_span("agent_run")
        span.set_attribute("agent.name", agent.name)
        return span

# 2. Prometheus 集成
from prometheus_client import Counter, Histogram, start_http_server

requests_total = Counter("agent_requests_total", "Total agent requests")
request_duration = Histogram("agent_request_duration_seconds", "Request duration")

# 3. 结构化日志（JSON）
import json

class JSONLogger:
    def log(self, level: str, event: str, data: dict):
        print(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "event": event,
            **data
        }, ensure_ascii=False))
```

### 生产环境配置

```python
# 开发环境：详细日志
logger = AgentLogger(level="DEBUG")

# 生产环境：关键事件日志
logger = AgentLogger(level="WARNING")

# 采样策略（高流量时降采样）
class SampledLogger:
    def __init__(self, sample_rate: float = 0.1):
        self.sample_rate = sample_rate

    def log(self, level: str, event: str, data: dict):
        if random.random() < self.sample_rate:
            self.base_logger.log(level, event, data)
```

### 调试模式

```python
class DebugMiddleware(Middleware):
    async def on_agent_start(self, agent, input_data, context):
        print(f"[DEBUG] Agent started: {agent.name}")
        print(f"[DEBUG] Input: {input_data}")

    async def on_agent_end(self, agent, output, context):
        print(f"[DEBUG] Agent ended")
        print(f"[DEBUG] Output: {output}")

    async def on_tool_call(self, tool_name: str, args: dict, context):
        print(f"[DEBUG] Tool called: {tool_name}")
        print(f"[DEBUG] Args: {args}")

    async def on_tool_end(self, tool_name: str, result, context):
        print(f"[DEBUG] Tool result: {result}")
```

## Things to Remember

- **可观测性三要素**：Logs（事件）+ Metrics（统计）+ Traces（链路）
- **Logs** = "发生了什么"，关注时间线和事件详情
- **Metrics** = "发生了多少次"，关注聚合的数值统计
- **Traces** = "执行路径是什么"，关注 span 之间的调用关系
- Middleware 是实现可观测性的**标准拦截点**
- 生产环境必须接入标准可观测性工具（OpenTelemetry、Prometheus 等）
- **不要等到出问题了才想到可观测性**——提前埋点
- 采样策略在高流量场景很重要，避免日志爆炸
- 链路追踪可以精确定位"哪一步"出了问题，Logs 告诉"发生了什么"
