# Item 30: Build Multimodal Agents That Handle Multiple Data Types

## 问题

你想让 Agent 处理图像，但不知道怎么做：

```python
# 你想分析用户上传的图片
result = await agent.run("描述这张图片")  # 图片在哪里？

# 实际上 Agent 只能处理文本
# 你需要告诉 Agent 图片在哪里
```

或者你尝试传图片，但格式不对：

```python
# 错误：图片 URL 直接写在文本里
result = await agent.run("描述这张图片: https://example.com/image.jpg")

# 可能工作了，但不够规范
```

## 深入解释

**多模态 = 能处理多种数据类型**（文本、图像、音频、视频），而不是只能处理文本：

```
┌─────────────────────────────────────────────────────────────┐
│              单模态 Agent（Text Only）                       │
├─────────────────────────────────────────────────────────────┤
│  输入：文本                                                 │
│  输出：文本                                                 │
│  能力：只能处理文字                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              多模态 Agent（Multimodal）                      │
├─────────────────────────────────────────────────────────────┤
│  输入：文本 + 图像 + 音频 + 视频...                        │
│  输出：文本 + 图像 + 音频 + 视频...                        │
│  能力：处理任意组合的数据类型                               │
└─────────────────────────────────────────────────────────────┘
```

**心智模型**：多模态 Agent 就像一个能看、能听、能说的助手，而不只是能读的助手。

## 推荐做法

### 图像输入（URL）

```python
from agent_framework import Agent

agent = Agent(
    client=client,
    instructions="你是一个视觉助手，可以分析图像内容并回答相关问题。",
)

# 使用 Content 组合多种输入
from agent_framework import Message

message = Message(
    role="user",
    contents=[
        {"type": "text", "text": "描述这张图片的内容"},
        {"type": "image_url", "url": "https://example.com/sample.jpg"},
    ]
)

result = await agent.run(messages=[message])
print(result.text)
```

### 图像输入（Base64）

```python
import base64

# 读取本地图片并转为 base64
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

message = Message(
    role="user",
    contents=[
        {"type": "text", "text": "这张图片里有什么？"},
        {
            "type": "image_url",
            "url": f"data:image/jpeg;base64,{image_data}"
        },
    ]
)

result = await agent.run(messages=[message])
```

### 多模态消息组合

```python
message = Message(
    role="user",
    contents=[
        {"type": "text", "text": "对比这两张图片的差异"},
        {"type": "image_url", "url": "https://example.com/image1.jpg"},
        {"type": "image_url", "url": "https://example.com/image2.jpg"},
    ]
)

result = await agent.run(messages=[message])
```

### 多模态输出处理

```python
result = await agent.run("生成一张代码流程图并解释它")

# 处理不同类型的输出
if hasattr(result, 'contents'):
    for content in result.contents:
        if content.type == "text" and content.text:
            print(f"文本输出: {content.text}")
        elif content.type == "image" and content.data:
            save_image(content.data)
        elif content.type == "audio" and content.data:
            play_audio(content.data)
```

## 好 vs 坏对比

```python
# 坏做法 1：图片 URL 写在纯文本里
result = await agent.run("描述图片 https://example.com/image.jpg 的内容")
# 可能工作，但不规范，Agent 可能只当 URL 是普通文本

# 好做法：用结构化的 image_url content
message = Message(role="user", contents=[
    {"type": "text", "text": "描述这张图片"},
    {"type": "image_url", "url": "https://example.com/image.jpg"},
])
result = await agent.run(messages=[message])

# 坏做法 2：假设所有模型都支持多模态
agent = Agent(client=client)  # 假设 client 支持图像
result = await agent.run(messages=[...with image...])
# 如果模型不支持，图像会被忽略或报错

# 好做法：先检查模型能力
if client.supports_vision():
    result = await agent.run(messages=[...with image...])
else:
    result = await agent.run("请描述图片中的内容（图片 URL: ...）")
```

## 扩展讨论

### 模态转换场景

| 输入 | 输出 | 场景 |
|------|------|------|
| 文本 | 图像 | 图像生成（DALL-E、Midjourney）|
| 图像 | 文本 | 图像描述、OCR、视觉问答 |
| 音频 | 文本 | 语音转文字（Whisper）|
| 文本 | 音频 | 文字转语音（TTS）|
| 图像 + 文本 | 文本 | 视觉问答（VQA）|
| 文档（PDF）| 文本 | 文档理解、信息提取 |

### 多模态 Client 配置

```python
# 确保 Client 支持多模态
client = OpenAIChatCompletionClient(
    api_key=os.getenv("AI_API_KEY"),
    base_url=os.getenv("AI_BASE_URL"),
    model="gpt-4o",  # 支持视觉的模型
)

# 检查能力
if not client.supports_vision():
    raise ValueError("当前模型不支持图像输入")
```

### 图像处理优化

```python
# 压缩大图像（减少 token 消耗）
from PIL import Image
import io

def compress_image(image_path: str, max_size: int = 1024) -> bytes:
    img = Image.open(image_path)

    # 等比缩放
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    # 转为 JPEG
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()

# 使用压缩后的图像
image_data = compress_image("large_image.jpg")
image_b64 = base64.b64encode(image_data).decode()
```

### 企业级考虑

```python
# 1. 图像缓存
class CachedImageProvider:
    def __init__(self, cache_dir: str = ".image_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache = {}

    def get_cached(self, url: str) -> bytes | None:
        if url in self.cache:
            return self.cache[url]

        cache_path = self.cache_dir / hashlib.md5(url.encode()).hexdigest()
        if cache_path.exists():
            data = cache_path.read_bytes()
            self.cache[url] = data
            return data
        return None

# 2. 多模态内容验证
class MultimodalValidator:
    def validate_message(self, message: Message) -> bool:
        for content in message.contents:
            if content.type == "image_url":
                if not self._is_valid_url(content.url):
                    return False
                if not self._is_supported_format(content.url):
                    return False
        return True
```

## Things to Remember

- **多模态 = 处理多种数据类型**（文本、图像、音频、视频）
- 图像输入用 `{"type": "image_url", "url": "..."}` 结构，而非纯文本
- `Message.contents` 列表可以组合多种数据类型
- **并非所有模型都支持多模态**——使用前检查 `client.supports_vision()`
- 多模态 Agent 输出的内容类型也可能是多种，需要按 `content.type` 分别处理
- 大图像需要压缩以减少 token 消耗
- Base64 图像适用于本地图片，URL 适用于网络图片
