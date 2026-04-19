# Copyright (c) Microsoft. All rights reserved.
# Multi-Agent - 多 Agent 协作，一个 Agent 调用另一个 Agent

import asyncio
import os
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient


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

    # ========== 创建专门的 Agent ==========

    # 翻译 Agent
    translator = Agent(
        client=client,
        name="Translator",
        instructions=(
            "你是一个专业的翻译助手。 "
            "将用户输入翻译成指定语言，保留原文的语气和风格。 "
            "只输出翻译结果，不要其他解释。"
        ),
    )

    # 总结 Agent
    summarizer = Agent(
        client=client,
        name="Summarizer",
        instructions=(
            "你是一个专业的文本总结助手。 "
            "将长文本压缩成简洁的要点，保留核心信息。 "
            "只输出总结内容，不要其他解释。"
        ),
    )

    # 调度 Agent（Router）
    router = Agent(
        client=client,
        name="Router",
        instructions=(
            "你是一个智能调度助手。分析用户请求，将任务分配给合适的专业 Agent："
            "- 如果用户需要翻译 → 调用 translator"
            "- 如果用户需要总结 → 调用 summarizer"
            "- 如果不确定 → 直接回答"
            "通过 context 变量传递任务给对应的 Agent，格式：{agent_name}: {task}"
        ),
    )

    print("=" * 60)
    print("  Multi-Agent Demo - 多 Agent 协作")
    print("=" * 60)

    session = router.create_session()

    # ========== 示例 1：翻译任务 ==========
    print("\n--- 示例 1：翻译任务 ---")
    query1 = "把这句话翻译成英文：月光下的宁静湖面"
    print(f"用户: {query1}")

    response1 = await router.run(query1, session=session)
    print(f"Router: {response1.text}")

    # 调用翻译 Agent
    print("\n[调用 Translator Agent]")
    trans_response = await translator.run(query1, session=session)
    print(f"Translator: {trans_response.text}")

    # ========== 示例 2：总结任务 ==========
    print("\n--- 示例 2：总结任务 ---")
    query2 = "请总结以下内容：人工智能的发展历程可以分为三个阶段。第一阶段是符号主义，强调逻辑推理和专家系统。第二阶段是统计学习，以机器学习算法为代表。第三阶段是深度学习，神经网络模型取得了突破性进展。"
    print(f"用户: {query2[:30]}...")

    response2 = await router.run(query2, session=session)
    print(f"Router: {response2.text}")

    # 调用总结 Agent
    print("\n[调用 Summarizer Agent]")
    sum_response = await summarizer.run(query2, session=session)
    print(f"Summarizer: {sum_response.text}")

    # ========== 示例 3：Agent 间传递上下文 ==========
    print("\n--- 示例 3：Agent 间共享上下文 ---")

    # 先让翻译 Agent 处理
    print("[Step 1] Translator 处理中文")
    trans_result = await translator.run("I love the moonlight", session=session)
    print(f"翻译结果: {trans_result.text}")

    # 让总结 Agent 基于翻译结果继续处理
    print("\n[Step 2] Summarizer 基于翻译结果总结")
    combined_query = f"请总结这句话传达的情感：{trans_result.text}"
    sum_result = await summarizer.run(combined_query, session=session)
    print(f"情感总结: {sum_result.text}")


if __name__ == "__main__":
    asyncio.run(main())