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

    # 创建支持 SiliconFlow 的 Client
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

    print("=== Microsoft Agent Framework 1.0 Python 基础练习 ===\n")
    print(f"You: {prompt}\n")

    print("Agent is thinking...")
    try:
        result = await agent.run(prompt)
        print(f"\nAgent: {result.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Microsoft Agent Framework 1.0 Python CLI")
    parser.add_argument("-p", "--prompt", type=str, required=True, help="提示词")
    args = parser.parse_args()
    asyncio.run(main(args.prompt))