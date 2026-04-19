# Item 24: Match Middleware Scope to Your Logging Granularity

Middleware 有两种作用域：Agent 级别（整个运行）和 Run 级别（单次调用）。选择正确的粒度影响性能和行为。

## 作用域对比

| 维度 | AgentMiddleware | RunMiddleware |
|------|-----------------|---------------|
| **生命周期** | Agent 整个生命周期 | 单次 run() 调用 |
| **状态共享** | 跨调用共享 | 每次调用独立 |
| **性能** | 初始化一次 | 每次初始化 |
| **适用场景** | 持久化资源 | 每次独立的上下文 |

## AgentMiddleware

```python
class AgentMiddleware:
    """作用域：Agent 整个生命周期"""
    def __init__(self):
        self.connection = create_db_connection()  # 初始化一次

    async def process(self, context: AgentContext, call_next):
        # 可以访问 self.connection
        await call_next()
```

## RunMiddleware

```python
class RunMiddleware:
    """作用域：单次 run() 调用"""
    async def process(self, context: RunContext, call_next):
        # 每次 run() 独立初始化
        await call_next()
```

## 选择指南

| 场景 | 推荐作用域 |
|------|-----------|
| 数据库连接池 | AgentMiddleware |
| 请求 ID 生成 | RunMiddleware |
| 限流计数器 | AgentMiddleware |
| 调试日志 | RunMiddleware |

## Things to Remember

- AgentMiddleware：跨调用共享状态
- RunMiddleware：每次调用独立
- 持久化资源用 AgentMiddleware
- 需要独立上下文的用 RunMiddleware
