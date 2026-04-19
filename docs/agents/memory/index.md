# Item 19: Memory Is How Agents Retain Information Across Sessions

Memory 系统让 Agent 能够在多次对话中保持状态。不同于 Session 的单会话上下文，Memory 是跨会话的持久化存储。

## 存储心智模型

```
会话开始 → 加载历史 Memory → 对话 → 保存新 Memory → 会话结束
```

## Memory vs Session

| 维度 | Session | Memory |
|------|---------|--------|
| **范围** | 单会话 | 跨会话 |
| **生命周期** | 会话内 | 永久 |
| **用途** | 多轮对话 | 长期记忆 |
| **实现** | 消息历史 | 持久化存储 |

## 实现架构

```python
from agent_framework.memory import Memory, MemoryStore

class VectorMemoryStore(MemoryStore):
    """向量数据库存储"""
    async def add(self, content: str, metadata: dict):
        vector = await embed(content)
        self.store.append({"vector": vector, "content": content, "metadata": metadata})

    async def search(self, query: str, top_k: int) -> list[dict]:
        query_vector = await embed(query)
        return self._cosine_search(query_vector, top_k)

memory = Memory(store=VectorMemoryStore())
```

## Memory 类型

| 类型 | 适用场景 | 实现难度 |
|------|----------|----------|
| **向量存储** | 语义搜索 | 高 |
| **键值存储** | 精确查找 | 低 |
| **混合存储** | 混合检索 | 高 |

## Things to Remember

- Memory 是跨会话的持久化存储
- Session 是单会话的消息历史
- 向量存储适合语义检索
- Memory 加载在会话开始时，保存在会话结束时
