# Events

## Item 16: Use WorkflowEvent Factory Methods, Not Constructors

工作流事件用工厂方法创建，不要直接实例化。

## 工厂方法

```python
from agent_framework import WorkflowEvent, WorkflowRunState, WorkflowErrorDetails

# 开始事件
event = WorkflowEvent.started()

# 状态事件（注意参数名是 state）
event = WorkflowEvent.status(state=WorkflowRunState.IN_PROGRESS)

# 输出事件
event = WorkflowEvent.output("processor", "result data")

# 警告事件
event = WorkflowEvent.warning("注意：某些数据未处理")

# 错误事件
event = WorkflowEvent.error(Exception("处理失败"))

# 失败事件
event = WorkflowEvent.failed(
    details=WorkflowErrorDetails(error_type="FATAL", message="致命错误")
)
```

## 遍历事件

```python
result: WorkflowRunResult = await workflow.run(input)

for event in result:
    print(f"{event.type} | {event.data}")

# 获取输出
outputs = result.get_outputs()  # 所有 type='output' 的 data

# 获取最终状态
final_state = result.get_final_state()
```

## 常见事件类型

| 类型 | 何时触发 |
|------|----------|
| `started` | 工作流开始 |
| `executor_invoked` | Executor 被调用 |
| `executor_completed` | Executor 完成 |
| `output` | 产生输出 |
| `completed` | 工作流完成 |

## Things to Remember

- **工厂方法**：started()、status(state=...)、emit()、output()、error()、failed(details=...)
- **status() 参数**：是 `state` 不是 `message`
- **output()**：接收 executor_id 和 data 两个参数
- **result 是 list**：直接遍历就是事件列表
- `result.get_outputs()` 获取所有输出
