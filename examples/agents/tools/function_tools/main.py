# Copyright (c) Microsoft. All rights reserved.
# Function Tools - 函数工具

import asyncio
import os
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from agent_framework import Agent, tool
from agent_framework.openai import OpenAIChatCompletionClient


@tool
def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """
    获取指定时区的当前时间。

    Args:
        timezone: 时区名称，例如 Asia/Shanghai、UTC、America/New_York

    Returns:
        格式化的当前时间字符串
    """
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.strftime(f"%Y-%m-%d %H:%M:%S ({timezone})")
    except Exception as e:
        return f"错误：无效的时区 '{timezone}'，原因：{e}"


@tool
def calculate(expression: str) -> str:
    """
    计算数学表达式。

    Args:
        expression: 数学表达式字符串，例如 "2 + 3 * 4"

    Returns:
        计算结果字符串
    """
    import re
    if not re.match(r'^[\d\s\+\-\*\/\.\(\)]+$', expression):
        return f"错误：表达式包含非法字符：{expression}"
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算失败：{e}"


@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息（模拟数据）。

    Args:
        city: 城市名称，例如 北京、上海、Tokyo

    Returns:
        天气信息字符串
    """
    mock_data = {
        "北京": "晴，18°C，东风 3 级，湿度 40%",
        "上海": "多云，22°C，东南风 2 级，湿度 65%",
        "广州": "阵雨，26°C，南风 4 级，湿度 80%",
        "东京": "Cloudy, 20°C, NE wind, Humidity 55%",
    }
    return mock_data.get(city, f"{city}：暂无天气数据")


async def main(prompt: str):
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
        name="ToolAgent",
        instructions=(
            "你是一个实用助手，拥有以下工具：\n"
            "- get_current_time：查询时区时间\n"
            "- calculate：计算数学表达式\n"
            "- get_weather：查询城市天气\n"
            "根据用户问题自动选择合适的工具。"
        ),
        tools=[get_current_time, calculate, get_weather],
    )

    print(f"User : {prompt}")
    print("Agent: ", end="", flush=True)

    stream = await agent.run(prompt, stream=True)

    async for update in stream:
        if update.contents:
            for content in update.contents:
                if content.text:
                    print(content.text, end="", flush=True)

    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", type=str, required=True)
    args = parser.parse_args()
    asyncio.run(main(args.prompt))
