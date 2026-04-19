# Item 22: Middleware Intercepts and Transforms Agent Behavior

Middleware 拦截 Agent 的请求/响应链，在其中注入横切逻辑：日志记录、指标收集、请求改写、响应修改等。

## 中间件心智模型

```
请求 → 中间件1 → 中间件2 → Agent → 中间件3 → 响应
```

## 三种 Middleware

| 类型 | 作用域 | 典型用途 |
|------|--------|----------|
| **AgentMiddleware** | 整个 Agent 运行 | 日志、监控、错误处理 |
| **FunctionMiddleware** | 单个工具调用 | 工具调用日志、参数验证 |
| **ChatMiddleware** | 单个 Chat 消息 | 消息改写、内容过滤 |

## 适用场景

- 日志记录和性能监控
- 请求/响应改写
- 错误处理和重试
- 速率限制和配额管理
- 内容审核和过滤

## Things to Remember

- Middleware 拦截请求/响应链
- 三种类型作用域不同
- 适合横切逻辑，不适合业务逻辑
- 可以组合多个 Middleware
