# Item 6: Use serve() for Development, Not Production

DevUI 的 `serve()` 是快速验证的好帮手，但它不是为生产设计的。

## 问题

直接暴露到网络很危险：

```python
serve(entities=[agent], port=8080)  # 没有任何认证
# 任何人可以调用你的 Agent
```

## 解决方案

开发时仅本地访问：

```python
serve(
    entities=[agent],
    port=8080,
    host="127.0.0.1",  # 仅本地
    auth_enabled=True,  # 启用认证
    auth_token="your-secret-token"
)
```

```bash
curl -X POST http://localhost:8080/api/agents/AgentName/run \
  -H "Authorization: Bearer your-secret-token" \
  -d "你好"
```

## 托管选项对比

| 选项 | 适用场景 | 生产安全 |
|------|----------|----------|
| DevUI serve() | 本地开发调试 | ❌ 需要认证 |
| A2A Protocol | Agent 间通信 | ✅ 建议生产 |
| Azure Functions | 无服务器部署 | ✅ 生产级 |
| OpenAI-Compatible | 接入现有客户端 | ✅ 视情况 |

## Things to Remember

- `serve()` 一行启动 HTTP 服务，但默认不安全
- 生产环境必须启用 auth_enabled 或限制 host
- DevUI 适合本地验证，不适合直接部署
- Agent 和 Workflow 都可以托管：`entities=[agent, workflow]`
