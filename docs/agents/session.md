# Item 4: Use Sessions to Maintain State Within a Conversation

## 问题

你做多轮对话，但每次调用 Agent 都是"新"的，不记得之前说过什么：

```python
# 用户：第一轮说"我叫李明"
result1 = await agent.run("我叫李明")
print(result1.text)  # "你好，李明！很高兴认识你。"

# 用户：第二轮问"我叫什么？"
result2 = await agent.run("我叫什么名字？")
print(result2.text)  # "你没有告诉我你叫什么名字" —— Agent 失忆了
```

或者你想在多次调用间共享状态，但不知道怎么做：

```python
# 多次调用之间，想共享一些数据
session = agent.create_session()  # 这有什么用？
session.state["count"] = 0

# 下次调用时，count 还是 0？
result = await agent.run("Hello", session=session)
print(session.state.get("count"))  # ???
```

## 深入解释

Agent Framework 中，默认情况下**每次 `agent.run()` 调用都是独立的**。Agent 不会自动记住上一次调用说了什么。

**Session 是 Agent 的"记忆容器"**——它让你的多次调用在同一个上下文中执行：

```
┌─────────────────────────────────────────────────────────────┐
│              无 Session（每次调用独立）                        │
├─────────────────────────────────────────────────────────────┤
│  agent.run("你好")     → Agent 独立执行，无记忆              │
│  agent.run("你叫什么") → Agent 独立执行，无记忆               │
│  agent.run("我叫李明") → Agent 独立执行，无记忆               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              有 Session（共享上下文）                          │
├─────────────────────────────────────────────────────────────┤
│  session = agent.create_session()                            │
│  session.state["name"] = "李明"                             │
│                                                              │
│  agent.run("你好", session=session)  →  session["name"] 可用  │
│  agent.run("你叫什么", session=session) → session["name"] 可用 │
│  agent.run("我叫王五", session=session) → session["name"] 更新 │
└─────────────────────────────────────────────────────────────┘
```

**心智模型**：Session 就像 HTTP 的 Cookie——它让无状态的请求变得有状态，是跨调用保持数据的机制。

## 推荐做法

### 基本 Session 用法

```python
# 创建 Session
session = agent.create_session()

# 第一次调用
result1 = await agent.run("我叫李明", session=session)
print(result1.text)

# 第二次调用（同一 Session，Agent 知道之前说了什么）
result2 = await agent.run("我叫什么名字？", session=session)
print(result2.text)  # "你叫李明"

# Session 间的状态
print(session.state.get("name"))  # "李明"
```

### Session 用于多 Agent 协作

```python
from agent_framework import Agent, AgentSession

# 创建共享 Session
shared_session = AgentSession()

# 多个 Agent 协作处理同一请求
translator_agent = Agent(client=client, name="Translator", instructions="翻译助手")
summarizer_agent = Agent(client=client, name="Summarizer", instructions="摘要助手")

async def handle_user_request(text: str):
    # 翻译
    translated = await translator_agent.run(text, session=shared_session)

    # 摘要（使用同一 Session，能看到翻译历史）
    summary = await summarizer_agent.run(translated.text, session=shared_session)

    return summary.text
```

### Session 状态管理

```python
# Session state 是字典，可以存储任意数据
session = agent.create_session()

# 存储用户信息
session.state["user_id"] = "user123"
session.state["preferences"] = {"theme": "dark", "language": "zh"}

# 存储对话计数
session.state["turn_count"] = 0

async def chat():
    session.state["turn_count"] += 1
    print(f"这是第 {session.state['turn_count']} 轮对话")

    # 存储历史（用于后续分析）
    session.state.setdefault("history", []).append({
        "turn": session.state["turn_count"],
        "timestamp": datetime.now(),
    })
```

## 好 vs 坏对比

```python
# 坏做法：每次调用都是独立的，无记忆
result1 = await agent.run("我叫李明")
result2 = await agent.run("我叫什么？")  # Agent 不记得

# 好做法：用 Session 保持上下文
session = agent.create_session()
result1 = await agent.run("我叫李明", session=session)
result2 = await agent.run("我叫什么？", session=session)  # Agent 记得

# 坏做法：在调用间丢失状态
session1 = agent.create_session()
session1.state["count"] = 0

session2 = agent.create_session()  # 新 Session
print(session2.state.get("count"))  # None —— 状态不共享

# 好做法：同一 Session 内状态持久
session = agent.create_session()
session.state["count"] = 0
await agent.run("Hello", session=session)
await agent.run("World", session=session)
print(session.state["count"])  # 0 —— 保持
```

## 扩展讨论

### Session vs ContextProvider

| 特性 | Session | ContextProvider |
|------|---------|-----------------|
| 生命周期 | 单次 Session | 跨 Session 持久 |
| 作用域 | Session 内共享 | 可跨 Session 共享 |
| 数据类型 | 任意 Python 对象 | 通常是字符串 |
| 典型用途 | 临时状态 | 长期记忆 |

### Session 的限制

```python
# Session 不是跨 Agent 共享的
session1 = agent1.create_session()
session1.state["name"] = "李明"

# agent2 无法访问 session1 的数据
result = await agent2.run("我叫？", session=session1)  # Agent 不知道

# 如果需要跨 Agent 共享 → 用 AgentSession 或 ContextProvider
```

### Session 持久化

```python
import json
from pathlib import Path

async def persist_session(session, path: str):
    """将 Session 状态持久化到文件"""
    data = {
        "state": session.state,
        # 其他需要保存的信息
    }
    Path(path).write_text(json.dumps(data, ensure_ascii=False, default=str))

async def restore_session(agent, path: str):
    """从文件恢复 Session"""
    if Path(path).exists():
        data = json.loads(Path(path).read_text())
        session = agent.create_session()
        session.state.update(data.get("state", {}))
        return session
    return agent.create_session()
```

### Session 清理

```python
# 显式清理 Session
session.delete()

# 或创建新 Session 替代
session.close()

# 使用 with 语句自动清理
async with agent.session() as session:
    result = await agent.run("Hello", session=session)
# session 自动清理
```

### 企业级考虑

```python
# 1. Session 池化管理
class SessionPool:
    def __init__(self, agent, max_size=100):
        self.agent = agent
        self.pool = queue.Queue(maxsize=max_size)
        self.active = {}  # session_id -> session

    def get_session(self) -> AgentSession:
        if not self.pool.empty():
            return self.pool.get()
        return self.agent.create_session()

    def return_session(self, session):
        session.clear()  # 清理状态
        self.pool.put(session)

# 2. Session 超时管理
async def session_with_timeout(session, timeout=3600):
    """Session 自动过期"""
    start = time.time()
    try:
        yield session
    finally:
        if time.time() - start > timeout:
            session.delete()

# 3. Session 监控
class MonitoredSession:
    def __init__(self, session, metrics):
        self.session = session
        self.metrics = metrics

    async def run(self, *args, **kwargs):
        start = time.time()
        result = await self.session.run(*args, **kwargs)
        self.metrics.record("session_run_duration", time.time() - start)
        return result
```

## Things to Remember

- **默认情况下，每次 `agent.run()` 是独立的**，Agent 不会记住之前的调用
- **Session 是 Agent 的"记忆容器"**，用 `session=session` 参数在多次调用间共享状态
- `session.state` 是字典，可以存储任意 Python 对象
- **新 Session = 新的状态空间**，不同 Session 间状态不共享
- Session 适合**单用户单对话的生命周期内**状态管理
- **跨 Session 持久化**需要额外机制（文件/数据库/ContextProvider）
- Session 不是跨 Agent 共享的——每个 Agent 有自己的 Session 空间
- 生产环境中 Session 应该设计超时清理机制，避免内存泄漏
- Session 适合短生命周期状态（对话内），长生命周期用 ContextProvider
