# Hosting

将 Agent 部署到服务端，让用户和其他 Agent 可以与其交互。

## 前置知识

- 已完成[基础对话](basic.md)
- 了解 Agent 的基本创建流程

## 托管选项概览

| 选项 | 说明 | 适用场景 |
|------|------|----------|
| DevUI | 本地开发测试 | 快速验证、本地调试 |
| A2A Protocol | Agent-to-Agent 协议 | 多 Agent 系统互联 |
| OpenAI-Compatible | OpenAI 兼容接口 | 现有 OpenAI 客户端接入 |
| Azure Functions | Azure 函数托管 | 无服务器、长运行任务 |
| AG-UI Protocol | Web 前端集成 | 构建 AI Agent 应用 |

## DevUI 本地托管

使用 `agent_framework.devui` 提供的 `serve` 函数快速托管 Agent 到本地 HTTP 服务。

### 单 Agent 托管

**文件：** `examples/hosting/main.py`

```python
import os
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework.devui import serve


def main():
    load_dotenv()

    client = OpenAIChatCompletionClient(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL"),
        model=os.getenv("AI_MODEL"),
    )

    agent = Agent(
        client=client,
        name="HostedAgent",
        instructions="你是一个友好的助手，使用中文回答。",
    )

    # 托管 Agent
    serve(entities=[agent], port=8080, host="127.0.0.1")


if __name__ == "__main__":
    main()
```

### 多 Agent 托管

```python
from agent_framework.devui import serve

# 创建多个 Agent
agent1 = Agent(client=client, name="Agent1", instructions="...")
agent2 = Agent(client=client, name="Agent2", instructions="...")

# 托管多个 Agent
serve(entities=[agent1, agent2], port=8080)
```

## Workflow 托管

```python
from agent_framework import Agent, WorkflowBuilder, Executor, WorkflowContext, handler
from agent_framework.devui import serve

# 创建 Workflow
class UpperCase(Executor):
    @handler
    async def process(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text.upper())

workflow = WorkflowBuilder(start_executor=UpperCase(id="upper")).build()

# 托管 Workflow
serve(entities=[workflow], port=8080)
```

## 运行

```bash
# 启动服务
uv run examples/hosting/main.py

# 服务启动后访问 http://127.0.0.1:8080
# 可通过 Web UI 与 Agent 对话
```

## API 调用示例

服务启动后，可以通过 HTTP API 调用 Agent：

```bash
# POST 请求调用 Agent
curl -X POST http://localhost:8080/api/agents/HostedAgent/run \
  -H "Content-Type: text/plain" \
  -d "你好，请介绍一下你自己"

# GET 请求查看可用 Agent
curl http://localhost:8080/api/agents
```

## serve 函数参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `entities` | `list` | 必填 | 要托管的 Agent 或 Workflow 列表 |
| `port` | `int` | 8080 | 服务端口 |
| `host` | `str` | 127.0.0.1 | 绑定地址 |
| `auto_open` | `bool` | False | 自动打开浏览器 |
| `ui_enabled` | `bool` | True | 启用 Web UI |
| `auth_enabled` | `bool` | False | 启用 Bearer 认证 |
| `auth_token` | `str` | None | 自定义认证 Token |

## 安全配置

!!! warning "安全警告"
    默认配置下服务暴露到网络是不安全的，请使用认证或限制访问。

```python
# 启用认证
serve(
    entities=[agent],
    port=8080,
    host="127.0.0.1",  # 仅本地访问
    auth_enabled=True,    # 启用 Bearer 认证
    auth_token="your-secret-token"
)
```

```bash
# 带认证调用
curl -X POST http://localhost:8080/api/agents/HostedAgent/run \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: text/plain" \
  -d "你好"
```

## 核心要点

| 组件 | 说明 |
|------|------|
| `serve()` | DevUI 提供的托管函数，启动 HTTP 服务 |
| `entities=[agent]` | 要托管的 Agent 或 Workflow 列表 |
| `AgentFunctionApp` | Azure Functions 托管（需安装 `agent-framework-azurefunctions`） |
| `auth_enabled` | 启用认证保护服务安全 |
