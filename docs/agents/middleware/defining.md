# Item 9: Understand the Three Middleware Types

Middleware 在请求到达 Agent 或调用工具之前拦截处理。有三种类型：

## 三种 Middleware

| 类型 | 拦截时机 | Context 类 |
|------|----------|-----------|
| Agent | Agent.run() 调用前后 | AgentContext |
| Function | 工具调用前后 | FunctionInvocationContext |
| Chat | LLM Chat API 调用前后 | ChatContext |

## Agent Middleware

```python
from agent_framework import AgentMiddleware, AgentContext

class LoggingMiddleware(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        print(f"Before agent run: {context.input_messages}")
        await call_next()
        print(f"After agent run")
```

## Function Middleware

```python
from agent_framework import FunctionMiddleware, FunctionInvocationContext

class TimingMiddleware(FunctionMiddleware):
    async def process(self, context: FunctionInvocationContext, call_next):
        import time
        start = time.time()
        await call_next()
        print(f"Tool {context.tool_name} took {time.time() - start}s")
```

## Chat Middleware

```python
from agent_framework import ChatMiddleware, ChatContext

class PromptInjectMiddleware(ChatMiddleware):
    async def process(self, context: ChatContext, call_next):
        context.messages.insert(0, Message(role="system", contents=["Always be concise."]))
        await call_next()
```

## 注册 Middleware

```python
agent = Agent(
    client=client,
    middleware=[LoggingMiddleware(), TimingMiddleware()]
)
```

## Things to Remember

- **Agent Middleware**：拦截 Agent.run()，适合日志、监控
- **Function Middleware**：拦截工具调用，适合计日志、性能追踪
- **Chat Middleware**：拦截 LLM API 调用，适合 prompt 修改
- `await call_next()` 继续执行链，不能忘了
