# Item 1: Create Agents with Both a Client and Instructions

## 问题

很多开发者在第一次创建 Agent 时，会遗漏其中关键的一个组成部分：

```python
# 错误：缺少 client，Agent 无法与 LLM 通信
agent = Agent(instructions="你是一个有帮助的助手")
result = await agent.run("你好")  # 抛出异常：No client configured

# 错误：缺少 instructions，Agent 不知道如何行为
agent = Agent(client=client)
result = await agent.run("你好")  # Agent 可能表现随机或无厘头
```

当你看到 `AgentResponse` 返回空文本或 `AttributeError` 时，首先检查这两部分是否完整。

## 深入解释

Microsoft Agent Framework 的核心抽象是**分离关注点**：

```
┌──────────────────────────────────────────────────────┐
│                      Agent                            │
│  ┌──────────────────┐    ┌────────────────────────┐  │
│  │     Client       │ +  │    Instructions       │  │
│  │                  │    │                       │  │
│  │ • API 通信       │    │ • 角色定义             │  │
│  │ • 模型选择        │    │ • 行为规范             │  │
│  │ • 认证/重试      │    │ • 输出格式期望          │  │
│  └──────────────────┘    └────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

**Client 的职责**：负责与外部 LLM 服务通信，处理认证、超时、重试、响应解析等底层细节。

**Instructions 的职责**：定义 Agent 的角色定位、回答风格、工具选择策略、边界约束等高层行为逻辑。

这两部分是正交的——同一个 Client 可以搭配不同的 Instructions 创建多个不同角色的 Agent；同一个 Instructions 也可以搭配不同的 Client 以适应不同的模型或部署环境。

## 推荐做法

始终同时提供 client 和 instructions，并显式管理两者的生命周期：

```python
import os
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

# 1. 加载环境变量
load_dotenv()

# 2. 创建 Client（底层通信）
client = OpenAIChatCompletionClient(
    api_key=os.getenv("AI_API_KEY"),
    base_url=os.getenv("AI_BASE_URL"),
    model=os.getenv("AI_MODEL"),
)

# 3. 创建 Agent（行为定义）
agent = Agent(
    client=client,
    name="MyAgent",
    instructions="你是一个专业、友好的助手，使用中文回答。回答要简洁实用。"
)

# 4. 运行
result = await agent.run("你好")
print(result.text)
```

**关键原则**：
- client 和 agent 对象在应用生命周期内通常只创建一次，复用多次
- instructions 应该具体、可操作，避免模糊的描述
- 敏感配置（API key）通过环境变量注入，不要硬编码

## 扩展讨论

### 同一 Client 驱动多个 Agent

```python
# 不同 Instructions，同一 Client
client = OpenAIChatCompletionClient(...)

code_agent = Agent(client=client, name="Coder", instructions="你是一个 Python 专家...")
review_agent = Agent(client=client, name="Reviewer", instructions="你是一个代码审查员...")
data_agent = Agent(client=client, name="DataAnalyst", instructions="你是一个数据分析专家...")
```

### Client 类型选择

| Client | 适用场景 |
|--------|----------|
| `OpenAIChatCompletionClient` | 兼容 OpenAI Chat Completions API（SiliconFlow、DeepSeek、自建） |
| `OpenAIChatClient`（新版） | 仅支持 OpenAI 官方 Responses API |
| `FoundryChatClient` | Azure AI Foundry 部署环境 |

**心智模型**：Client 是**通信层**，Instructions 是**行为层**。分离两者让你能独立切换模型或调整行为，而不影响另一层。

### 企业级考虑

- **配置外部化**：将 API endpoint、model 等配置放入环境变量或配置中心，而不是代码中
- **Client 复用**：避免每次请求创建新 Client，连接池和认证 token 复用能显著降低延迟
- **Instructions 版本化**：复杂的 Instructions 应该像代码一样版本化管理，便于回滚和审计

## Things to Remember

- Agent = **client**（通信能力）+ **instructions**（行为规范），两者缺一不可
- Client 负责与 LLM 服务通信，处理认证、重试、响应解析等底层细节
- Instructions 定义 Agent 的角色、风格、边界，相当于"系统提示词"
- 敏感配置（API key、endpoint）必须通过环境变量注入，不要硬编码
- 同一个 Client 可以搭配多个不同的 Agent，实现角色复用
- 创建 Client 和 Agent 的开销很小，应用生命周期内应该复用而非每次请求重建
- 选择 Client 类型前，先确认你的 API 服务商支持的是 Chat Completions 还是 Responses API
