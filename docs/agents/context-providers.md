# Item 5: Use ContextProvider to Inject State Across Sessions

## 问题

你试图在 Session 中保存用户信息，但发现 Session 切换后数据丢失：

```python
# Session 1：用户说"我叫李明"
session1 = agent.create_session()
session1.state["name"] = "李明"
session1.state["preferences"] = {"theme": "dark"}

# Session 2：用户重新开始，但希望 Agent 记得"李明"
session2 = agent.create_session()
print(session2.state.get("name"))  # None —— 数据丢失了
```

或者你想在每次 Agent 调用前自动注入用户历史信息，但不知道怎么做：

```python
# 每次调用都要手动拼接，太繁琐
result = await agent.run(f"用户历史：{history}\n\n当前问题：{query}")
```

## 深入解释

ContextProvider 是 Agent Framework 的**拦截器模式**——它能拦截 `agent.run()` 的完整生命周期，在适当的位置注入或提取数据：

```
┌─────────────────────────────────────────────────────────────┐
│                    agent.run() 执行流程                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  ContextProvider.before_run()                         │    │
│  │  • 读取 state 中的记忆                                │    │
│  │  • 注入到 context（Agent 的指令上下文）                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│                    LLM 模型调用                              │
│                          ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  ContextProvider.after_run()                          │    │
│  │  • 从输入中提取新信息                                 │    │
│  │  • 写入 state 持久化                                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**心智模型**：ContextProvider 就像 Web 框架的 **Middleware**——请求前后有机会处理逻辑，但它操作的是 Agent 的"上下文"而非 HTTP 请求。

## 推荐做法

### 自定义 MemoryProvider

```python
from agent_framework import ContextProvider, Agent

class MemoryProvider(ContextProvider):
    def __init__(self):
        super().__init__("memory")

    async def before_run(self, *, agent, session, context, state):
        """在模型调用前：读取记忆，注入上下文"""
        memories = state.get("memories", [])

        if memories:
            # 将最近 3 条记忆注入 Agent 上下文
            recent = memories[-3:]
            memory_text = "\n".join(f"- {m}" for m in recent)
            context.extend_instructions(
                self.source_id,
                f"\n【用户历史记忆】\n{memory_text}\n"
            )

    async def after_run(self, *, agent, session, context, state):
        """在模型调用后：从输入中提取重要信息，写入 state"""
        # 获取用户输入
        for msg in context.input_messages:
            if hasattr(msg, 'contents'):
                for c in msg.contents:
                    if hasattr(c, 'text') and c.text:
                        text = c.text
                        # 简单规则：包含"我叫"、"我叫"的提取为记忆
                        if "我叫" in text or "我的名字是" in text:
                            if text not in state.get("memories", []):
                                state.setdefault("memories", []).append(text)

# 使用
agent = Agent(
    client=client,
    context_providers=[MemoryProvider()],
    instructions="你是一个友好的助手，能记住用户之前说过的话。",
)
```

### 持久化 MemoryProvider（跨 Session）

```python
import json
from pathlib import Path

class PersistentMemoryProvider(ContextProvider):
    def __init__(self, storage_path: str = "memory.json"):
        super().__init__("persistent-memory")
        self.storage_path = Path(storage_path)
        self.storage = self._load()

    def _load(self) -> dict:
        if self.storage_path.exists():
            return json.loads(self.storage_path.read_text())
        return {}

    def _save(self):
        self.storage_path.write_text(json.dumps(self.storage, ensure_ascii=False))

    async def before_run(self, *, agent, session, context, state):
        user_id = state.get("user_id", "anonymous")
        memories = self.storage.get(user_id, [])

        if memories:
            recent = memories[-5:]
            memory_text = "\n".join(f"- {m}" for m in recent)
            context.extend_instructions(
                self.source_id,
                f"\n【用户历史】\n{memory_text}\n"
            )

    async def after_run(self, *, agent, session, context, state):
        user_id = state.get("user_id", "anonymous")
        for msg in context.input_messages:
            if hasattr(msg, 'contents'):
                for c in msg.contents:
                    if hasattr(c, 'text') and c.text:
                        text = c.text
                        if any(kw in text for kw in ["我叫", "我的", "我喜欢"]):
                            if text not in self.storage.get(user_id, []):
                                self.storage.setdefault(user_id, []).append(text)
        self._save()
```

## 好 vs 坏对比

```python
# 坏做法：每次手动拼接历史
history_text = "\n".join(history)
result = await agent.run(f"{history_text}\n\n{user_input}")

# 好做法：用 ContextProvider 自动注入
agent = Agent(
    client=client,
    context_providers=[MemoryProvider()],  # 自动处理
)
result = await agent.run(user_input)  # 干干净净

# 坏做法：Session 切换后记忆丢失
session1 = agent.create_session()
session1.state["name"] = "李明"
session2 = agent.create_session()
print(session2.state.get("name"))  # None

# 好做法：用 ContextProvider + 持久化存储
agent = Agent(context_providers=[PersistentMemoryProvider()])
# 每个 Session 都能访问历史记忆
```

## 扩展讨论

### 与 Session 的区别

| 特性 | Session | ContextProvider |
|------|---------|-----------------|
| 生命周期 | 单次 Session | 跨 Session 持久 |
| 作用域 | 单用户/单会话 | 可跨会话共享 |
| 典型用途 | 临时状态 | 长期记忆 |
| 数据写入 | Session 结束时丢失 | 可持久化到存储 |

### before_run vs after_run

```python
class MyProvider(ContextProvider):
    async def before_run(self, *, agent, session, context, state):
        # 读取 state → 注入 context
        # 例：加载用户偏好、记忆、上下文
        pass

    async def after_run(self, *, agent, session, context, state):
        # 读取 input → 写入 state
        # 例：保存新信息、持久化
        pass
```

### 多个 Provider 组合

```python
agent = Agent(
    client=client,
    context_providers=[
        MemoryProvider(),        # 用户记忆
        PreferencesProvider(),   # 用户偏好
        KnowledgeProvider(),    # 知识库
    ],
)
# 按注册顺序执行 before_run，逆序执行 after_run
```

### 企业级考虑

```python
# 1. Provider 优先级
class PriorityProvider(ContextProvider):
    async def before_run(self, *, agent, session, context, state):
        # 高优先级：安全/合规检查
        await self.check_compliance(context)
        # 低优先级：个性化记忆
        await self.load_memory(context)

# 2. Provider 错误隔离
class SafeProvider(ContextProvider):
    async def before_run(self, *, agent, session, context, state):
        try:
            await self.risky_operation()
        except Exception as e:
            logger.warning(f"Provider failed: {e}")  # 不影响主流程
```

## Things to Remember

- ContextProvider 是**拦截器**，在 `agent.run()` 生命周期中注入逻辑
- `before_run()`：读取 state，注入 context（为 LLM 准备上下文）
- `after_run()`：读取 input messages，写入 state（保存新信息）
- ContextProvider 可以实现**跨 Session 的记忆持久化**，Session 本身不行
- `context.extend_instructions()` 向 Agent 指令追加内容
- 多个 Provider 可以组合，按注册顺序执行
- Provider 错误应该隔离捕获，不应阻断主流程
- 持久化存储（文件/数据库）让记忆跨越应用重启
