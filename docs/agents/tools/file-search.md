# Item 17: File Search Enables codebase Intelligence

File Search 让 Agent 能够搜索和读取本地文件。这使得 Agent 可以理解项目结构、阅读源码、回答关于代码库的问题。

## 搜索心智模型

```
用户查询 → 定位相关文件 → 读取文件内容 → 基于内容回答
```

## 基础用法

```python
from agent_framework import Agent
from agent_framework.tools import FileSearch

agent = Agent(
    client=client,
    tools=[FileSearch(root=".", patterns=["**/*.py"])],
    instructions="你是一个代码库助手，可以搜索和阅读文件。",
)

response = await agent.run("找到所有使用 asyncio 的文件")
```

## 搜索模式

| 模式 | 说明 | 示例 |
|------|------|------|
| `*.py` | 单扩展名 | `**/*.py` |
| `*.{js,ts}` | 多扩展名 | `**/*.{js,ts}` |
| `!**/node_modules/**` | 排除目录 | 跳过第三方代码 |

## 读取限制

```python
file_search = FileSearch(
    root="./src",
    patterns=["**/*.py"],
    max_file_size=1024 * 1024,  # 最大 1MB
    max_files=50,               # 最多读取 50 个文件
)
```

## Things to Remember

- File Search 按 glob 模式匹配文件
- 可以限制搜索根目录和文件大小
- 结合上下文注入提升回答质量
- 跳过 node_modules 等第三方目录
