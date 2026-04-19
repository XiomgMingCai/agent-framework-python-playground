# Workflows as Agents

## Item 23: WorkflowAgent Requires Start Executor Accepting list[Message]

WorkflowAgent 将工作流包装为 Agent，但要求 start executor 能处理 `list[Message]`（Agent 标准输入格式）。

## 错误做法

```python
class TextProcessor(Executor):
    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.yield_output(text.upper())

# 报错：Workflow's start executor cannot handle list[Message]
agent = WorkflowAgent(workflow=workflow)
```

## 正确做法

用 AgentExecutor 作为 start executor：

```python
class SimpleAgent:
    """实现 SupportsAgentRun 协议"""
    def __init__(self):
        self.id = "simple_agent"
        self.name = "SimpleAgent"

    def create_session(self):
        return None

    async def run(self, messages=None, *, stream=False, session=None):
        # 处理 list[Message]
        text = messages[-1].text if messages else ""
        return AgentResponse(messages=[...])

text_agent = SimpleAgent()
agent_executor = AgentExecutor(agent=text_agent)

workflow = (
    WorkflowBuilder(start_executor=agent_executor)
    .build()
)

# 成功
agent = WorkflowAgent(workflow=workflow, name="MyAgent")
```

## 属性速查

| 属性 | 说明 |
|------|------|
| `agent.name` | Agent 名称 |
| `agent.workflow` | 底层工作流 |
| `agent.run()` | 与普通 Agent 相同的调用方式 |

## Things to Remember

- **list[Message] 要求**：WorkflowAgent 要求 start executor 能处理 Agent 标准输入
- **AgentExecutor**：支持多种输入类型，是合法的 start executor
- **如果报错**：`ValueError: Workflow's start executor cannot handle list[Message]` → 用 AgentExecutor 包装
- **统一接口**：workflow.run() = agent.run()，调用方式一样
