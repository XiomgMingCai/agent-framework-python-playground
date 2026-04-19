# Copyright (c) Microsoft. All rights reserved.
# FastAPI A2A Server - 使用 FastAPI 实现 A2A 协议服务端
# 支持 JSON-RPC 2.0 格式的请求和响应

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

# A2A 协议类型
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    Message,
    Role,
    Task,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
)


# ========== JSON-RPC 模型 ==========

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any]
    id: str | None = None


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: str | None = None
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None


# ========== Agent 实现 ==========

class A2AAgentWrapper:
    """包装 agent_framework Agent 为 A2A Server"""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.sessions: dict[str, Any] = {}

    async def handle_message(self, message_data: dict, context_id: str | None = None) -> dict[str, Any]:
        """处理消息"""
        message = Message(**message_data)
        context_id = context_id or message.contextId or str(uuid.uuid4())

        if context_id not in self.sessions:
            self.sessions[context_id] = self.agent.create_session()

        session = self.sessions[context_id]

        # 提取文本内容
        text_parts = []
        for part in message.parts:
            if hasattr(part, 'text') and part.text:
                text_parts.append(part.text)

        user_text = "\n".join(text_parts)

        # 调用 Agent
        response = await self.agent.run(user_text, session=session)

        return {
            "kind": "message",
            "role": "agent",
            "parts": [{"kind": "text", "text": response.text}],
            "messageId": str(uuid.uuid4()),
            "contextId": context_id,
        }

    async def handle_jsonrpc(self, request: JSONRPCRequest, stream: bool = False):
        """处理 JSON-RPC 请求"""
        method = request.method
        params = request.params

        if method == "message/send":
            message_data = params.get("message", {})
            result = await self.handle_message(message_data)
            return JSONRPCResponse(id=request.id, result=result)

        elif method == "message/stream":
            message_data = params.get("message", {})
            context_id = message_data.get("contextId") or str(uuid.uuid4())

            if context_id not in self.sessions:
                self.sessions[context_id] = self.agent.create_session()

            session = self.sessions[context_id]

            # 提取文本内容
            text_parts = []
            for part in message_data.get("parts", []):
                if hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
            user_text = "\n".join(text_parts) if text_parts else ""

            # 流式调用
            stream_result = self.agent.run(user_text, stream=True, session=session)

            # 返回 SSE generator
            return stream_result, context_id

        else:
            return JSONRPCResponse(
                id=request.id,
                error={"code": -32601, "message": f"Method not found: {method}"},
            )

    async def get_task_result(self, task_id: str) -> dict[str, Any]:
        """获取任务结果（用于轮询）"""
        if not hasattr(self, '_tasks') or task_id not in self._tasks:
            return {"error": "Task not found"}

        task = self._tasks[task_id]
        context_id = task["context_id"]
        message_data = task["message_data"]

        if not task.get("completed"):
            session = self.sessions.get(context_id)
            if session:
                # 调用 Agent
                text_parts = []
                for part in message_data.get("parts", []):
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                user_text = "\n".join(text_parts) if text_parts else ""

                # 检查是否已有结果
                if not task.get("result"):
                    task["result"] = await self.agent.run(user_text, session=session)
                task["completed"] = True

            return {
                "kind": "task",
                "id": task_id,
                "state": {"status": "completed" if task["completed"] else "working"},
                "result": task.get("result"),
            }

        return {
            "kind": "task",
            "id": task_id,
            "state": {"status": "completed"},
        }


# ========== FastAPI 应用 ==========

agent_wrapper: A2AAgentWrapper | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_wrapper

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

    # 创建 Agent
    agent = Agent(
        client=client,
        name="A2AServer",
        instructions="你是一个友好、简洁的助手。",
    )

    agent_wrapper = A2AAgentWrapper(agent)

    print("=" * 60)
    print("  A2A Server 启动成功!")
    print("=" * 60)
    print(f"  Agent Card: GET /.well-known/agent-card.json")
    print(f"  JSON-RPC:   POST / (统一端点)")
    print("=" * 60)

    yield

    print("A2A Server 关闭")


app = FastAPI(
    title="A2A Server",
    description="基于 FastAPI 的 A2A 协议服务端",
    version="1.0.0",
    lifespan=lifespan,
)


# ========== A2A 端点 ==========

@app.get("/.well-known/agent-card.json", response_model=AgentCard)
async def get_agent_card():
    """返回 Agent Card，用于 Agent 发现"""
    return AgentCard(
        name="A2AServer",
        description="基于 FastAPI + agent_framework 的 A2A 服务端",
        version="1.0.0",
        url="http://127.0.0.1:8080",
        capabilities=AgentCapabilities(
            streaming=True,
            push_notifications=False,
            state_transition_history=False,
        ),
        default_input_modes=["text"],
        default_output_modes=["text"],
        skills=[
            AgentSkill(
                id="general-assistant",
                name="General Assistant",
                description="通用助手，可以回答各种问题",
                tags=["assistant", "general"],
            )
        ],
    )


@app.post("/")
async def handle_jsonrpc(request: Request):
    """统一处理所有 JSON-RPC 请求"""
    if agent_wrapper is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    body = await request.json()
    jsonrpc_request = JSONRPCRequest(**body)

    result = await agent_wrapper.handle_jsonrpc(jsonrpc_request)

    # 如果是 streaming，返回 SSE
    if isinstance(result, tuple):
        stream_result, context_id = result

        async def event_generator():
            task_id = str(uuid.uuid4())
            rpc_id = str(uuid.uuid4())

            # Step 1: 先发送 Task 对象（用于获取 task ID）
            task = Task(
                id=task_id,
                context_id=context_id,
                status=TaskStatus(state=TaskState.working),
            )
            task_response = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": task.model_dump(mode="json"),
            }
            yield f"data: {json.dumps(task_response)}\n\n"

            # Step 2: 发送 TaskStatusUpdateEvent（消息放在 status.message 中）
            full_text = ""
            async for update in stream_result:
                if update.text:
                    full_text += update.text

            if full_text:
                status_message = Message(
                    message_id=str(uuid.uuid4()),
                    role=Role.agent,
                    parts=[TextPart(kind="text", text=full_text)],
                )
                status_update = TaskStatusUpdateEvent(
                    context_id=context_id,
                    task_id=task_id,
                    final=False,
                    status=TaskStatus(state=TaskState.working, message=status_message),
                )
                status_event = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "result": status_update.model_dump(mode="json"),
                }
                yield f"data: {json.dumps(status_event)}\n\n"

            # Step 3: 最后发送完成状态
            complete_status = TaskStatus(state=TaskState.completed)
            complete_event_obj = TaskStatusUpdateEvent(
                context_id=context_id,
                task_id=task_id,
                final=True,
                status=complete_status,
            )
            complete_event = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "result": complete_event_obj.model_dump(mode="json"),
            }
            yield f"data: {json.dumps(complete_event)}\n\n"

        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # 非 streaming，返回 JSON
    return JSONResponse(content=result.model_dump(exclude_none=True))


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务状态和结果（用于轮询）"""
    if agent_wrapper is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    result = await agent_wrapper.get_task_result(task_id)
    return JSONResponse(content=result)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "agent": "A2AServer"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)