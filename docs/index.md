# Microsoft Agent Framework 1.0 Python 练习

基于 `agent_framework` 的 Python 学习项目，通过多个练习主题逐步掌握 Agent 开发。

## 前置环境

在 `.env` 中配置 API：

```env
AI_API_KEY=your-api-key
AI_BASE_URL=https://api.siliconflow.cn/v1
AI_MODEL=Qwen/Qwen3.5-35B-A3B
```

> 支持任意 OpenAI Chat Completions 兼容 API（如 SiliconFlow、DeepSeek 等）

## 练习主题

| 主题 | 说明 | 难度 |
|------|------|------|
| [基础对话](basic.md) | 非流式调用，理解 Agent 基本用法 | ⭐ |
| [流式输出](streaming.md) | 实时流式响应，提升用户体验 | ⭐⭐ |
| [工具调用](tool-use.md) | 让 Agent 调用外部函数，扩展执行能力 | ⭐⭐⭐ |
| [多轮对话](multi-turn.md) | 让 Agent 记住对话历史，支持连续上下文交互 | ⭐⭐⭐ |
| [Memory](memory.md) | 通过 ContextProvider 实现自定义记忆与持久化 | ⭐⭐⭐⭐ |
| [Workflows](workflow.md) | 串联多个步骤的工作流编排 | ⭐⭐⭐⭐ |
| [Hosting](hosting.md) | 将 Agent 部署到本地服务器或云端 | ⭐⭐⭐⭐ |

## 技术栈

- **框架**：[agent_framework](https://github.com/microsoft/agent-framework)
- **文档工具**：MkDocs + Material
- **API**：OpenAI Chat Completions 兼容接口
