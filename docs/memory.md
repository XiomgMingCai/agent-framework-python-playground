# Item 5: Use ContextProvider to Inject State Across Sessions

Session 是一次性的，但 ContextProvider 可以跨 Session 持久化记忆。

## 问题

Session 的 state 只在当前 Session 内有效：

```python
session1 = agent.create_session()
session1.state["name"] = "李明"  # 只在 session1 内有效

session2 = agent.create_session()
print(session2.state.get("name"))  # None，两个 session 不共享
```

如果想让 Agent "记住"跨对话的信息，需要 ContextProvider。

## 解决方案

用 ContextProvider 拦截 run 的生命周期：

```python
class MemoryProvider(ContextProvider):
    async def before_run(self, *, agent, session, context, state):
        # 从 state 读记忆，注入到 context
        memories = state.get("memories", [])
        if memories:
            context.extend_instructions(
                self.source_id,
                f"用户之前提过：{memories[-3:]}"
            )

    async def after_run(self, *, agent, session, context, state):
        # 从输入提取新信息，写入 state
        for msg in context.input_messages:
            if "重要信息" in msg.text:
                state.setdefault("memories", []).append(msg.text)

agent = Agent(
    client=client,
    context_providers=[MemoryProvider()]
)
```

## 生命周期

```
before_run() → LLM 调用 → after_run()
     ↓               ↓
   读 state         写 state
   注入 context
```

## Things to Remember

- ContextProvider = 拦截器，before_run 读 state 注入 context，after_run 写 state 持久化
- `extend_instructions()` 向 Agent 注入个性化指令
- `Session.state` 是跨调用持久化的字典
- `agent.create_session()` 创建的新 Session 状态隔离
