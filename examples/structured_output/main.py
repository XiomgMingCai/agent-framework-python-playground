# Copyright (c) Microsoft. All rights reserved.
# Structured Output - 使用 Pydantic 模型生成结构化输出

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
    # 去除 markdown 代码块包裹的 JSON
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text.strip())
    if match:
        cleaned = match.group(1).strip()
        try:
            return model_cls.model_validate_json(cleaned)
        except Exception:
            pass
    # 尝试直接解析
    try:
        return model_cls.model_validate_json(text)
    except Exception:
        return None


async def main():
    load_dotenv()

    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model = os.getenv("AI_MODEL")

    if not all([api_key, base_url, model]):
        raise ValueError("请在 .env 中配置 AI_API_KEY、AI_BASE_URL、AI_MODEL")

    client = OpenAIChatCompletionClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
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

    print("=" * 60)
    print("  Structured Output Demo - 结构化输出")
    print("=" * 60)

    # 示例 1: 提取城市信息
    print("\n--- 示例 1: 城市信息提取 ---")
    query1 = "北京是中国的首都，人口约 2200万，是一座历史悠久的现代化城市。"
    print(f"输入: {query1}")

    response1 = await agent.run(query1)
    if response1.text:
        city_info = parse_structured_response(response1.text, CityInfo)
        if city_info:
            print(f"城市: {city_info.city}")
            print(f"国家: {city_info.country}")
            print(f"人口: {city_info.population}")
            print(f"描述: {city_info.description}")
        else:
            print(f"原始响应: {response1.text}")

    # 示例 2: 提取人物信息
    print("\n--- 示例 2: 人物信息提取 ---")
    query2 = "张伟是一名35岁的软件工程师，在北京工作。"
    print(f"输入: {query2}")

    # 调整指令以匹配 PersonInfo 格式
    agent2 = Agent(
        client=client,
        name="StructuredAgent2",
        instructions=(
            "你是一个信息提取助手。请根据用户输入提取信息，并以纯 JSON 格式返回，"
            "格式如：{\"name\": \"姓名\", \"age\": 年龄, \"occupation\": \"职业\"}。"
            "age必须是整数。只输出JSON，不要其他文字。"
        ),
    )

    response2 = await agent2.run(query2)
    if response2.text:
        person_info = parse_structured_response(response2.text, PersonInfo)
        if person_info:
            print(f"姓名: {person_info.name}")
            print(f"年龄: {person_info.age}")
            print(f"职业: {person_info.occupation}")
        else:
            print(f"原始响应: {response2.text}")


if __name__ == "__main__":
    asyncio.run(main())
