# Copyright (c) Microsoft. All rights reserved.
# Declarative Agents - YAML 配置加载

import asyncio
import os
import yaml

from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient


# YAML 配置文件
AGENT_CONFIG = """
name: yaml-agent
description: 一个通过 YAML 配置的助手

instructions: |
  你是一个乐于助人的助手。
  当用户问候时，友好回应。

tools:
  - name: get_time
    description: 获取当前时间
    function: get_current_time
  - name: calculate
    description: 计算数学表达式
    function: calculate
"""


def get_current_time():
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


class DeclarativeAgent:
    """声明式 Agent 加载器"""

    def __init__(self, config_path: str = None, config_text: str = None):
        if config_path:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        elif config_text:
            self.config = yaml.safe_load(config_text)
        else:
            raise ValueError("需要提供 config_path 或 config_text")

        self.name = self.config["name"]
        self.instructions = self.config["instructions"]
        self.description = self.config.get("description", "")
        self.tools = self._load_tools()

    def _load_tools(self):
        """加载工具"""
        from agent_framework import tool
        tools = []
        for tool_config in self.config.get("tools", []):
            func_name = tool_config["function"]
            if func_name == "get_current_time":
                tools.append(tool(get_current_time))
            elif func_name == "calculate":
                tools.append(tool(calculate))
        return tools

    def create_agent(self, client):
        """创建 Agent 实例"""
        return Agent(
            client=client,
            name=self.name,
            instructions=self.instructions,
            tools=self.tools,
        )


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 从 YAML 创建 Agent
    agent_loader = DeclarativeAgent(config_text=AGENT_CONFIG)
    agent = agent_loader.create_agent(client)

    print("=" * 60)
    print("  Declarative Agents Demo - YAML 配置加载")
    print("=" * 60)

    # 显示配置
    print(f"\nAgent 名称: {agent_loader.name}")
    print(f"Agent 描述: {agent_loader.description}")
    print(f"工具数量: {len(agent_loader.tools)}")

    # 对话
    print("\n--- 对话 1: 问候 ---")
    response = await agent.run("你好！")
    print(f"Agent: {response.text}")

    print("\n--- 对话 2: 使用工具 ---")
    response = await agent.run("现在几点了？")
    print(f"Agent: {response.text}")

    print("\n--- 对话 3: 计算 ---")
    response = await agent.run("计算 (2 + 3) * 4 等于多少？")
    print(f"Agent: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
