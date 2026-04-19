# Item 13: Think of Workflows as Directed Graphs with Superstep Synchronization

Workflow 是有向图，不是流水线。理解 superstep（超步）同步语义是关键。

## 核心心智模型

```
Superstep 1:  所有节点并行执行
              A: set_state("x", 1)  ─┐
              B: get_state("x") = ?  ─┼─ 本 superstep 内互相看不到
              C: get_state("x") = ?  ─┘

Superstep 边界：状态提交

Superstep 2:  所有节点看到提交的值
              A: get_state("x") = 1
              B: get_state("x") = 1
              C: get_state("x") = 1
```

## 构建工作流

```python
from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler, executor

class UpperCase(Executor):
    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text.upper())

@executor(id="reverse")
async def reverse(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.yield_output(text[::-1])

workflow = (
    WorkflowBuilder(start_executor=UpperCase())
    .add_edge(UpperCase(), reverse)
    .build()
)

result = await workflow.run("hello")
```

## 三种边类型

| 边类型 | 含义 | 场景 |
|--------|------|------|
| SingleEdge | 一对一 | 管道式处理 |
| FanOutEdgeGroup | 一对多 | 广播任务 |
| FanInEdgeGroup | 多对一 | 收集结果 |
| SwitchCaseEdgeGroup | 条件路由 | 分支处理 |

## Things to Remember

- Workflow = Executor 图 + Edge 连接
- Superstep 内 set_state() 的值，同 superstep 内其他节点看不到
- `ctx.send_message()` 发给下游，`ctx.yield_output()` 产出最终结果
- Edge 决定数据流向，不是执行顺序
