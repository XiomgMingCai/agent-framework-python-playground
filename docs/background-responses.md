# Item 8: Use asyncio.create_task() for Background Tasks

`background=True` 是 OpenAI Responses API 的专属功能，Chat Completions API 不支持。用 asyncio 模拟后台任务。

## 问题

以为可以用官方后台任务：

```python
# OpenAIChatCompletionClient 不支持
stream = await agent.run(prompt, background=True)  # 不会生效
```

## 解决方案

用 asyncio 模拟：

```python
async def run_in_background(agent, query, session):
    return asyncio.create_task(agent.run(query, session=session))

# 启动后台任务
task = await run_in_background(agent, query, session)

# 主线程继续工作
print("处理其他事情...")
await asyncio.sleep(1)

# 等待完成
while not task.done():
    await asyncio.sleep(1)

# 获取结果
response = task.result()
```

## 断点续传：用 Session 保持上下文

```python
# 模拟网络中断
stream = agent.run(query, stream=True, session=session)
async for update in stream:
    if update.text:
        print(update.text, end="")
    if some_condition:  # 中断条件
        break

# Session 保持上下文，可以继续生成
stream2 = agent.run(query, stream=True, session=session)
async for update in stream2:
    ...
```

## Things to Remember

- `background=True` 是 Responses API 专属，Chat Completions API 不支持
- `asyncio.create_task()` 将协程放入后台
- `task.done()` 检查是否完成，`task.result()` 获取返回值
- Session 上下文保持，支持模拟断点续传
