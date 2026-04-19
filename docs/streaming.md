# Item 2: Use Streaming for Real-Time Response

当用户请求长文本或需要实时反馈时，不要让用户等待完整结果。使用流式输出，让 AI 的思考过程可见。

## 问题

非流式调用的问题：

```python
# 用户要等待完整响应才能看到任何输出
result = await agent.run("写一篇关于AI的文章")
print(result.text)  # 干等 30 秒，然后一次性输出
```

如果生成需要 30 秒，用户会以为程序卡死了。

## 解决方案

用 `stream=True` 启用流式输出：

```python
stream = await agent.run(prompt, stream=True)

print("Agent: ", end="", flush=True)
async for update in stream:
    if update.contents:
        for content in update.contents:
            if content.text:
                print(content.text, end="", flush=True)

await stream.get_final_response()  # 必须调用
```

## 关键细节

- **flush=True**：立即输出，不等缓冲区
- **get_final_response()**：必须调用，否则资源泄漏
- **update.contents**：内容在列表里，需要遍历取 text

## Things to Remember

- `stream=True` 返回 ResponseStream，不是普通字符串
- `async for update in stream` 遍历每个 chunk
- `update.contents[i].text` 取文本内容
- 必须调用 `get_final_response()` 获取完整响应
