# Item 10: Use Agent Pipeline to Chain Multiple Agents Together

## 问题

你想让多个 Agent 协作完成复杂任务，但不知道怎么做：

```python
# 你想做：翻译 → 总结 → 分析
translator = Agent(client=client, name="Translator", ...)
summarizer = Agent(client=client, name="Summarizer", ...)
analyzer = Agent(client=client, name="Analyzer", ...)

# 但你怎么让它们顺序执行？
result1 = await translator.run(text)        # 第一步
result2 = await summarizer.run(result1.text) # 第二步
result3 = await analyzer.run(result2.text)   # 第三步
# 这样写可以，但不够优雅，错误处理麻烦
```

或者你想让一个 Agent 判断下一步该调用哪个 Agent：

```python
# 你想让 Router Agent 自动决定调用哪个 Worker
router = Agent(client=client, name="Router", ...)

# 但怎么让 Router 调用其他 Agent？
# Agent 不能直接调用其他 Agent
```

## 深入解释

**Agent Pipeline = 多个 Agent 按顺序/条件协作**：

```
┌─────────────────────────────────────────────────────────────┐
│              单 Agent（无法处理复杂任务）                       │
├─────────────────────────────────────────────────────────────┤
│  User Input → Agent → Response                              │
│                                                              │
│  适合：简单、独立的任务                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Agent Pipeline（多 Agent 协作）                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Input → Router → [Translator] → [Summarizer] → ...   │
│                      ↓                                       │
│                   Worker 1                                   │
│                      ↓                                       │
│                   Worker 2                                   │
│                      ↓                                       │
│                   Response                                    │
│                                                              │
│  适合：复杂任务、需要多角色协作                               │
└─────────────────────────────────────────────────────────────┘
```

**心智模型**：Pipeline 就像**工厂流水线**——原材料（User Input）经过多个工序（Agent）加工，最终产出成品（Response），每个工序专注做一件事。

## 推荐做法

### 顺序 Pipeline

```python
async def pipeline_sequential(user_input: str) -> str:
    """顺序执行多个 Agent"""

    # Step 1: 翻译
    translator = Agent(
        client=client,
        name="Translator",
        instructions="将文本翻译成英文，保持专业术语准确。"
    )
    translated = await translator.run(user_input)

    # Step 2: 总结
    summarizer = Agent(
        client=client,
        name="Summarizer",
        instructions="用简洁的语言总结文本要点，不超过 3 句话。"
    )
    summarized = await summarizer.run(translated.text)

    # Step 3: 分析
    analyzer = Agent(
        client=client,
        name="Analyzer",
        instructions="分析文本，给出专业评价和建议。"
    )
    analyzed = await analyzer.run(summarized.text)

    return analyzed.text


# 使用
result = await pipeline_sequential("你的长文本内容...")
```

### 带 Session 共享的 Pipeline

```python
async def pipeline_with_session(user_input: str) -> str:
    """Pipeline 共享 Session，让 Agent 感知完整上下文"""

    # 创建共享 Session
    session = AgentSession()

    translator = Agent(client=client, name="Translator", instructions="翻译成英文...")
    summarizer = Agent(client=client, name="Summarizer", instructions="总结上文...")
    analyzer = Agent(client=client, name="Analyzer", instructions="分析上文...")

    # 同一个 Session，所有 Agent 共享历史
    t_result = await translator.run(user_input, session=session)
    s_result = await summarizer.run(t_result.text, session=session)
    a_result = await analyzer.run(s_result.text, session=session)

    return a_result.text
```

### Router Agent（条件路由）

```python
from enum import Enum

class RequestType(Enum):
    TRANSLATION = "translation"
    SUMMARY = "summary"
    ANALYSIS = "analysis"
    OTHER = "other"

async def router_pipeline(user_input: str) -> str:
    """Router Agent 判断请求类型，路由到对应 Worker"""

    # Router 负责分类
    router = Agent(
        client=client,
        name="Router",
        instructions="""
        分析用户输入，判断属于哪种类型：
        - translation: 需要翻译
        - summary: 需要总结
        - analysis: 需要分析
        - other: 其他

        只输出一个词：translation/summary/analysis/other
        """
    )

    request_type_text = await router.run(user_input)
    request_type = request_type_text.text.strip().lower()

    # 根据类型路由到不同 Worker
    if request_type == "translation":
        worker = Agent(client=client, name="Translator", instructions="翻译成英文...")
        result = await worker.run(user_input)
    elif request_type == "summary":
        worker = Agent(client=client, name="Summarizer", instructions="总结要点...")
        result = await worker.run(user_input)
    elif request_type == "analysis":
        worker = Agent(client=client, name="Analyzer", instructions="深度分析...")
        result = await worker.run(user_input)
    else:
        default_agent = Agent(client=client, name="Default", instructions="通用回答...")
        result = await default_agent.run(user_input)

    return result.text
```

### 并行 Pipeline

```python
async def pipeline_parallel(user_input: str) -> str:
    """多个 Agent 并行处理，返回组合结果"""

    # 三个 Agent 并行执行
    translator = Agent(client=client, name="Translator", instructions="翻译成英文...")
    summarizer = Agent(client=client, name="Summarizer", instructions="总结...")
    sentiment = Agent(client=client, name="Sentiment", instructions="分析情感...")

    # 并行启动
    t_task = asyncio.create_task(translator.run(user_input))
    s_task = asyncio.create_task(summarizer.run(user_input))
    se_task = asyncio.create_task(sentiment.run(user_input))

    # 等待所有完成
    t_result, s_result, se_result = await asyncio.gather(t_task, s_task, se_task)

    # 组合结果
    combiner = Agent(
        client=client,
        name="Combiner",
        instructions="整合多个分析结果为连贯的报告。"
    )

    combined = await combiner.run(
        f"翻译：{t_result.text}\n\n总结：{s_result.text}\n\n情感分析：{se_result.text}"
    )

    return combined.text
```

## 好 vs 坏对比

```python
# 坏做法：硬编码顺序，无错误处理
result1 = await translator.run(text)
result2 = await summarizer.run(result1.text)
result3 = await analyzer.run(result2.text)
# 中间任何一步失败，整个 Pipeline 就断了

# 好做法：Pipeline 封装 + 错误处理
async def safe_pipeline(user_input: str) -> str:
    try:
        session = AgentSession()
        translator = Agent(client=client, name="Translator", ...)
        summarizer = Agent(client=client, name="Summarizer", ...)

        result = await translator.run(user_input, session=session)
        if not result.text:
            return "翻译失败"

        summarized = await summarizer.run(result.text, session=session)
        if not summarized.text:
            return "总结失败"

        return summarized.text
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return f"处理失败: {e}"
```

## 扩展讨论

### Pipeline 模式对比

| 模式 | 特点 | 适用场景 |
|------|------|----------|
| **Sequential** | 顺序执行，上一步输出下一步输入 | 强依赖的步骤 |
| **Parallel** | 并行执行，汇总结果 | 独立子任务 |
| **Router** | 条件路由到不同分支 | 多类型请求 |
| **Fan-out/Fan-in** | 分发到多个，结果汇总 | 批量处理 |

### Pipeline 中间件

```python
class PipelineLoggingMiddleware(Middleware):
    async def on_agent_start(self, agent, input_data, context):
        print(f"[Pipeline] {agent.name} started")

    async def on_agent_end(self, agent, output, context):
        print(f"[Pipeline] {agent.name} ended: {output.text[:50]}...")

    async def on_error(self, agent, error, context):
        print(f"[Pipeline] {agent.name} error: {error}")
        raise error  # Pipeline 通常应该 fail-fast
```

### 超时和重试

```python
async def pipeline_with_timeout(user_input: str) -> str:
    try:
        result = await asyncio.wait_for(
            sequential_pipeline(user_input),
            timeout=30.0
        )
        return result
    except asyncio.TimeoutError:
        return "处理超时，请稍后重试"

async def pipeline_with_retry(user_input: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            return await sequential_pipeline(user_input)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(1 * (attempt + 1))  # 指数退避
```

### 企业级考虑

```python
# 1. Pipeline 配置外部化
class PipelineConfig:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def get_pipeline(self, name: str) -> list[dict]:
        return self.config["pipelines"][name]

# pipelines.yaml
# my_pipeline:
#   - agent: translator
#     timeout: 10
#   - agent: summarizer
#     timeout: 5

# 2. Pipeline 监控
class PipelineMetrics:
    def record_pipeline_duration(self, pipeline_name: str, duration: float):
        # 发送到 Prometheus
        pipeline_duration.labels(pipeline=pipeline_name).observe(duration)

    def record_pipeline_step(self, pipeline_name: str, step: str, success: bool):
        pipeline_steps.labels(pipeline=pipeline_name, step=step, success=success).inc()
```

## Things to Remember

- **Pipeline = 多个 Agent 顺序/条件协作**，解决复杂任务
- **Sequential Pipeline**：强依赖步骤，上一步输出是下一步输入
- **Parallel Pipeline**：独立子任务并行执行，最后汇总
- **Router Pipeline**：条件路由，根据输入决定调用哪个 Agent
- **共享 Session** 让多个 Agent 能感知完整上下文
- Pipeline 需要**错误处理**（try/except）和**超时控制**
- 每个 Agent 在 Pipeline 中应该**职责单一**
- Pipeline 失败时应该**快速失败**（fail-fast），不要传播错误到下游
- 复杂 Pipeline 应该**配置外部化**，而不是硬编码
