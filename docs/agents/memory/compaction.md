# Item 21: Use Compaction to Prevent Memory Bloat

随着对话增加，Memory 会不断膨胀。Compaction（压缩）机制将历史信息压缩为摘要，保留关键信息同时控制存储增长。

## 压缩心智模型

```
原始消息 → 压缩提取 → 摘要 → 替换原始
```

## 触发条件

| 策略 | 说明 | 阈值 |
|------|------|------|
| **消息数量** | 超过 N 条消息 | 100 条 |
| **Token 数量** | 超过 N tokens | 4096 tokens |
| **时间窗口** | 超过 N 时间 | 24 小时 |

## 实现压缩

```python
from agent_framework.memory import Memory, CompactionStrategy

class SemanticCompaction(CompactionStrategy):
    """语义压缩：提取关键信息生成摘要"""
    async def compact(self, messages: list[Message]) -> Message:
        summary = await llm.summarize(messages)
        return Message(
            role="system",
            content=f"对话摘要: {summary}"
        )

memory = Memory(
    storage=VectorStorage(),
    compaction=SemanticCompaction(),
    compaction_threshold=100,  # 100 条消息后压缩
)
```

## 压缩时机

```python
memory = Memory(
    compaction=SemanticCompaction(),
    # 压缩时机
    compact_on_threshold=True,    # 达到阈值时
    compact_on_session_end=True,  # 会话结束时
    compact_on_idle=True,        # 空闲时定期
)
```

## Things to Remember

- Compaction 防止 Memory 无限增长
- 压缩后保留语义，丢弃细节
- 合理设置触发阈值
- 压缩是异步后台操作，不阻塞主流程
