# Item 33: Local MCP Tools Run on Your Infrastructure

Local MCP Tools 在本地基础设施上运行 MCP Server，适合需要数据隔离或自定义逻辑的场景。

## 本地 MCP 心智模型

```
Agent → MCP Client → Local MCP Server → 本地服务/数据库
```

## 启动本地 MCP Server

```python
from agent_framework.tools.mcp import MCPLocalServer, MCPServerConfig

server = MCPLocalServer(
    name="local-db",
    config=MCPServerConfig(
        command=["python", "-m", "mcp_server"],
        env={"DB_PATH": "/path/to/db"},
    ),
)

# 启动服务器
await server.start()

# 获取工具
tools = await server.get_tools()
```

## 自定义 MCP Server

```python
# mcp_server.py
from mcp.server import MCPServer
from mcp.types import Tool

server = MCPServer(name="my-tools")

@server.tool(name="query_db", description="执行数据库查询")
def query_db(sql: str) -> str:
    return execute_query(sql)

if __name__ == "__main__":
    server.run()
```

## 与 Hosted 对比

| 维度 | Local MCP | Hosted MCP |
|------|-----------|------------|
| **部署** | 本地/私有云 | 托管服务 |
| **延迟** | 低 | 中 |
| **数据安全** | 完全控制 | 部分信任 |
| **维护** | 自己负责 | 服务商负责 |

## Things to Remember

- Local MCP 数据完全在本地
- 需要自行维护 MCP Server
- 适合敏感数据场景
- 延迟更低，无网络依赖
