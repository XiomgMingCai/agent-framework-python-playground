# Item 7: Handle Markdown-Wrapped JSON from LLMs

LLM 返回结构化数据时，喜欢用 markdown 包裹 JSON。你的解析代码需要处理这个。

## 问题

你让 Agent 返回纯 JSON，但它会这样：

````
```json
{"name": "李明", "age": 25}
```
````

直接 `model_validate_json()` 会失败。

## 解决方案

用正则提取：

```python
def parse_json(text: str, model_cls: type[BaseModel]) -> BaseModel | None:
    # 先尝试提取 markdown 包裹的 JSON
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text.strip())

    json_str = match.group(1) if match else text

    try:
        return model_cls.model_validate_json(json_str.strip())
    except Exception:
        return None
```

## 完整示例

```python
class Person(BaseModel):
    name: str
    age: int
    occupation: str

response = await agent.run("李明是一名25岁的软件工程师")
person = parse_json(response.text, Person)
if person:
    print(f"{person.name}, {person.age}岁, {person.occupation}")
```

## Things to Remember

- LLM 喜欢用 ```json ... ``` 包裹 JSON，需要正则提取
- `model_validate_json()` 解析 JSON 为 Pydantic 模型
- instructions 中强调"只输出 JSON，不要其他文字"可以减少 markdown 包裹
- `response_format` 参数可以指定输出格式，但兼容性不稳定
