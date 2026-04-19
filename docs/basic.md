# Item 1: Create Agents with Both a Client and Instructions

Agent 需要两部分才能工作：底层的聊天客户端（client）和上层的行为指令（instructions）。没有 client，Agent 不知道怎么和 LLM 通信；没有 instructions，Agent 不知道该做什么。

## 问题

很多初学者会这样写：

```python
# 缺少 client
agent = Agent(instructions="你是一个有帮助的助手")

# 缺少 instructions
agent = Agent(client=client)
```

这样运行时会报错或产生无意义输出。

## 解决方案

始终同时提供 client 和 instructions：

```python
from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

client = OpenAIChatCompletionClient(
    api_key=os.getenv("AI_API_KEY"),
    base_url=os.getenv("AI_BASE_URL"),
    model=os.getenv("AI_MODEL")
)

agent = Agent(
    client=client,
    name="MyAgent",
    instructions="你是一个有帮助的助手，使用中文回答。"
)
```

## 运行方式

```bash
uv run examples/basic/main.py -p "你好"
```

**输出：**
```
你好！有什么我可以帮你的吗？
```

## Things to Remember

- Agent = client（通信）+ instructions（行为），两者缺一不可
- OpenAIChatCompletionClient 兼容 OpenAI 格式，支持 SiliconFlow、DeepSeek 等
- 通过 os.getenv() 从 .env 读取配置，保持密钥安全
- agent.run(prompt) 返回 AgentResponse，result.text 获取文本
