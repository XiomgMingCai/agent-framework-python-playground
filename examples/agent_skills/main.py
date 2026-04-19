# Copyright (c) Microsoft. All rights reserved.
# Agent Skills - 可插拔的技能包，让 Agent 掌握专业能力

import os
import json
from pathlib import Path
from textwrap import dedent
from dotenv import load_dotenv

from agent_framework import Agent, Skill, SkillResource, SkillsProvider
from agent_framework.openai import OpenAIChatCompletionClient


def create_code_defined_skill() -> Skill:
    """创建一个代码定义的技能：代码风格指南"""
    code_style_skill = Skill(
        name="code-style",
        description="Coding style guidelines and best practices for the team",
        content=dedent("""\
            Use this skill when answering questions about coding style,
            conventions, or best practices for the team.
        """),
        resources=[
            SkillResource(
                name="style-guide",
                content=dedent("""\
                    # Team Coding Style Guide
                    - Use 4-space indentation (no tabs)
                    - Maximum line length: 120 characters
                    - Use type annotations on all public functions
                    - Prefer async/await over callbacks
                """),
            ),
        ],
    )
    return code_style_skill


def create_script_defined_skill() -> Skill:
    """创建一个带脚本的技能：数学计算器"""
    calculator = Skill(
        name="calculator",
        description="Perform mathematical calculations using basic operations",
        content="Use the calculate script to perform calculations.",
    )

    @calculator.script(name="calculate", description="Calculate: result = value × factor")
    def calculate(value: float, factor: float) -> str:
        """将 value 乘以 factor 进行计算"""
        result = round(value * factor, 4)
        return json.dumps({"value": value, "factor": factor, "result": result})

    return calculator


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

    # 创建代码定义的技能
    code_style_skill = create_code_defined_skill()
    calculator_skill = create_script_defined_skill()

    # 从文件发现技能
    skills_dir = Path(__file__).parent / "skills"
    file_skill_paths = [skills_dir] if skills_dir.exists() else []

    # 创建 SkillsProvider（支持文件 + 代码混合）
    skills_provider = SkillsProvider(
        skill_paths=file_skill_paths,
        skills=[code_style_skill, calculator_skill],
    )

    agent = Agent(
        client=client,
        name="SkillsAgent",
        instructions="你是一个有帮助的助手，可以根据需要加载技能来回答问题。",
        context_providers=[skills_provider],
    )

    print("=" * 60)
    print("  Agent Skills Demo - 技能扩展")
    print("=" * 60)

    session = agent.create_session()

    # 示例 1：使用代码定义的转换脚本
    print("\n--- 示例 1：单位转换 ---")
    query1 = "26.2 英里等于多少公里？"
    print(f"输入: {query1}")
    response1 = await agent.run(query1, session=session)
    print(f"响应: {response1.text}")

    # 示例 2：使用代码定义的风格指南技能
    print("\n--- 示例 2：代码风格咨询 ---")
    query2 = "我们团队的代码规范对缩进有什么要求？"
    print(f"输入: {query2}")
    response2 = await agent.run(query2, session=session)
    print(f"响应: {response2.text}")

    # 示例 3：文件发现的技能（如果存在）
    print("\n--- 示例 3：文件技能（单位转换器）---")
    query3 = "请把 100 磅转换成公斤"
    print(f"输入: {query3}")
    response3 = await agent.run(query3, session=session)
    print(f"响应: {response3.text}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())