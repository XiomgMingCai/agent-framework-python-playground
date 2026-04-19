# Copyright (c) Microsoft. All rights reserved.
# Overview - Agent 概述

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

    client = OpenAIChatCompletionClient(
        api_key=api_key,
        base_url=base_url,
        model=model
    )

    agent = Agent(
        client=client,
        name="MyPythonAgent",
        instructions="You are a helpful assistant. Use Chinese to respond."
    )

    result = await agent.run(prompt)
    print(result.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", type=str, required=True)
    args = parser.parse_args()
    asyncio.run(main(args.prompt))
