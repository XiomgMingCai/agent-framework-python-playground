# Agents in Workflows

## Item 17: AgentExecutor Wraps an Agent, It Is Not an Agent

Agent 需要用 AgentExecutor 包装才能加入工作流，而不是直接放进 WorkflowBuilder。

## 错误做法

```python
# Agent 不能直接作为工作流节点
workflow = (
    WorkflowBuilder(start_executor=agent)  # 错误！
    .build()
)
```

## 正确做法

```python
agent_executor = AgentExecutor(agent=agent)

workflow = (
    WorkflowBuilder(start_executor=preprocessor)
    .add_edge(preprocessor, agent_executor)  # AgentExecutor 可以
    .build()
)
```

## 完整示例

```python
from agent_framework import AgentExecutor, Agent, WorkflowBuilder

# 创建 Agent
agent = Agent(
    client=client,
    name="Translator",
    instructions="将输入翻译成英文"
)

# 包装为 Executor
translator_executor = AgentExecutor(agent=agent)

# 构建工作流
workflow = (
    WorkflowBuilder(start_executor=preprocessor)
    .add_edge(preprocessor, translator_executor)
    .add_edge(translator_executor, summarizer)
    .build()
)
```

## Things to Remember

- **Agent ≠ Executor**：Agent 需要用 AgentExecutor 包装
- **AgentExecutor 输入类型**：支持 list[Message]、str、Message 等
- **多 Agent 协作**：用 add_edge() 连接多个 AgentExecutor
- **不支持 invoke()**：AgentExecutor 是工作流组件，没有 invoke 方法
