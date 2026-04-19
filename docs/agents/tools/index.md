# Item 14: Tools Are How AgentsInteract with the World

Tools extend Agent 的能力边界，让它能执行代码、搜索文件、查询网络。理解工具的本质是**带结构化输出的函数调用**。

## 工具心智模型

```
Agent 决策 → 选择工具 → 等待结果 → 继续推理
```

工具不是 Agent 的一部分，而是 Agent **可调用**的外部能力。Agent 自己不执行工具，由底层运行时代为执行。

## 工具类型

| 类型 | 用途 | 示例 |
|------|------|------|
| **Function Tool** | 执行 Python 函数 | `get_weather()`, `calculate()` |
| **Code Interpreter** | 执行动态代码 | Python 代码执行环境 |
| **File Search** | 搜索本地文件 | 读取项目源码 |
| **Web Search** | 搜索互联网 | 查最新资讯 |
| **MCP Tool** | 第三方服务 | Slack、GitHub 集成 |

## 共同模式

所有工具都有两个核心属性：

```python
class Tool:
    name: str        # 唯一标识符
    description: str # 帮助 LLM 理解何时使用
```

工具的 `description` 是最关键的字段 — 它直接决定 LLM 何时选择这个工具。

## 审批机制

生产环境中，工具调用通常需要人工审批：

```python
agent = Agent(
    client=client,
    tools=[dangerous_tool],
    tool_approval=ToolApproval(approver=human_review),
)
```

## Things to Remember

- 工具 = 函数 + 元数据（name、description）
- `description` 决定 LLM 何时调用
- 工具由运行时执行，不是 Agent 自己执行
- 敏感工具需要审批机制保护
- MCP 工具通过 Model Context Protocol 接入外部服务
