# Item 18: Web Search Extends Agent Knowledge Beyond Training Data

Web Search 让 Agent 能够搜索互联网，获取最新信息、实时数据、新闻资讯。解决了 LLM 知识截止日期的问题。

## 搜索心智模型

```
用户查询 → 搜索互联网 → 获取结果 → 综合回答
```

## 基础用法

```python
from agent_framework import Agent
from agent_framework.tools import WebSearch

agent = Agent(
    client=client,
    tools=[WebSearch()],
    instructions="你是一个研究助手，可以搜索网络获取最新信息。",
)

response = await agent.run("今天有什么科技新闻？")
```

## 搜索配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `engine` | 搜索引擎 | auto-detect |
| `num_results` | 返回结果数 | 5 |
| `language` | 结果语言 | en |

## 结果注入

搜索结果会自动注入到 Agent 上下文：

```python
web_search = WebSearch(
    num_results=10,
    inject_as="search_results",  # 注入的上下文键名
)
```

## Things to Remember

- Web Search 解决知识时效性问题
- 合理配置返回结果数量
- 搜索结果会注入为 Agent 上下文
- 配合 Tool Approval 控制搜索范围
