# Structured Output

让 Agent 生成结构化输出（JSON），而非自由文本。

## 前置知识

- 已完成[基础对话](basic.md)
- 了解 Pydantic 模型基础

## 核心概念

```
User: "北京是中国的首都..."
         ↓
   Agent (Structured Output)
         ↓
   提取信息 → 生成 JSON
         ↓
   Pydantic Model 解析
         ↓
   结构化数据: {city: "北京", country: "中国", ...}
```

## 示例代码

**文件：** `examples/structured_output/main.py`

```python
import asyncio
import os
import re
from pydantic import BaseModel
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient


class CityInfo(BaseModel):
    """城市信息结构"""
    city: str
    country: str
    population: str
    description: str


class PersonInfo(BaseModel):
    """人物信息结构"""
    name: str
    age: int
    occupation: str


def parse_structured_response(text: str, model_cls: type[BaseModel]) -> BaseModel | None:
    """解析 JSON 响应，处理 markdown 包裹情况"""
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text.strip())
    if match:
        cleaned = match.group(1).strip()
        try:
            return model_cls.model_validate_json(cleaned)
        except Exception:
            pass
    try:
        return model_cls.model_validate_json(text)
    except Exception:
        return None


async def main():
    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    agent = Agent(
        client=client,
        name="StructuredAgent",
        instructions=(
            "你是一个信息提取助手。请根据用户输入提取信息，并以纯 JSON 格式返回，"
            "格式如：{\"city\": \"城市名\", \"country\": \"国家\", \"population\": \"人口\", \"description\": \"描述\"}。"
            "只输出 JSON，不要其他文字。"
        ),
    )

    # 提取城市信息
    response = await agent.run("北京是中国的首都，人口约2200万...")
    city_info = parse_structured_response(response.text, CityInfo)
    if city_info:
        print(f"城市: {city_info.city}")
        print(f"国家: {city_info.country}")
        print(f"人口: {city_info.population}")
        print(f"描述: {city_info.description}")
```

## 运行

```bash
uv run examples/structured_output/main.py
```

## 输出示例

```
============================================================
  Structured Output Demo - 结构化输出
============================================================

--- 示例 1: 城市信息提取 ---
输入: 北京是中国的首都，人口约2200万，是一座历史悠久的现代化城市。
城市: 北京
国家: 中国
人口: 2200万
描述: 历史悠久的现代化城市

--- 示例 2: 人物信息提取 ---
输入: 张伟是一名35岁的软件工程师，在北京工作。
姓名: 张伟
年龄: 35
职业: 软件工程师
```

## 核心要点

| 组件 | 说明 |
|------|------|
| `BaseModel` | Pydantic 基类，定义数据结构 |
| `model_validate_json()` | 从 JSON 字符串验证并解析为模型实例 |
| `response_format` | `agent.run()` 的 options 参数，指定结构化输出格式 |
| Markdown 处理 | LLM 可能返回 markdown 包裹的 JSON，需预处理 |

## Pydantic 模型定义

```python
from pydantic import BaseModel

class CityInfo(BaseModel):
    """城市信息"""
    city: str           # 城市名
    country: str        # 国家
    population: str     # 人口
    description: str    # 描述
```

## 使用 response_format 参数

```python
from pydantic import BaseModel

class PersonInfo(BaseModel):
    name: str
    age: int
    occupation: str

# 通过 response_format 指定输出格式
response = await agent.run(
    "张伟是一名35岁的工程师",
    options={"response_format": PersonInfo}
)

# response.value 直接返回 Pydantic 模型实例
person: PersonInfo = response.value
print(f"姓名: {person.name}, 年龄: {person.age}")
```

!!! note "提示"
    部分模型对 `response_format` 支持不完善，可能返回 markdown 包裹的 JSON，此时需手动处理。
