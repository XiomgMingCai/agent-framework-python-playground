# Copyright (c) Microsoft. All rights reserved.
# Structured Output - 结构化输出

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
    load_dotenv()

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

    print("=" * 60)
    print("  Structured Output Demo - 结构化输出")
    print("=" * 60)

    # 提取城市信息
    print("\n--- 示例 1: 城市信息提取 ---")
    response = await agent.run("北京是中国的首都，人口约2200万，是一座历史悠久的现代化城市。")
    city_info = parse_structured_response(response.text, CityInfo)
    if city_info:
        print(f"城市: {city_info.city}")
        print(f"国家: {city_info.country}")
        print(f"人口: {city_info.population}")
        print(f"描述: {city_info.description}")

    # 提取人物信息
    print("\n--- 示例 2: 人物信息提取 ---")
    response = await agent.run("张伟是一名35岁的软件工程师，在北京工作。")
    person_info = parse_structured_response(response.text, PersonInfo)
    if person_info:
        print(f"姓名: {person_info.name}")
        print(f"年龄: {person_info.age}")
        print(f"职业: {person_info.occupation}")


if __name__ == "__main__":
    asyncio.run(main())
