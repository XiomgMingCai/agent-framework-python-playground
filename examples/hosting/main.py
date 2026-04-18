# Copyright (c) Microsoft. All rights reserved.
# Based on: https://learn.microsoft.com/en-us/agent-framework/get-started/hosting
# Step 6: Host Your Agent - 使用 DevUI 本地托管 Agent

import os
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework.devui import serve


def main():
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
        model=model,
    )

    # 创建 Agent
    agent = Agent(
        client=client,
        name="HostedAgent",
        instructions="你是一个友好的助手，使用中文回答。",
    )

    print("=" * 60)
    print("  Agent 托管服务")
    print("=" * 60)
    print(f"  启动服务: http://127.0.0.1:8080")
    print(f"  可通过 UI 界面与 Agent 对话")
    print("=" * 60)

    # 托管 Agent（阻塞调用）
    serve(entities=[agent], port=8080, host="127.0.0.1", auto_open=False)


if __name__ == "__main__":
    main()
