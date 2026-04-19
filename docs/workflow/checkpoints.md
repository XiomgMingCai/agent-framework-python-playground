# Checkpoints & Resuming

## Item 19: Save Checkpoints Before Long Operations, Restore After Failures

长时间运行的工作流应该保存检查点，失败后从检查点恢复而不是从头开始。

## 两种存储后端

```python
# 内存存储（测试用，重启丢失）
from agent_framework import InMemoryCheckpointStorage
storage = InMemoryCheckpointStorage()

# 文件存储（生产用）
from agent_framework import FileCheckpointStorage
storage = FileCheckpointStorage(storage_path="./checkpoints")
```

## 保存和恢复

```python
# 1. 运行前保存检查点
checkpoint = await storage.save(workflow_id, workflow_state)

# 2. 模拟崩溃
del workflow

# 3. 从检查点恢复
restored = await storage.restore(checkpoint)

# 4. 继续执行
result = await restored.run(continued_input)
```

## 检查点内容

| 字段 | 说明 |
|------|------|
| `workflow_id` | 工作流标识 |
| `messages` | 消息历史 |
| `state` | 状态快照 |
| `pending_requests` | 待处理请求 |
| `iteration_count` | 迭代次数 |

## Things to Remember

- **InMemory**：测试用，重启后丢失
- **FileCheckpointStorage**：生产用，参数是 `storage_path=`
- **save()** 返回检查点对象，用其恢复
- **restore()** 用检查点对象恢复工作流状态
- **断点续传**：崩溃 → 恢复 → 继续执行
