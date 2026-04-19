# A2A 示例

基于 FastAPI 的 A2A Server + Python A2AAgent Client 完整示例。

## 什么是 A2A？

A2A（Agent-to-Agent）协议是用于 Agent 之间通信的标准化协议，支持：
- **Agent 发现**：通过 AgentCard 描述能力
- **消息传递**：支持同步和异步消息
- **流式响应**：通过 SSE 实现实时流式输出
- **任务追踪**：状态机管理长期运行的任务

## 运行方式

**终端 1 - 启动 A2A Server:**
```bash
uv run examples/a2a/server/main.py
```

**终端 2 - 启动 A2A Client:**
```bash
uv run examples/a2a/client/main.py
```

## 架构

```
┌─────────────────┐        A2A 协议         ┌─────────────────┐
│   FastAPI       │ ←────────────────────── │   A2AAgent     │
│   A2A Server   │   HTTP + JSON/SSE        │   Client       │
│                 │                          │                 │
│  /.well-known/  │ ──────────────────────→ │  发现 Agent    │
│  agent-card.json│                          │  发送消息       │
│                 │                          │  流式响应       │
└─────────────────┘                          └─────────────────┘
```

## 核心概念

### AgentCard

用于描述 Agent 的能力和元数据：
- `name`: Agent 名称
- `capabilities`: 支持的功能（流式、推送通知等）
- `skills`: Agent 擅长的技能
- `url`: Agent 服务地址

### 消息格式

A2A 使用 JSON-RPC 2.0 格式：
- `message/send`: 同步消息发送
- `message/stream`: 流式消息（通过 SSE 返回）

### 流式响应

流式响应通过 Server-Sent Events (SSE) 实现，事件顺序：
1. **Task** - 任务对象（包含 task_id 和 context_id）
2. **TaskStatusUpdateEvent** - 状态更新（消息内容在 `status.message` 中）
3. **TaskStatusUpdateEvent (final=True)** - 最终状态

## 关键 API

### Server

| 端点 | 方法 | 说明 |
|------|------|------|
| `/.well-known/agent-card.json` | GET | 获取 Agent Card |
| `/` | POST | JSON-RPC 统一端点 |
| `/tasks/{task_id}` | GET | 获取任务状态 |
| `/health` | GET | 健康检查 |

### Client

```python
# 发现 Agent
resolver = A2ACardResolver(httpx_client=http_client, base_url=a2a_host)
agent_card = await resolver.get_agent_card()

# 非流式对话
async with A2AAgent(name=agent_card.name, agent_card=agent_card, url=a2a_host) as agent:
    response = await agent.run("你好")

# 流式对话
stream = agent.run("你好", stream=True)
async for update in stream:
    print(update.text)
final = await stream.get_final_response()
```

## 注意事项

1. **流式响应格式**：消息内容必须放在 `TaskStatusUpdateEvent.status.message` 中，而不是单独的 `Message` 对象
2. **Task 对象**：第一个事件必须是包含 `id` 和 `context_id` 的 `Task` 对象
3. **最终状态**：需要发送 `final=True` 的 `TaskStatusUpdateEvent` 表示任务完成