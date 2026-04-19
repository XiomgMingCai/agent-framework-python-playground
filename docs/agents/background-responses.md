# Item 7: Use Background Tasks for Long-Running Operations

## 问题

你有一段耗时很长的 Agent 任务（比如分析大量数据），但不想让用户一直等待：

```python
# 问题：用户要等 60 秒才能看到任何输出
result = await agent.run("分析这 1000 条用户日志，找出异常模式")
print(result.text)  # 干等...
```

或者你尝试用 `background=True`，但没有任何效果：

```python
# 错误：OpenAIChatCompletionClient 不支持 background=True
stream = await agent.run("分析这 1000 条日志", background=True)
# 没有效果，任务仍然同步执行
```

## 深入解释

**`background=True` 是 Responses API 的专属功能**。如果你使用的是 `OpenAIChatCompletionClient`（基于 Chat Completions API），这个参数会被忽略。

```
┌─────────────────────────────────────────────────────┐
│           OpenAI Responses API vs Chat API           │
├─────────────────────────────────────────────────────┤
│  Responses API (OpenAIChatClient)                    │
│  • 支持 background=True                              │
│  • 原生后台任务                                      │
│  • 但 SiliconFlow/DeepSeek 等不支持                 │
├─────────────────────────────────────────────────────┤
│  Chat Completions API (OpenAIChatCompletionClient)   │
│  • 不支持 background=True（参数被忽略）              │
│  • 兼容性好（SiliconFlow、DeepSeek 等都支持）        │
│  • 需要用 asyncio 模拟后台任务                       │
└─────────────────────────────────────────────────────┘
```

当你需要兼容多个 API 服务商时，必须用 `asyncio.create_task()` 模拟后台任务。

## 推荐做法

### 方法一：asyncio.create_task() 模拟后台任务

```python
import asyncio

async def run_in_background(agent, query: str):
    """后台运行 agent 任务"""
    return await agent.run(query)

async def main():
    # 启动后台任务
    task = asyncio.create_task(run_in_background(agent, "分析这 1000 条日志"))

    # 主线程继续工作
    print("正在启动分析任务...")
    do_other_work()

    # 等待任务完成
    while not task.done():
        await asyncio.sleep(1)
        print("分析进行中...")

    # 获取结果
    result = task.result()
    print(f"分析完成：{result.text[:100]}...")

asyncio.run(main())
```

### 方法二：带进度回调的后台任务

```python
import asyncio

async def run_with_progress(agent, query: str, progress_callback=None):
    """带进度回调的后台任务"""
    stream = await agent.run(query, stream=True)
    full_response = ""

    async for update in stream:
        if update.contents:
            for content in update.contents:
                if content.text:
                    full_response += content.text
                    if progress_callback:
                        progress_callback(full_response)

    return full_response

# 使用
async def main():
    def show_progress(text):
        print(f"\r进度：{len(text)} 字符", end="", flush=True)

    task = asyncio.create_task(run_with_progress(agent, "长文本分析", show_progress))
    await do_other_work()
    result = await task
    print(f"\n完成：{result[:50]}...")
```

### 方法三：Session + 断点续传

当后台任务可能中断时（如网络断开），使用 Session 保持上下文：

```python
from agent_framework import AgentSession

async def resumable_task(agent, query: str):
    """支持断点续传的任务"""
    session = AgentSession()

    # 第一阶段：生成前一部分
    stream1 = await agent.run(query, stream=True, session=session)
    partial = ""
    async for update in stream1:
        if update.contents:
            for content in update.contents:
                if content.text:
                    partial += content.text

    # 模拟中断：用户断开连接

    # 第二阶段：从断点继续
    stream2 = await agent.run(
        f"继续分析：{partial}",
        stream=True,
        session=session  # Session 保持完整上下文
    )

    final = ""
    async for update in stream2:
        if update.contents:
            for content in update.contents:
                if content.text:
                    final += content.text

    return final
```

## 好 vs 坏对比

```python
# 坏做法 1：假设 background=True 有效果
stream = await agent.run(query, background=True)  # 在 Chat API 上无效
print(stream)  # 没有后台执行

# 坏做法 2：同步等待长任务，阻塞主线程
result = await agent.run("分析 10000 条日志")  # 用户等待 60 秒无反馈
print(result.text)

# 好做法：用 asyncio.create_task() 后台执行
task = asyncio.create_task(agent.run(query))
print("任务启动，主线程继续...")  # 用户立刻看到反馈
await do_other_work()
result = await task
```

## 扩展讨论

### 官方 vs 模拟后台任务对比

| 特性 | Responses API (官方) | asyncio.create_task (模拟) |
|------|---------------------|---------------------------|
| API 要求 | OpenAI 官方 API | 任意 Chat Completions 兼容 API |
| 状态保持 | 原生 continuation_token | 需要 Session |
| 断点续传 | 原生支持 | 需手动管理 Session |
| 超时处理 | 框架内置 | 需手动实现 |
| 兼容性 | 仅 OpenAI | 所有兼容 API |

### 超时处理

```python
async def timed_task(agent, query: str, timeout: float = 30.0):
    """带超时控制的后台任务"""
    task = asyncio.create_task(agent.run(query))

    try:
        result = await asyncio.wait_for(task, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        task.cancel()
        return {"error": "任务超时"}
```

### 企业级考虑

```python
# 1. 任务队列化
async def task_queue_example():
    from asyncio import Queue

    task_queue = Queue()

    async def worker(agent):
        while True:
            query = await task_queue.get()
            result = await agent.run(query)
            print(f"完成：{query[:30]}...")
            task_queue.task_done()

    # 启动多个 worker
    workers = [asyncio.create_task(worker(agent)) for _ in range(3)]

    # 入队任务
    queries = [f"分析任务 {i}" for i in range(10)]
    for q in queries:
        await task_queue.put(q)

    await task_queue.join()
    for w in workers:
        w.cancel()

# 2. 任务状态持久化（断电恢复）
import json
from pathlib import Path

async def persistent_task(agent, query: str, state_file: Path):
    """任务状态持久化，支持断电恢复"""
    if state_file.exists():
        state = json.loads(state_file.read_text())
        session = AgentSession.from_state(state)
    else:
        session = AgentSession()

    stream = await agent.run(query, stream=True, session=session)

    # 定期保存状态
    async for update in stream:
        if should_checkpoint():
            state_file.write_text(json.dumps(session.to_state()))

    return stream
```

## Things to Remember

- `background=True` 是 **Responses API 专属**，在 `OpenAIChatCompletionClient` 上无效
- 如果需要兼容多个 API 服务商，用 `asyncio.create_task()` 模拟后台任务
- `asyncio.create_task()` 将协程放入事件循环后台，不阻塞主线程
- `task.done()` 检查任务状态，`task.result()` 获取返回值（需先 done()）
- 长任务配合 Session 可以实现断点续传，Session 保持完整上下文
- 生产环境中任务应设计超时控制，避免无限等待
- 后台任务的结果获取要放在 try/except 中，任务可能抛出异常
- 多个后台任务可以用 `asyncio.gather()` 并行执行
