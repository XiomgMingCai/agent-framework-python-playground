# Copyright (c) Microsoft. All rights reserved.
# Agent Skills - 可插拔技能包

import asyncio
import os
import json
from pathlib import Path

from dotenv import load_dotenv

from agent_framework import Agent, Skill, SkillResource, SkillsProvider
from agent_framework.openai import OpenAIChatCompletionClient


def create_code_defined_skill() -> Skill:
    """代码定义的技能：风格指南"""
    code_style = Skill(
        name="code-style",
        description="Coding style guidelines and best practices",
        content="Use this skill when answering coding style questions.",
        resources=[
            SkillResource(
                name="style-guide",
                content="- 4-space indentation\n- Max 120 chars per line\n- Use type hints",
            ),
        ],
    )
    return code_style


def create_calculator_skill() -> Skill:
    """带脚本的技能：计算器"""
    calc = Skill(
        name="calculator",
        description="Perform mathematical calculations",
        content="Use the calculate script for math operations.",
    )

    @calc.script(name="calculate", description="result = value × factor")
    def calculate(value: float, factor: float) -> str:
        result = round(value * factor, 4)
        return json.dumps({"value": value, "factor": factor, "result": result})

    return calc


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 混合：文件技能 + 代码技能
    skills_provider = SkillsProvider(
        skill_paths=[Path(__file__).parent / "skills"],
        skills=[create_code_defined_skill(), create_calculator_skill()],
    )

    agent = Agent(
        client=client,
        name="SkillsAgent",
        instructions="你是一个有帮助的助手",
        context_providers=[skills_provider],
    )

    print("=" * 60)
    print("  Agent Skills Demo - 技能扩展")
    print("=" * 60)

    # 代码风格咨询
    print("\n--- 示例 1: 代码风格咨询 ---")
    response = await agent.run("我们代码规范对缩进有什么要求？")
    print(f"响应: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
