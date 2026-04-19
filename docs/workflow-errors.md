# Workflow 示例常见错误记录

本文档记录 Workflow 子主题示例中遇到的错误，供后续开发参考。

---

## 1. executors/main.py

### 错误 1: `response_handler` 装饰器签名错误

**错误信息:**
```
TypeError: response_handler() missing 1 required positional argument: 'original_request'
```

**原因:** `response_handler` 装饰器需要 4 个参数，但代码中只写了 3 个。

**修复:**
```python
# 错误写法
@response_handler
async def handle_response(self, response: Any, ctx: WorkflowContext[str]) -> None:
    pass

# 正确写法
@response_handler
async def handle_response(self, original_request: Any, response: Any, ctx: WorkflowContext[str]) -> None:
    pass
```

---

## 2. edges/main.py

### 错误 1: FanInEdgeGroup 类型不兼容

**错误信息:**
```
TypeCompatibilityError: Target 'fan_in_collector' cannot accept input from source 'filter'
```

**原因:** FanIn 的 collector 需要接受多个不同来源的消息，但原代码中定义的类型不兼容。

**修复:** 使用 `Any` 类型或创建中间转换节点。

### 错误 2: SwitchCaseEdgeGroup 的 Case 构造

**错误信息:**
```
TypeError: Case() takes 1 positional argument but 2 were given
```

**原因:** Case 是 dataclass，需要用 keyword argument `condition=` 构造。

**修复:**
```python
# 错误写法
SwitchCaseEdgeGroup([Case(text.startswith("upper"), upper_executor, "upper")])

# 正确写法
SwitchCaseEdgeGroup([Case(condition=text.startswith("upper"), executor=upper_executor, edge_name="upper")])
```

---

## 3. events/main.py

### 错误 1: `WorkflowEvent.status()` 参数错误

**错误信息:**
```
TypeError: status() missing required argument: 'state'
```

**原因:** `status()` 方法需要 `state` 参数，不是 `message`。

**修复:**
```python
# 错误写法
WorkflowEvent.status(message="进行中")

# 正确写法
WorkflowEvent.status(state=WorkflowRunState.IN_PROGRESS)
```

### 错误 2: `WorkflowEvent.emit()` vs `WorkflowEvent.data()`

**错误信息:**
```
AttributeError: 'WorkflowEvent' object has no attribute 'data'
```

**原因:** 应该用 `emit()` 而不是 `data()` 创建事件。

**修复:**
```python
# 错误写法
WorkflowEvent.data("processor", "some data")

# 正确写法
WorkflowEvent.emit("processor", "some data")
```

### 错误 3: `WorkflowEvent.failed()` 参数错误

**错误信息:**
```
TypeError: failed() missing required argument: 'details'
```

**原因:** `details` 参数类型是 `WorkflowErrorDetails`，需要用 keyword argument。

**修复:**
```python
# 正确写法
WorkflowEvent.failed(details=WorkflowErrorDetails(error_type="FATAL", message="致命错误"))
```

---

## 4. checkpoints/main.py

### 错误 1: `FileCheckpointStorage` 参数名错误

**错误信息:**
```
TypeError: __init__() missing 1 required argument: 'storage_path'
```

**原因:** 参数名是 `storage_path` 不是 `checkpoint_dir`。

**修复:**
```python
# 错误写法
file_storage = FileCheckpointStorage(checkpoint_dir=tmpdir)

# 正确写法
file_storage = FileCheckpointStorage(storage_path=tmpdir)
```

---

## 5. human_in_the_loop/main.py

### 错误 1: `workflow.graph` 不存在

**错误信息:**
```
AttributeError: 'Workflow' object has no attribute 'graph'
```

**原因:** Workflow 对象使用 `executors` 和 `edge_groups` 属性，不是 `graph`。

**修复:**
```python
# 错误写法
print(f"执行器数: {len(workflow.graph.nodes)}")

# 正确写法
print(f"执行器数: {len(workflow.executors)}")
print(f"边组数: {len(workflow.edge_groups)}")
```

---

## 6. observability/main.py

### 错误 1: `WorkflowEvent.source` 不存在

**错误信息:**
```
AttributeError: 'WorkflowEvent' object has no attribute 'source'
```

**原因:** 应该用 `origin` 属性。

**修复:**
```python
# 错误写法
"source": str(event.source) if event.source else None,

# 正确写法
"origin": str(event.origin) if event.origin else None,
```

### 错误 2: `WorkflowEventType` 枚举值不存在

**错误信息:**
```
AttributeError: 'WorkflowEventType' object has no attribute 'EXECUTOR_INVOKED'
```

**原因:** 实际枚举值是 `EXECUTOR_INVOKED` 格式，但框架实现可能不同。使用字符串字面量代替。

**修复:**
```python
# 使用字符串字面量代替枚举
if event.type == "executor_invoked":
    self.metrics["executor_invocations"] += 1
```

---

## 7. workflows_as_agents/main.py

### 错误 1: `WorkflowAgent` 要求 start executor 接受 `list[Message]`

**错误信息:**
```
ValueError: Workflow's start executor cannot handle list[Message]
```

**原因:** `WorkflowAgent` 将工作流包装为 Agent 时，要求 start executor 必须能处理 `list[Message]` 类型输入（Agent 的标准输入格式）。普通的文本处理 executor 只能处理 `str`。

**修复:** 使用 `AgentExecutor` 作为 start executor，因为 `AgentExecutor` 支持多种输入类型包括 `list[Message]`。

```python
# 创建支持 list[Message] 的 AgentExecutor
class SimpleTextAgent:
    """实现 SupportsAgentRun 协议"""
    def __init__(self):
        self.id = "simple_text_agent"
        self.name = "SimpleTextAgent"
        self.description = "简单的文本处理 Agent"

    def create_session(self):
        return None

    async def run(self, messages=None, *, stream=False, session=None, **kwargs):
        # 处理逻辑
        return AgentResponse(...)

text_agent = SimpleTextAgent()
agent_executor = AgentExecutor(agent=text_agent, id="text_agent_executor")
workflow = WorkflowBuilder(start_executor=agent_executor).build()
agent = WorkflowAgent(workflow=workflow, name="AnalysisAgent")
```

---

## 8. visualization/main.py

### 错误 1: `workflow.graph` 不存在

**错误信息:**
```
AttributeError: 'Workflow' object has no attribute 'graph'
```

**原因:** Workflow 对象没有 `graph` 属性，应该使用 `executors` 和 `edge_groups`。

**修复:**
```python
# 错误写法
for node in workflow.graph.nodes:
    print(f"  - {node.id}")

# 正确写法
for exec_id, executor in workflow.executors.items():
    print(f"  - {exec_id} ({type(executor).__name__})")

# 边遍历
for edge_group in workflow.edge_groups:
    for edge in edge_group.edges:
        print(f"  - {edge.source_id} → {edge.target_id}")
```

### 错误 2: `workflow.workflow_id` 不存在

**错误信息:**
```
AttributeError: 'Workflow' object has no attribute 'workflow_id'
```

**原因:** Workflow 的 ID 属性是 `id` 不是 `workflow_id`。

**修复:**
```python
# 错误写法
print(f"workflow_id: {workflow.workflow_id}")

# 正确写法
print(f"workflow_id: {workflow.id}")
```

---

## 9. agents_in_workflows/main.py

### 错误 1: `AgentExecutor` 没有 `invoke` 方法

**错误信息:**
```
AttributeError: 'AgentExecutor' object has no attribute 'invoke'
```

**原因:** `AgentExecutor` 是工作流的组件，不能直接调用 `invoke()`。需要通过工作流来运行。

**修复:**
```python
# 错误写法
result = await agent_executor.invoke(messages=[...])

# 正确写法 - 通过工作流运行
workflow = (
    WorkflowBuilder(start_executor=agent_executor)
    .build()
)
result = await workflow.run(message=[...])
```

注意: 如果没有实际 LLM client，可以用结构演示代替实际运行。

---

## 10. state/main.py

### 错误 1: `State` 类不存在

**错误信息:**
```
ImportError: cannot import name 'State' from 'agent_framework'
```

**原因:** 状态管理使用 `WorkflowContext.get_state()` 和 `ctx.set_state()`，不需要单独的 `State` 类。

**修复:**
```python
# 删除 State 导入，直接使用 ctx.get_state/set_state
# ctx.get_state("key", default=0)
# ctx.set_state("key", value)
```

---

## 通用经验总结

### Workflow 对象属性速查

| 旧代码 | 正确代码 |
|--------|----------|
| `workflow.graph.nodes` | `workflow.executors.items()` |
| `workflow.graph.edges` | `workflow.edge_groups` |
| `workflow.workflow_id` | `workflow.id` |

### WorkflowEvent 创建方法

| 事件类型 | 正确方法 |
|----------|----------|
| started | `WorkflowEvent.started()` |
| status | `WorkflowEvent.status(state=WorkflowRunState.XXX)` |
| emit/data | `WorkflowEvent.emit(executor_id, data)` |
| output | `WorkflowEvent.output(executor_id, data)` |
| error | `WorkflowEvent.error(Exception(...))` |
| failed | `WorkflowEvent.failed(details=WorkflowErrorDetails(...))` |

### Executor 类型兼容性

- **普通 Executor**: 处理 `str`、`int` 等简单类型
- **AgentExecutor**: 处理 `list[Message]`、`AgentExecutorRequest` 等类型
- **WorkflowAgent 包装**: 要求 start executor 能处理 `list[Message]`
