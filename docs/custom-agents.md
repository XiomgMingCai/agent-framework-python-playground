# Item 10: Use BaseAgent When You Need Full Control

大多数场景用内置 `Agent` 就够了。只有当需要完全控制执行逻辑时，才继承 `BaseAgent`。

## 问题

有时候需要不用 LLM 的 Agent，比如：

- Echo Agent（回显）
- Mock Agent（测试）
- 自定义协议的 Agent

这时不能用内置 Agent。

## 解决方案

继承 BaseAgent：

```python
from agent_framework import (
    BaseAgent, AgentResponse, AgentResponseUpdate,
    Message, Content, ResponseStream, normalize_messages
)

class EchoAgent(BaseAgent):
    def __init__(self, prefix: str = "Echo: "):
        self.prefix = prefix
        super().__init__(name="EchoAgent")

    async def _run(self, messages, *, session=None):
        normalized = normalize_messages(messages)
        text = normalized[-1].text if normalized else "Hello"
        response_msg = Message(
            role="assistant",
            contents=[Content.from_text(f"{self.prefix}{text}")]
        )
        return AgentResponse(messages=[response_msg])

    def run(self, messages=None, *, stream=False, session=None):
        if stream:
            return ResponseStream(
                self._run_stream(messages, session),
                finalizer=AgentResponse.from_updates,
            )
        return self._run(messages, session=session)
```

## 流式实现

```python
async def _run_stream(self, messages, session=None):
    normalized = normalize_messages(messages)
    text = normalized[-1].text if normalized else "Hello"

    words = text.split()
    for i, word in enumerate(words):
        chunk = f" {word}" if i > 0 else word
        yield AgentResponseUpdate(
            contents=[Content.from_text(chunk)],
            role="assistant"
        )
        await asyncio.sleep(0.05)
```

## Things to Remember

- `BaseAgent` 是自定义 Agent 的基类，必须实现 run() 方法
- `normalize_messages()` 标准化输入消息格式
- `ResponseStream` 包装流式响应，需要返回 AsyncIterable
- `@overload` 装饰器声明非流式/流式的不同返回类型
- `session.state` 存储自定义 Agent 的状态
