# Executors

## Item 14: Distinguish Between Classes and Functions for Different Complexity Levels

Executor 是工作流的节点。有两种创建方式：类定义适合复杂逻辑和有状态场景，函数装饰器适合简单转换。

## 类定义 Executor（有状态）

```python
from agent_framework import Executor, WorkflowContext, handler

class Counter(Executor):
    def __init__(self, id: str = "counter"):
        super().__init__(id=id)
        self._count = 0

    @handler
    async def increment(self, _: str, ctx: WorkflowContext[int]) -> None:
        self._count += 1
        ctx.set_state("count", self._count)
        await ctx.send_message(self._count)
```

## 函数 Executor（无状态）

```python
from agent_framework import executor, WorkflowContext

@executor(id="upper")
async def upper(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(text.upper())
```

## AgentExecutor（嵌入 LLM）

```python
from agent_framework import AgentExecutor, Agent

agent = Agent(client=client, name="AIAssistant", instructions="...")
agent_executor = AgentExecutor(agent=agent)
```

## response_handler（4 个参数）

```python
class Interactive(Executor):
    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        result = await ctx.request_info(prompt="确认？", expected_type=bool)

    @response_handler
    async def handle_response(self, original_request, response, ctx) -> None:
        pass  # 处理响应
```

## Things to Remember

- **类 Executor**：继承 `Executor`，用 `@handler` 标记处理方法，适合有状态逻辑
- **函数 Executor**：用 `@executor(id="...")` 装饰器，适合简单转换
- **AgentExecutor**：包装 Agent 使其参与工作流
- **response_handler**：4 个参数 `(self, original_request, response, ctx)`
- `ctx.send_message()` 发送给下游，`ctx.yield_output()` 产出最终结果
