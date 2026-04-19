# Item 29: Access Runtime Context to Understand Agent State

Runtime Context 包含 Agent 运行时的完整信息：输入消息、历史记录、工具调用状态、中间结果。Middleware 可以读取这些信息来做决策。

## 运行时上下文心智模型

```
Agent 运行中 → Context 保存状态 → Middleware 读取 → 决定如何处理
```

## 可访问的信息

| 信息 | 说明 | 用途 |
|------|------|------|
| `input_messages` | 用户输入列表 | 输入分析、审核 |
| `output_messages` | Agent 输出列表 | 输出分析、缓存 |
| `tool_calls` | 工具调用记录 | 调用审计 |
| `state` | Agent 内部状态 | 调试、监控 |
| `metadata` | 自定义元数据 | 传递额外信息 |

## 读取上下文

```python
class InputAnalysisMiddleware(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        # 分析输入
        if not context.input_messages:
            return await call_next()

        last_input = context.input_messages[-1]
        word_count = len(last_input.text.split())

        # 记录指标
        metrics.histogram("input_words", word_count)

        # 拒绝过长输入
        if word_count > 10000:
            return AgentResponse(
                text="输入过长，请缩短问题。"
            )

        return await call_next()
```

## 写入上下文

```python
class MetadataMiddleware(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        response = await call_next()

        # 添加自定义元数据
        context.metadata["processed_at"] = datetime.now().isoformat()
        context.metadata["model_version"] = response.model_version

        return response
```

## Things to Remember

- Runtime Context 保存 Agent 运行时的完整状态
- Middleware 可以读取和写入 Context
- 输入分析、输出审核都依赖 Context
- 不要修改输入消息，添加新字段
