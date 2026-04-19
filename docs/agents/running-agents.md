# Item 2: Use Streaming for Real-Time Response and serve() for Development

流式输出让 AI 的思考过程可见；serve() 让 Agent 快速托管到 HTTP 服务。

## 流式输出

### 问题

非流式调用让用户等待完整结果：

```python
result = await agent.run("写一篇关于AI的文章")
print(result.text)  # 干等 30 秒，然后一次性输出
```

### 解决方案

```python
stream = await agent.run(prompt, stream=True)

print("Agent: ", end="", flush=True)
async for update in stream:
    if update.contents:
        for content in update.contents:
            if content.text:
                print(content.text, end="", flush=True)

await stream.get_final_response()
```

### 关键细节

- **flush=True**：立即输出，不等缓冲区
- **get_final_response()**：必须调用
- **update.contents**：内容在列表里，需要遍历

## 本地托管

### 问题

需要让其他服务或前端调用 Agent。

### 解决方案

```python
from agent_framework.devui import serve

agent = Agent(
    client=client,
    name="HostedAgent",
    instructions="你是一个友好的助手",
)

serve(entities=[agent], port=8080, host="127.0.0.1")
```

### 生产安全

```python
serve(
    entities=[agent],
    port=8080,
    host="127.0.0.1",
    auth_enabled=True,
    auth_token="your-secret-token"
)
```

## 托管选项对比

| 选项 | 适用场景 | 生产安全 |
|------|----------|----------|
| DevUI serve() | 本地开发调试 | ❌ 需认证 |
| A2A Protocol | Agent 间通信 | ✅ 生产级 |
| Azure Functions | 无服务器部署 | ✅ 生产级 |

## Things to Remember

- `stream=True` 返回 ResponseStream，不是普通字符串
- `async for update in stream` 遍历每个 chunk
- 必须调用 `get_final_response()` 获取完整响应
- `serve()` 一行启动 HTTP 服务，但默认不安全
- 生产环境必须启用 auth_enabled
