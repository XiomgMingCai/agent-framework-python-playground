# Copyright (c) Microsoft. All rights reserved.
# Agent Pipeline - Agent 管道

import asyncio
import os

from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient


async def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建专业 Agent
    translator = Agent(
        client=client,
        name="Translator",
        instructions="你是一个专业翻译助手，将输入翻译成英文，只返回翻译结果。",
    )

    summarizer = Agent(
        client=client,
        name="Summarizer",
        instructions="你是一个专业总结助手，将输入总结为一句话。",
    )

    # 调度 Agent
    router = Agent(
        client=client,
        name="Router",
        instructions="你是一个调度助手，根据用户请求决定调用翻译还是总结。",
    )

    print("=" * 60)
    print("  Agent Pipeline Demo - Agent 管道")
    print("=" * 60)

    # 使用共享 Session
    session = router.create_session()

    print("\n--- 示例: 翻译 + 总结管道 ---")

    # 翻译
    print("\n[Step 1] 翻译...")
    trans_result = await translator.run("月光下的宁静湖面", session=session)
    print(f"翻译结果: {trans_result.text}")

    # 总结
    print("\n[Step 2] 总结...")
    combined_input = f"基于翻译结果：{trans_result.text}，进行情感总结"
    summary_result = await summarizer.run(combined_input, session=session)
    print(f"总结结果: {summary_result.text}")


if __name__ == "__main__":
    asyncio.run(main())
