# Item 12: Put Message Content in TaskStatusUpdateEvent.status.message

A2A 流式响应的关键是：消息内容必须放在 `TaskStatusUpdateEvent.status.message` 中，而不是单独的消息对象。

## 问题

以为可以这样发消息：

```python
# 错误：内容没有放在 status.message 里
yield TaskStatusUpdateEvent(
    task_id=task_id,
    state=TaskState.working,
    message=Message(...)  # 放在这里
)
```

客户端可能收不到消息内容。

## 正确做法

消息内容必须放在 status.message 中：

```python
status_message = Message(
    message_id=str(uuid.uuid4()),
    role=Role.agent,
    parts=[TextPart(kind="text", text=full_text)],
)
status_update = TaskStatusUpdateEvent(
    task_id=task_id,
    final=False,
    status=TaskStatus(
        state=TaskState.working,
        message=status_message  # 必须在这里
    ),
)
yield f"data: {json.dumps(...)}\n\n"
```

## SSE 事件顺序

```
1. Task (state=working)           → 建立任务，获取 task_id
2. TaskStatusUpdateEvent           → 状态更新，消息在 status.message 中
3. TaskStatusUpdateEvent (final)   → 最终状态 (state=completed)
```

## Things to Remember

- `TaskStatusUpdateEvent.status.message` 是消息内容的容器
- SSE 事件用 JSON-RPC 2.0 格式：`{"jsonrpc": "2.0", "id": ..., "result": {...}}`
- `AgentCard` 是 Agent 的元数据，用于发现和描述能力
- `TaskState` 状态机：working → completed/failed
- `A2AAgent` 客户端通过 agent_card 发现远程 Agent
