# Item 32: Hosted MCP Tools Connect to External Services via Protocol

Hosted MCP Tools 通过 Model Context Protocol 连接到托管的外部服务（Slack、GitHub、Notion 等）。无需本地运行服务，直接通过 API 连接。

## MCP 协议心智模型

```
Agent → MCP Client → MCP Server (托管) → 外部服务 API
```

## 基础配置

```python
from agent_framework.tools.mcp import MCPHostedTool, MCPToolConfig

# 连接到托管的 Slack MCP 服务
slack_tool = MCPHostedTool(
    name="slack",
    config=MCPToolConfig(
        server_url="https://mcp.example.com/slack",
        api_key=os.getenv("SLACK_MCP_API_KEY"),
    ),
)

agent = Agent(
    client=client,
    tools=[slack_tool],
)
```

## 可用服务

| 服务 | 能力 |
|------|------|
| **Slack** | 发送消息、读取频道 |
| **GitHub** | Issue、PR、代码操作 |
| **Notion** | 读写页面、数据库 |
| **Salesforce** | CRM 数据操作 |
| **Google Workspace** | Docs、Sheets、Drive |

## 认证管理

```python
config = MCPToolConfig(
    server_url="https://mcp.example.com/slack",
    auth={
        "type": "bearer",
        "token": os.getenv("SLACK_TOKEN"),
    },
)
```

## Things to Remember

- Hosted MCP 不需要本地运行服务
- 通过标准协议连接外部 API
- 需要 API Key 或 OAuth 认证
- 适合生产环境使用
