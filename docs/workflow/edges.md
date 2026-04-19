# Edges

## Item 15: Choose the Right Edge Type for Your Data Flow Pattern

Edge 决定数据如何流动。根据场景选择合适的边类型。

## 四种边类型

| 类型 | 类 | 何时用 |
|------|------|--------|
| 一对一 | SingleEdgeGroup | 管道式处理 |
| 一对多 | FanOutEdgeGroup | 广播任务 |
| 多对一 | FanInEdgeGroup | 收集结果 |
| 条件路由 | SwitchCaseEdgeGroup | 分支处理 |

## SingleEdge（一对一）

```python
workflow = (
    WorkflowBuilder(start_executor=upper)
    .add_edge(upper, reverse)  # upper → reverse
    .build()
)
```

## FanOut（一对多）

```python
workflow = (
    WorkflowBuilder(start_executor=producer)
    .add_fan_out_edges(producer, [triple, square])  # → triple AND → square
    .build()
)
```

## FanIn（多对一）

```python
workflow = (
    WorkflowBuilder(start_executor=source)
    .add_fan_in_edges([upper, lower], to_string)  # upper + lower → to_string
    .build()
)
```

## SwitchCase（条件路由）

```python
from agent_framework import Case, Default

workflow = (
    WorkflowBuilder(start_executor=router)
    .add_switch_case_edge_group(
        router,
        {
            Case("large"): triple,
            Case("small"): square,
            Default(): passthrough,
        },
    )
    .build()
)
```

## Things to Remember

- **edge_name**：用 `ctx.send_message(data, edge_name="xxx")` 指定路由标签
- **Case(condition=...)**：Condition 需要用 keyword argument 构造
- **Default()**：无匹配时走默认路由
- **FanIn 注意事项**：collector 需要接受多个来源的消息，注意类型兼容
