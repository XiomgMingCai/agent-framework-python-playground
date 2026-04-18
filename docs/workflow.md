# Workflows

通过 Workflow 将多个步骤串联起来，每个步骤处理数据后传递给下一个步骤。

## 前置知识

- 已完成[基础对话](basic.md)
- 了解 Python 异步编程基础

## 核心概念

```
Input: "hello world"
         ↓
    UpperCase 步骤
    (转换为大写)
         ↓
     "HELLO WORLD"
         ↓
   ReverseText 步骤
    (翻转字符串)
         ↓
   Output: "DLROW OLLEH"
```

## 示例代码

**文件：** `examples/workflow/main.py`

```python
import asyncio

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler, executor


# Step 1: A class-based executor that converts text to uppercase
class UpperCase(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def to_upper_case(self, text: str, ctx: WorkflowContext[str]) -> None:
        """Convert input to uppercase and forward to the next node."""
        await ctx.send_message(text.upper())


# Step 2: A function-based executor that reverses the string and yields output
@executor(id="reverse_text")
async def reverse_text(text: str, ctx: WorkflowContext[str]) -> None:
    """Reverse the string and yield the final workflow output."""
    await ctx.yield_output(text[::-1])


def create_workflow():
    """Build the workflow: UpperCase → reverse_text."""
    upper = UpperCase(id="upper_case")
    return WorkflowBuilder(start_executor=upper).add_edge(upper, reverse_text).build()


async def main():
    workflow = create_workflow()

    test_cases = ["hello world", "Python", "Microsoft Agent Framework"]

    for test_input in test_cases:
        events = await workflow.run(test_input)
        outputs = events.get_outputs()
        output = outputs[0] if outputs else ""

        print_workflow_flow(test_input, output)


if __name__ == "__main__":
    asyncio.run(main())
```

## 运行

```bash
uv run examples/workflow/main.py
```

## 输出示例

```
╔══════════════════════════════════════════════════════════════╗
║                    Workflow 执行过程                        ║
╠══════════════════════════════════════════════════════════════╣
║   Input: "hello world"                                       ║
║                          ↓                                   ║
║                  ┌─────────────────┐                         ║
║                  │    UpperCase    │                         ║
║                  │  (转换为大写)    │                         ║
║                  └─────────────────┘                         ║
║                          ↓                                   ║
║                    "HELLO WORLD"                            ║
║                          ↓                                   ║
║                  ┌─────────────────┐                         ║
║                  │   ReverseText   │                         ║
║                  │   (翻转字符串)   │                         ║
║                  └─────────────────┘                         ║
║                          ↓                                   ║
║   Output: "DLROW OLLEH"                                     ║
╚══════════════════════════════════════════════════════════════╝
```

## 核心要点

| 组件 | 说明 |
|------|------|
| `Executor` | 工作流步骤基类，处理输入并转发到下一个节点 |
| `@handler` | 装饰器，标记处理方法 |
| `WorkflowContext.send_message()` | 发送消息到下一个步骤 |
| `WorkflowContext.yield_output()` | 产出工作流最终输出 |
| `@executor` | 函数装饰器，将函数转为 Executor |
| `WorkflowBuilder` | 工作流构建器，连接各步骤 |
| `add_edge()` | 添加步骤之间的边（数据流向） |
| `workflow.run()` | 运行工作流 |

## 两种 Executor 定义方式

### 1. 类定义（适合复杂逻辑）

```python
class UpperCase(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text.upper())
```

### 2. 函数装饰器（适合简单逻辑）

```python
@executor(id="my_executor")
async def my_func(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(text.upper())
```

## WorkflowContext 方法

| 方法 | 说明 |
|------|------|
| `ctx.send_message(data)` | 发送数据到下一个步骤 |
| `ctx.yield_output(data)` | 产出工作流最终结果 |
| `ctx.get_state(key)` | 获取工作流状态 |
| `ctx.set_state(key, value)` | 设置工作流状态 |
