# Item 28: Share State Across Middleware with Context

多个 Middleware 需要共享数据（如请求 ID、用户信息）。使用 AgentContext 在 Middleware 之间传递状态。

## 共享状态心智模型

```
Middleware A → 设置 context["request_id"] → Middleware B → 读取 context["request_id"]
```

## 基本用法

```python
class RequestIDMiddleware(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        context["request_id"] = str(uuid.uuid4())
        return await call_next()

class LoggingMiddleware(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        request_id = context.get("request_id", "unknown")
        logger.info(f"[{request_id}] Request started")
        try:
            response = await call_next()
            logger.info(f"[{request_id}] Request completed")
            return response
        except Exception as e:
            logger.error(f"[{request_id}] Request failed: {e}")
            raise
```

## 类型安全的状态共享

```python
from dataclasses import dataclass

@dataclass
class AgentContext:
    request_id: str
    user_id: str
    session_id: str

class ContextualMiddleware(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        # 强类型访问
        logger.info(f"User {context.user_id} session {context.session_id}")
        return await call_next()
```

## 状态初始化顺序

```python
agent = Agent(
    middleware=[
        RequestIDMiddleware(),      # 第1个设置 request_id
        UserAuthMiddleware(),       # 第2个设置 user_id
        LoggingMiddleware(),         # 第3个读取两者
    ]
)
```

## Things to Remember

- context 是 Middleware 间共享的数据容器
- 按注册顺序执行，前面的先设置
- 使用 dataclass 保证类型安全
- 避免在 context 中存储大量数据
