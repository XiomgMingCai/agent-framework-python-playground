# Claude Code 项目笔记

## 通用文档管理规则
- 大多数现代 Python 团队采用 **docs/ 目录 + Markdown 文件**的结构
- 将文档当作代码一样管理（版本控制、代码审查）
- 使用 MkDocs + Material 主题构建静态文档站
- 文档与代码同仓库，主题一一对应

## 示例代码目录规则
- 所有示例放在 `examples/[主题]/` 子目录
- 主入口文件统一命名为 `main.py`
- 每个主题独立，方便按需运行和对比学习

## MkDocs + Material 文档编写规范

### 文件与目录
- 文档源文件放在 `docs/` 目录
- 每个主题一个 `.md` 文件，文件名用英文 kebab-case（如 `streaming-output.md`）
- `docs/index.md` 为文档首页
- 图片放在 `docs/assets/` 子目录

### 页面结构（每篇文档）
1. **标题** — 一级标题 `# 主题名`
2. **简介** — 1-2 句话说明本节内容
3. **前置知识**（可选）— 衔接前后内容
4. **正文** — 分层组织，使用二级/三级标题
5. **核心要点** — 用表格总结关键概念
6. **运行/验证** — 如何运行示例代码验证
7. **延伸阅读**（可选）— 相关链接

### 排版规范
- 中文与英文/数字之间加空格
- 代码块必须有语言标识：` ```python `
- 代码块禁止截断，使用完整可运行片段
- 链接用 Markdown 格式 `[文字](url)`
- 无序列表用 `-`，有序列表用 `1.`
- 强调用 `**粗体**`，别滥用斜体

### Material 特有语法
```markdown
!!! note "提示"
    这是提示内容

!!! warning "注意"
    这是警告内容

??? info "详情"
    可折叠的详情块

!!! example "示例"
    示例说明
```

### 表格规范
- 用 `|` 分隔列，`---` 分隔表头与内容
- 表头小写加粗，列名用英文
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Value    | Value    |
```

### 代码块规范
- 代码文件路径放在代码块上方，用 `**文件：** ` 标注
- 运行命令放在代码块下方，用 `**运行：** ` 标注
- 禁止在代码块中混入说明文字

### 目录结构（mkdocs.yml）
```yaml
nav:
  - 首页: index.md
  - 基础对话: basic.md
  - 流式输出: streaming.md
  - 工具调用: tool-use.md
  - 多轮对话: multi-turn.md
```
- 最多两层（首页 + 二级页面）
- 避免超过 7 个页面，考虑拆分子章节

### 编写原则
- **DITA 风格**：每篇一个主题，主题独立
- **KISS 原则**：简单直接，不重复造轮子
- **DRY 原则**：代码示例只出现一次，避免复制粘贴导致不一致
- 写给读者而非作者 — 考虑读者背景和目标
- 文档是代码的副产品，先让代码跑通再写文档

## 项目结构
```
examples/
├── basic/         # 基础示例，非流式对话
│   └── main.py
├── streaming/     # 流式输出示例
│   └── main.py
├── tool_use/     # 工具调用示例
│   └── main.py
└── multi_turn/   # 多轮对话示例
    └── main.py

docs/
├── index.md       # 文档首页
├── basic.md       # 基础对话文档
├── streaming.md   # 流式输出文档
├── tool-use.md   # 工具调用文档
└── multi-turn.md # 多轮对话文档
```

## 经验总结

### 6. agent_framework.tools 模块不存在
- **错误**：`ModuleNotFoundError: No module named 'agent_framework.tools'`
- **原因**：`tool` 装饰器不在 `agent_framework.tools` 子模块中
- **解决**：`from agent_framework import tool`
- **预防**：编写代码前先用 `uv run python -c "from agent_framework import tool"` 验证导入路径

### 1. agent_framework 导入错误
- **错误**：`ImportError: cannot import name 'ChatAgent' from 'agent_framework'`
- **原因**：包中没有 `ChatAgent`，正确的类是 `Agent`
- **解决**：`from agent_framework import Agent`

### 2. OpenAI Client 版本不匹配
- **错误**：`Not Found` (404)
- **原因**：`OpenAIChatClient` 使用新版 **Responses API** (`/responses`)，但 SiliconFlow 只支持旧版 **Chat Completions API** (`/chat/completions`)
- **解决**：使用 `OpenAIChatCompletionClient` 替代 `OpenAIChatClient`
  ```python
  from agent_framework.openai import OpenAIChatCompletionClient
  client = OpenAIChatCompletionClient(api_key=..., base_url=..., model=...)
  ```

### 3. provider 路径错误
- **错误**：`ModuleNotFoundError: No module named 'agent_framework.providers'`
- **原因**：provider 模块路径不存在，正确的路径是 `agent_framework.openai`
- **解决**：`from agent_framework.openai import OpenAIChatCompletionClient`

### 4. 环境变量名不一致
- **原因**：代码中变量名与 .env 中不一致（如 `AI_BASE_URI` vs `AI_BASE_URL`）
- **预防**：保持 .env 变量名与代码一致

### 5. 中文占位符导致编码错误
- **错误**：`UnicodeEncodeError: 'ascii' codec can't encode characters`
- **原因**：.env 中 `AI_API_KEY=sk-你的七牛云API_Key` 包含中文，HTTP 头无法处理
- **预防**：.env 中的占位符必须替换为真实值，不要保留中文占位符

## 关键 API 知识
- `OpenAIChatClient` → Responses API (OpenAI 新版)
- `OpenAIChatCompletionClient` → Chat Completions API (兼容 SiliconFlow、DeepSeek 等)
- 选 client 前先确认 API 服务商支持的 API 类型
