# Microsoft Agent Framework Python 练习

通过可行动的 Item 清单，系统掌握 Agent 开发。

## 学习路径

### 入门（先跑起来）

| Item | 你会学到 | 关键代码 |
|------|----------|----------|
| [Item 1: Create Agents with Both Client and Instructions](agents/overview.md) | Agent 的本质 | `Agent(client=..., instructions=...)` |
| [Item 2: Use Streaming for Real-Time Response](agents/running-agents.md) | 流式调用 | `stream=True` + `async for` |

### 核心能力（扩展 Agent）

| Item | 你会学到 | 关键代码 |
|------|----------|----------|
| [Item 3: Write Tool Docstrings Like Explaining to a Colleague](agents/tools/function-tools.md) | 工具定义 | `@tool` + 清晰 docstring |
| [Item 4: Pass Full History to Each Turn](agents/session.md) | 多轮对话 | `messages=history` |
| [Item 5: Use ContextProvider to Inject State](agents/context-providers.md) | 持久化记忆 | `before_run` / `after_run` |

### Agents 主题（33 个 Items）

#### 核心概念

| Item | 你会学到 | 关键代码 |
|------|----------|----------|
| [Item 6: Handle Markdown-Wrapped JSON](agents/structured-output.md) | 结构化输出 | Pydantic + 正则提取 |
| [Item 7: Use asyncio.create_task() for Background](agents/background-responses.md) | 后台任务 | `create_task()` |
| [Item 8: Use Skills for Progressive Loading](agents/agent-skills.md) | 渐进式技能 | `SkillsProvider` |
| [Item 9: Understand the Three Middleware Types](agents/middleware/defining.md) | 中间件类型 | Agent/Function/Chat |
| [Item 10: Share Sessions to Share Context](agents/agent-pipeline.md) | Agent Pipeline | `session=shared_session` |
| [Item 11: Collect Logs, Metrics, and Traces](agents/observability.md) | 可观测性 | Middleware 拦截 |
| [Item 12: Use ContextProvider to Implement RAG](agents/rag.md) | RAG 模式 | 检索 + 生成 |
| [Item 13: Think of Declarative Agents as YAML-First](agents/declarative-agents.md) | 声明式配置 | YAML + 解析器 |

#### Tools

| Item | 你会学到 |
|------|----------|
| [Item 14: Tools Are How Agents Interact with the World](agents/tools/index.md) | 工具本质 |
| [Item 15: Use Tool Approval for Dangerous Operations](agents/tools/tool-approval.md) | 工具审批 |
| [Item 16: Code Interpreter Enables Dynamic Execution](agents/tools/code-interpreter.md) | 代码执行 |
| [Item 17: File Search Enables Codebase Intelligence](agents/tools/file-search.md) | 文件搜索 |
| [Item 18: Web Search Extends Knowledge Beyond Training](agents/tools/web-search.md) | 网络搜索 |
| [Item 19-20: MCP Tools Connect External Services](agents/tools/hosted-mcp-tools.md) | MCP 协议 |
| [Item 21-22: Local MCP Tools Run on Infrastructure](agents/tools/local-mcp-tools.md) | 本地 MCP |

#### Memory

| Item | 你会学到 | 关键代码 |
|------|----------|----------|
| [Item 23: Memory Is How Agents Retain Information](agents/memory/index.md) | 跨会话存储 |
| [Item 24: Choose the Right Storage Backend](agents/memory/storage.md) | 存储后端 |
| [Item 25: Use Compaction to Prevent Bloat](agents/memory/compaction.md) | 压缩摘要 |

#### Middleware

| Item | 你会学到 | 关键代码 |
|------|----------|----------|
| [Item 26: ChatMiddleware Transforms Messages](agents/middleware/chat-level.md) | 消息转换 |
| [Item 27: Match Middleware Scope to Logging](agents/middleware/agent-vs-run-scope.md) | 作用域 |
| [Item 28: Use Termination to Stop Gracefully](agents/middleware/termination.md) | 优雅停止 |
| [Item 29: Override Results to Inject Custom](agents/middleware/result-overrides.md) | 结果覆盖 |
| [Item 30: Handle Exceptions Without Swallowing](agents/middleware/exception-handling.md) | 异常处理 |
| [Item 31: Share State Across Middleware](agents/middleware/shared-state.md) | 状态共享 |
| [Item 32: Access Runtime Context](agents/middleware/runtime-context.md) | 运行时上下文 |

#### 高级主题

| Item | 你会学到 | 关键代码 |
|------|----------|----------|
| [Item 33: Multimodal Agents Handle Multiple Data Types](agents/multimodal.md) | 多模态 |
| [Item 34: Safety Should Be Layered](agents/agent-safety.md) | 分层安全 |

### 终极技能（Workflows）

| Item | 你会学到 | 关键代码 |
|------|----------|----------|
| [Item 35: Think of Workflows as Directed Graphs](workflow.md) | 工作流心智模型 | Executor 图 + Superstep 同步 |

## 前置环境

在 `.env` 中配置 API：

```env
AI_API_KEY=your-api-key
AI_BASE_URL=https://api.siliconflow.cn/v1
AI_MODEL=Qwen/Qwen2.5-72B-Instruct
```

支持任意 OpenAI Chat Completions 兼容 API（SiliconFlow、DeepSeek 等）。

## 运行示例

```bash
# 基础对话
uv run examples/agents/overview/main.py

# 流式输出
uv run examples/agents/running_agents/main.py

# 工具调用
uv run examples/agents/tools/function_tools/main.py
```

## 技术栈

- **框架**：[agent_framework](https://github.com/microsoft/agent-framework)
- **文档**：MkDocs + Material
- **API**：OpenAI Chat Completions 兼容
