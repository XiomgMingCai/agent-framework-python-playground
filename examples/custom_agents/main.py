# Copyright (c) Microsoft. All rights reserved.
# Custom Agents - 自定义 Agent 类，完全控制执行逻辑

import asyncio
import os
from collections.abc import AsyncIterable, Awaitable, Sequence
from typing import Any, Literal, overload
from dotenv import load_dotenv

from agent_framework import (
    Agent,
    AgentResponse,
    AgentResponseUpdate,
    AgentSession,
    BaseAgent,
    Content,
    Message,
    ResponseStream,
    normalize_messages,
)
from agent_framework.openai import OpenAIChatCompletionClient


class EchoAgent(BaseAgent):
    """自定义 Echo Agent：将用户消息加上前缀回显"""

    echo_prefix: str = "Echo: "

    def __init__(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        echo_prefix: str = "Echo: ",
        **kwargs: Any,
    ) -> None:
        self.echo_prefix = echo_prefix
        super().__init__(
            name=name or "EchoAgent",
            description=description or "A simple echo agent",
            **kwargs,
        )

    @overload
    def run(
        self,
        messages: str | Message | Sequence[str | Message] | None = None,
        *,
        stream: Literal[False] = False,
        session: AgentSession | None = None,
        **kwargs: Any,
    ) -> Awaitable[AgentResponse]: ...

    @overload
    def run(
        self,
        messages: str | Message | Sequence[str | Message] | None = None,
        *,
        stream: Literal[True],
        session: AgentSession | None = None,
        **kwargs: Any,
    ) -> ResponseStream[AgentResponseUpdate, AgentResponse]: ...

    def run(
        self,
        messages: str | Message | Sequence[str | Message] | None = None,
        *,
        stream: bool = False,
        session: AgentSession | None = None,
        **kwargs: Any,
    ) -> Awaitable[AgentResponse] | ResponseStream[AgentResponseUpdate, AgentResponse]:
        if stream:
            return ResponseStream(
                self._run_stream(messages=messages, session=session, **kwargs),
                finalizer=AgentResponse.from_updates,
            )
        return self._run(messages=messages, session=session, **kwargs)

    async def _run(
        self,
        messages: str | Message | Sequence[str | Message] | None = None,
        *,
        session: AgentSession | None = None,
        **kwargs: Any,
    ) -> AgentResponse:
        normalized = normalize_messages(messages)

        if not normalized:
            text = "你好！我是自定义 Echo Agent。发送消息我会加上前缀回显。"
        else:
            last = normalized[-1]
            text = f"{self.echo_prefix}{last.text}" if last.text else f"{self.echo_prefix}[收到非文本消息]"

        response_msg = Message(role="assistant", contents=[Content.from_text(text)])

        if session is not None:
            stored = session.state.setdefault("memory", {}).setdefault("messages", [])
            stored.extend(normalized)
            stored.append(response_msg)

        return AgentResponse(messages=[response_msg])

    async def _run_stream(
        self,
        messages: str | Message | Sequence[str | Message] | None = None,
        *,
        session: AgentSession | None = None,
        **kwargs: Any,
    ) -> AsyncIterable[AgentResponseUpdate]:
        normalized = normalize_messages(messages)

        if not normalized:
            text = "你好！我是自定义 Echo Agent。发送消息我会加上前缀回显。"
        else:
            last = normalized[-1]
            text = f"{self.echo_prefix}{last.text}" if last.text else f"{self.echo_prefix}[收到非文本消息]"

        words = text.split()
        for i, word in enumerate(words):
            chunk = f" {word}" if i > 0 else word
            yield AgentResponseUpdate(
                contents=[Content.from_text(chunk)],
                role="assistant",
            )
            await asyncio.sleep(0.05)

        if session is not None:
            complete_msg = Message(role="assistant", contents=[Content.from_text(text)])
            stored = session.state.setdefault("memory", {}).setdefault("messages", [])
            stored.extend(normalized)
            stored.append(complete_msg)


async def main():
    load_dotenv()

    print("=" * 60)
    print("  Custom Agents Demo - 自定义 Agent")
    print("=" * 60)

    # 示例 1：使用自定义 EchoAgent
    print("\n--- 示例 1：自定义 EchoAgent（非流式）---")
    echo_agent = EchoAgent(name="EchoAgent", echo_prefix="回显: ")

    response1 = await echo_agent.run("你好，Agent！")
    print(f"输入: 你好，Agent！")
    print(f"输出: {response1.messages[-1].text}")

    # 示例 2：EchoAgent 流式
    print("\n--- 示例 2：自定义 EchoAgent（流式）---")
    echo_agent2 = EchoAgent(name="EchoAgent2", echo_prefix=">> ")
    session = echo_agent2.create_session()

    print(f"输入: 流式消息测试")
    print(f"输出:", end=" ", flush=True)

    stream = echo_agent2.run("流式消息测试", stream=True, session=session)
    async for update in stream:
        if update.text:
            print(update.text, end="", flush=True)
    print()

    # 示例 3：在自定义 Agent 中调用 LLM
    print("\n--- 示例 3：自定义 Agent 调用 LLM ---")
    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    # 创建一个使用 LLM 的自定义 Agent
    llm_agent = Agent(
        client=client,
        name="LLMAgent",
        instructions="你是一个诗人，用简洁优雅的语言回复。",
    )

    response3 = await llm_agent.run("用一句话形容月光")
    print(f"输入: 用一句话形容月光")
    print(f"输出: {response3.text}")


if __name__ == "__main__":
    asyncio.run(main())