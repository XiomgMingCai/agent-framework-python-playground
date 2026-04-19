# Human-in-the-Loop

## Item 20: Use request_info() as a Pause Button, Not a End Button

`ctx.request_info()` 是工作流的暂停按钮，不是结束。暂停后等待外部响应，然后继续执行。

## 基本用法

```python
class HumanApproval(Executor):
    @handler
    async def check(self, text: str, ctx: WorkflowContext[str]) -> None:
        # 暂停，等待外部响应
        approved = await ctx.request_info(
            prompt=f"请确认是否处理：{text}",
            expected_type=bool,
        )

        # 收到响应后继续执行
        if approved:
            await ctx.send_message(f"已批准: {text}")
        else:
            await ctx.yield_output(f"已拒绝: {text}")
```

## 响应处理

```python
class Interactive(Executor):
    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        result = await ctx.request_info(prompt="输入内容", expected_type=str)

    @response_handler
    async def handle_response(self, original_request, response, ctx) -> None:
        # 处理外部响应
        await ctx.send_message(f"收到: {response}")
```

## 应用场景

| 场景 | 用法 |
|------|------|
| 审批流程 | approved → send_message，rejected → yield_output |
| 人工输入 | 等待用户输入字符串/数字 |
| 异常处理 | 出错时人工介入决定如何处理 |

## Things to Remember

- **request_info = 暂停按钮**：等待 expected_type 类型的响应后继续
- **expected_type**：指定期望的响应类型（bool、str、int 等）
- **response_handler**：装饰器方法处理响应（4 个参数）
- **不是结束**：收到响应后工作流继续执行，不是终止
