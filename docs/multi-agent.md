# Item 11: Share Sessions to Share Context Between Agents

多个 Agent 协作时，用同一个 Session 让它们自动共享上下文。

## 问题

分别调用各个 Agent，上下文断了：

```python
translator = Agent(client=client, name="Translator", ...)
summarizer = Agent(client=client, name="Summarizer", ...)

# 上下文不共享
result1 = await translator.run("你好")
result2 = await summarizer.run("总结一下")  # 不知道翻译说了什么
```

## 解决方案

用同一个 Session：

```python
# 创建一个 Session 给所有 Agent 共享
session = router.create_session()

# 翻译
trans_result = await translator.run("月光下的宁静湖面", session=session)

# 总结（能看到翻译的内容）
summary_result = await summarizer.run(
    f"基于翻译结果：{trans_result.text}，进行情感总结",
    session=session
)
```

## 协作模式

| 模式 | 说明 |
|------|------|
| Router + Workers | 调度 Agent 分析请求，分配给专业 Worker |
| Sequential | 多个 Agent 顺序执行，上一个输出作为下一个输入 |
| Parallel | 多个 Agent 并行处理不同部分 |

## Things to Remember

- Session 是 Agent 间的上下文纽带，用 `agent.create_session()` 创建
- 共享 Session 时，所有 Agent 的消息历史自动累积
- 一个 Agent 的输出可以作为另一个 Agent 的输入
- Router Agent 分析请求，决定调用哪个 Worker
