import asyncio
import os
import argparse
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient


async def main(prompt: str):
    load_dotenv()

    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model = os.getenv("AI_MODEL")

    if not all([api_key, base_url, model]):
        raise ValueError("请在 .env 中配置 AI_API_KEY、AI_BASE_URL、AI_MODEL")

    # 创建 Client
    client = OpenAIChatCompletionClient(
        api_key=api_key,
        base_url=base_url,
        model=model
    )

    agent = Agent(
        client=client,
        name="MyPythonAgent",
        instructions=(
            "You are a professional and friendly AI assistant, "
            "helping users learn Microsoft Agent Framework 1.0. "
            "Keep answers concise and practical, with code examples."
        )
    )

    print("=== Microsoft Agent Framework 1.0 流式输出练习 ===\n")
    print(f"You: {prompt}\n")

    print("Agent is thinking...")
    try:
        # 流式调用
        stream = await agent.run(prompt, stream=True)

        print("\nAgent: ", end="", flush=True)
        full_text = []

        async for update in stream:
            # 从 update 中提取文本内容
            if update.contents:
                for content in update.contents:
                    if content.text:
                        print(content.text, end="", flush=True)
                        full_text.append(content.text)

        # 获取最终响应
        final_response = await stream.get_final_response()
        print("\n")
    except Exception as e:
        print(f"Error: {e}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Microsoft Agent Framework 1.0 流式输出 CLI")
    parser.add_argument("-p", "--prompt", type=str, required=True, help="提示词")
    args = parser.parse_args()
    asyncio.run(main(args.prompt))
