# Item 25: Use Termination to Gracefully Stop Agent Execution

Termination 是 Agent 运行过程中的停止机制，用于实现超时控制、Guardrails（护栏）和人工介入。

## 停止心智模型

```
Agent 运行 → 检测停止条件 → 设置终止标记 → 完成当前步骤 → 退出
```

## 超时终止

```python
from agent_framework.middleware import AgentMiddleware, Termination

class TimeoutMiddleware(AgentMiddleware):
    def __init__(self, timeout_seconds: int):
        self.timeout = timeout_seconds

    async def process(self, context: AgentContext, call_next):
        try:
            await asyncio.wait_for(
                call_next(),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            context.terminate(reason="timeout")
            raise
```

## Guardrails 终止

```python
class ContentGuardrail(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        response = await call_next()

        if self._contains_blocked_content(response):
            context.terminate(reason="content_violation")
            raise AgentTerminationError("内容违反政策")

        return response
```

## 终止原因

| 原因 | 说明 |
|------|------|
| `timeout` | 执行超时 |
| `content_violation` | 内容违规 |
| `user_request` | 用户主动停止 |
| `budget_exceeded` | 超出配额 |

## Things to Remember

- Termination 是优雅停止，不是强制杀死
- 超时用 asyncio.wait_for 实现
- Guardrails 在响应后检查
- 终止时可以返回部分结果
