# State Management

## Item 18: Remember That State Is Visible Only After the Superstep Commits

State 在 superstep 边界提交。同一 superstep 内，set_state() 设置的值其他节点看不到。

## Superstep 语义

```
Superstep 1:
  A: set_state("x", 1)   ← 设置 x = 1
  B: get_state("x") = ?   ← 看不到 A 的值，可能是旧值
  ↓ superstep 结束，状态提交

Superstep 2:
  A: get_state("x") = 1   ← 现在能看到上一轮提交的值
  B: get_state("x") = 1
```

## 代码示例

```python
class Counter(Executor):
    @handler
    async def count(self, _: str, ctx: WorkflowContext[int]) -> None:
        # get_state 读取上一 superstep 提交的值
        current = ctx.get_state("count", default=0)

        # set_state 设置本 superstep 的值
        # 同 superstep 内其他节点看不到这个值
        ctx.set_state("count", current + 1)

        await ctx.send_message(current + 1)
```

## 错误例子

```python
# 错误：期望同 superstep 内立即看到更新
class BadExample(Executor):
    @handler
    async def process(self, x: int, ctx: WorkflowContext[int]) -> None:
        ctx.set_state("sum", ctx.get_state("sum", 0) + x)
        # 下一行读不到刚设置的值！
        total = ctx.get_state("sum", 0)  # 仍然是旧值
```

## Things to Remember

- **get_state()**：读取上一个 superstep 提交的值
- **set_state()**：写入当前 superstep，但同 superstep 内其他节点不可见
- **跨超步可见**：下一个 superstep 才能读到本轮提交的值
- **带默认值**：`ctx.get_state("key", default=0)` 避免 None
