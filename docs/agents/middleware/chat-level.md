# Item 23: Use ChatMiddleware to Transform Individual Messages

ChatMiddleware 作用于单个 Chat 消息级别，在消息进入或离开时进行转换、验证、过滤。

## 消息级别心智模型

```
用户消息 → ChatMiddleware(输入) → Agent → ChatMiddleware(输出) → 用户响应
```

## 基础用法

```python
from agent_framework.middleware import ChatMiddleware

class InputFilterMiddleware(ChatMiddleware):
    """输入过滤：敏感词替换"""
    async def process_input(self, message: ChatMessage):
        message.content = message.content.replace("密码", "***")
        return message

    async def process_output(self, message: ChatMessage):
        return message

agent = Agent(
    client=client,
    middleware=[InputFilterMiddleware()],
)
```

## 消息转换链

```python
class ChainMiddleware(ChatMiddleware):
    def __init__(self, middlewares: list[ChatMiddleware]):
        self.middlewares = middlewares

    async def process_input(self, message: ChatMessage):
        for mw in self.middlewares:
            message = await mw.process_input(message)
        return message
```

## 常见模式

| 模式 | 用途 |
|------|------|
| **Input Filter** | 敏感词过滤、输入验证 |
| **Output Transform** | 响应改写、格式调整 |
| **Audit Log** | 记录对话内容 |
| **Content Warning** | 添加警告信息 |

## Things to Remember

- ChatMiddleware 作用于单条消息
- 输入过滤在消息进入前处理
- 输出转换在消息发出前处理
- 可以链式组合多个中间件
