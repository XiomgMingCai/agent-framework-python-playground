# Item 6: Handle Structured Output from LLMs Correctly

## 问题

你要求 Agent 返回结构化数据（JSON），但它返回的是：

```python
# 你写的代码
result = await agent.run("返回一个用户的姓名和年龄： 李明 25岁")
print(result.text)
# 输出：
# ```json
# {"name": "李明", "age": 25}
# ```
```

然后你尝试解析：

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

# 错误：直接解析会失败
person = Person.model_validate_json(result.text)
# ValidationError: Invalid JSON...
```

LLM 喜欢用 Markdown 包裹 JSON，但你的解析代码假设是裸 JSON。

## 深入解释

LLM 生成文本时，Markdown 格式是"自然"输出——它训练时见过大量代码文档，自然倾向于用 triple-backticks 包裹代码块。这不是 bug，而是 LLM 的默认行为。

**常见变形**：

```python
# 变形 1：带语言标识
"""json
{"name": "李明"}
"""

# 变形 2：不带语言标识
```
{"name": "李明"}
```

# 变形 3：带额外文字
Here is the JSON:
```json
{"name": "李明"}
```

# 变形 4：嵌套在其他内容中
Sure! Here is the information:
```json
{"name": "李明", "age": 25}
```

# 变形 5：尾部有说明
```json
{"name": "李明", "age": 25}
```
```

## 推荐做法

### 方法一：Instructions 约束（推荐）

在 Instructions 中明确要求"只输出 JSON，不要其他内容"：

```python
agent = Agent(
    client=client,
    name="DataAgent",
    instructions="""
    你是一个数据返回助手。你的职责是根据用户请求返回精确的 JSON 数据。

    重要规则：
    1. 只输出纯 JSON，不要任何 Markdown 包裹
    2. 不要输出解释、说明或其他文字
    3. 确保 JSON 格式正确，可以被 json.loads() 解析
    """
)
```

### 方法二：代码层面处理 Markdown 包裹

```python
import re
import json
from pydantic import BaseModel

def parse_json_response(text: str) -> dict | None:
    """
    从 LLM 输出中提取 JSON。
    处理多种包裹形式：```json ... ```、``` ... ```、裸 JSON
    """
    # 尝试提取任何 Markdown 包裹的 JSON
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    matches = re.findall(pattern, text.strip())

    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue

    # 尝试直接解析裸 JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None

# 使用
result = await agent.run("返回一个用户的姓名和年龄")
data = parse_json_response(result.text)
if data:
    person = Person.model_validate(data)
    print(f"{person.name}, {person.age}岁")
```

### 方法三：使用 response_format 参数（兼容性不稳定）

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

# 有些 Client 支持 response_format
result = await agent.run(
    "返回一个用户的姓名和年龄",
    options={"response_format": Person}  # 可能不支持
)
if hasattr(result, 'value'):
    person = result.value  # 直接获得 Pydantic 对象
```

## 好 vs 坏对比

```python
# 坏做法：假设 LLM 返回裸 JSON
result = await agent.run("返回用户信息")
person = Person.model_validate_json(result.text)  # 几乎必定失败

# 好做法 1：Instructions 约束输出格式
agent = Agent(
    client=client,
    instructions="只输出纯 JSON，不要 Markdown 包裹，不要其他文字。"
)
result = await agent.run("返回用户信息")
person = Person.model_validate_json(result.text)  # 大概率成功

# 好做法 2：代码层面容错
result = await agent.run("返回用户信息")
data = parse_json_response(result.text)  # 处理各种变形
if data:
    person = Person.model_validate(data)
```

## 扩展讨论

### 边缘情况处理

```python
def robust_json_parse(text: str, model_cls: type[BaseModel] | None = None) -> BaseModel | dict | None:
    """更健壮的 JSON 解析"""
    # 1. 提取所有可能的 JSON 块
    patterns = [
        r'```json\s*([\s\S]*?)\s*```',      # ```json ...
        r'```\s*([\s\S]*?)\s*```',           # ``` ...
        r'\{[\s\S]*\}',                       # 裸 JSON（最后兜底）
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                data = json.loads(match.strip())
                if model_cls:
                    return model_cls.model_validate(data)
                return data
            except (json.JSONDecodeError, Exception):
                continue

    return None
```

### 性能考虑

- 额外的正则解析开销极小（微秒级），不必担心
- 但 Instructions 约束输出格式更优雅，能减少 token 消耗（少了 Markdown 包裹）

### 结构化输出的企业级实践

```python
# 1. 定义清晰的 Schema
class ApiResponse(BaseModel):
    success: bool
    data: dict | None = None
    error: str | None = None

# 2. Instructions 中强调 Schema 约束
instructions = """
返回格式必须严格遵循：
{
    "success": true/false,
    "data": {...} | null,
    "error": "错误信息" | null
}
"""

# 3. 验证失败时重试
def fetch_structured(agent, prompt, model_cls, max_retries=3):
    for i in range(max_retries):
        result = await agent.run(prompt)
        try:
            return model_cls.model_validate_json(result.text)
        except Exception:
            if i == max_retries - 1:
                raise ValueError(f"Failed after {max_retries} retries")
    return None
```

## Things to Remember

- LLM 倾向于用 Markdown 包裹 JSON（` ```json ... ``` `），直接解析会失败
- **首选方案**：在 Instructions 中明确约束"只输出纯 JSON，不要 Markdown"，从源头解决问题
- **备选方案**：代码层面用正则 `r"```(?:json)?\s*([\s\S]*?)\s*```"` 提取
- `response_format` 参数兼容性不稳定，生产环境不建议依赖
- 结构化输出应该定义清晰的 Pydantic Schema，并通过 Instructions 强调格式约束
- 验证失败时应设计重试机制，而不是假设每次都成功
- 解析 JSON 前先 `.strip()` 去除空白，能减少奇怪的解析失败
