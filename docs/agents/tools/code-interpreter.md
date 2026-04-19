# Item 16: Code Interpreter Enables Dynamic Code Execution

Code Interpreter 允许 Agent 在运行时动态执行 Python 代码，返回执行结果。这使得 Agent 能处理计算、文件处理、数据分析等动态任务。

## 执行心智模型

```
Agent 生成代码 → 发送到解释器 → 执行并捕获输出 → 返回结果给 Agent
```

## 基础用法

```python
from agent_framework import Agent
from agent_framework.tools import CodeInterpreter

agent = Agent(
    client=client,
    tools=[CodeInterpreter()],
    instructions="你是一个数据分析师，可以执行 Python 代码进行分析。",
)

response = await agent.run("计算 1 到 100 的和")
# Agent 生成的代码会被自动执行
```

## 典型场景

| 场景 | 示例 |
|------|------|
| **数学计算** | 复杂数学运算、统计 |
| **文件处理** | 读取、处理、生成文件 |
| **数据分析** | 分析 CSV、JSON 数据 |
| **可视化** | 生成图表、绘图 |

## 执行隔离

Code Interpreter 在隔离环境中执行代码，防止危险操作：

```python
interpreter = CodeInterpreter(
    timeout=30,           # 超时时间（秒）
    memory_limit="256MB",  # 内存限制
    allowed_modules=["math", "json", "csv"],  # 允许的模块
)
```

## Things to Remember

- Code Interpreter 执行动态生成的代码
- 所有代码在隔离环境中运行
- 合理设置 timeout 和 memory_limit
- 敏感场景配合 Tool Approval 使用
