# Item 4: Pass Full History to Each Turn, Not Just the Latest Message

多轮对话的关键：每次调用都要传完整的历史，而不是只传新消息。

## 问题

新手常犯的错误：

```python
# 错误：只传新消息
response = await agent.run("我叫李明")
response = await agent.run("我叫什么名字？")  # Agent 不记得了
```

Agent 没有记忆，每次调用都是独立的。

## 解决方案

维护历史列表，每次传入完整上下文：

```python
history: list[Message] = []

while True:
    user_input = input("\nYou: ")
    history.append(Message(role="user", contents=[user_input]))

    stream = await agent.run(messages=history, stream=True)

    # 收集 Agent 回复
    full_response = ""
    async for update in stream:
        if update.contents:
            for content in update.contents:
                if content.text:
                    full_response += content.text

    # 把 Agent 回复也加入历史
    history.append(Message(role="assistant", contents=[full_response]))
```

## 历史管理策略

| 策略 | 方法 | 适用场景 |
|------|------|----------|
| 无限历史 | `history.append()` | 短对话 |
| 滑动窗口 | `history[-max_messages:]` | 长对话 |
| 摘要压缩 | 定期压缩为摘要 | 超长对话 |

## Things to Remember

- `history: list[Message]` = [user, assistant, user, assistant, ...]
- 每次 `agent.run(messages=history)` 传入完整历史
- 用户消息加 `role="user"`，Agent 回复加 `role="assistant"`
- 长对话用滑动窗口裁剪，控制 token 消耗
