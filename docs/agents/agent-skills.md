# Item 8: Use Skills for Progressive Knowledge Loading

## 问题

你想让 Agent 处理专业领域（比如财务报销），于是把所有规则塞进 Instructions：

```python
agent = Agent(
    client=client,
    instructions="""
    你是报销专家，请遵循以下规则：

    # 国内出差报销
    1. 机票：经济舱实报实销，高铁二等座...
    2. 住宿：北上广深 600元/天，其他城市 400元/天...
    3. 餐饮：50元/餐，一天不超过 150元...

    # 国外出差报销
    1. 机票：商务舱报销条件...
    2. 住宿：参照外事差旅标准...
    ...（此处省略 500 行）
    """
)
```

**问题来了**：

1. **每次调用都消耗大量 token**——即使用户只问"我的机票能报吗"
2. **上下文窗口被浪费**——大量规则挤占了模型思考空间
3. **更新困难**——规则改了要改代码

## 深入解释

Skills 是 Agent Framework 的**按需加载知识**机制，灵感来自 Dynamic Scoping 和 lazy loading：

```
┌──────────────────────────────────────────────────────────┐
│              传统方式：一次性加载所有知识                    │
├──────────────────────────────────────────────────────────┤
│  Instructions: [5000 tokens 报销规则...]                 │
│                     ↓                                    │
│  每次请求都带 5000 tokens，不管用户问的是什么               │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│              Skills 方式：渐进式加载知识                    │
├──────────────────────────────────────────────────────────┤
│  第一步：Agent 知道有哪些 Skills（~100 tokens）           │
│          "我有 expense-skill、travel-skill..."            │
│                     ↓                                    │
│  第二步：用户问"机票报销标准"                             │
│          → 只加载 expense-skill 中的机票部分（~500 tokens） │
│                     ↓                                    │
│  第三步：用户问"国外差旅"                                 │
│          → 加载 expense-skill 中的国外部分（~500 tokens）  │
└──────────────────────────────────────────────────────────┘
```

**心智模型**：Skills 就像图书馆的**借阅系统**——不把所有书都放在你桌上（浪费空间），而是按需借阅，用完归还。

## 推荐做法

### 方法一：内联 Skill（简单场景）

```python
from agent_framework import Agent, Skill, SkillsProvider

# 定义 Skill
expense_skill = Skill(
    name="expense-rules",
    description="处理报销政策咨询，包括机票、住宿、餐饮等报销标准",
)

# 创建 SkillsProvider
provider = SkillsProvider(skills=[expense_skill])

# 注入到 Agent
agent = Agent(
    client=client,
    name="ExpenseAgent",
    instructions="你是一个报销助手。当用户询问报销相关问题时，加载对应的 skill。",
    context_providers=[provider],
)
```

### 方法二：带资源的 Skill（复杂场景）

```python
from agent_framework import Skill, SkillResource

expense_skill = Skill(
    name="expense-rules",
    description="处理报销政策咨询",
    resources=[
        SkillResource(
            name="domestic-travel",
            description="国内出差报销标准",
            content="""
            # 国内出差报销标准

            ## 机票
            - 经济舱实报实销
            - 高铁二等座实报实销

            ## 住宿
            - 北上广深：600元/天
            - 其他城市：400元/天

            ## 餐饮
            - 50元/餐
            - 日上限：150元
            """,
        ),
        SkillResource(
            name="overseas-travel",
            description="国外出差报销标准",
            content="""
            # 国外出差报销标准

            ## 机票
            - 商务舱：需部门 VP 审批
            - 经济舱：实报实销

            ## 住宿
            - 参照外事差旅住宿标准
            - 上限：100 USD/天
            """,
        ),
    ],
)
```

### 方法三：SKILL.md 文件技能（团队共享）

```
examples/agent_skills/skills/expense/
├── SKILL.md          # Skill 定义
└── resources/
    ├── domestic.md   # 国内报销规则
    └── overseas.md   # 国外报销规则
```

```python
# 从文件系统加载 Skill
expense_skill = Skill.from_directory("examples/agent_skills/skills/expense")
```

## 好 vs 坏对比

```python
# 坏做法：所有知识塞进 Instructions
agent = Agent(
    client=client,
    instructions="""
    你是一个报销助手...
    [10000 行报销规则]...
    """
)
# 每次调用消耗 10000+ tokens，即使只问一个问题

# 好做法：用 Skills 按需加载
provider = SkillsProvider(skills=[
    expense_skill,
    travel_skill,
    it_skill,
])
agent = Agent(
    client=client,
    instructions="你是一个专业助手，有多个技能可用。",
    context_providers=[provider],
)
# 用户问机票问题 → 只加载 expense-skill 的机票部分 (~500 tokens)
```

## 扩展讨论

### 加载阶段详解

| 阶段 | Token 消耗 | 说明 |
|------|-----------|------|
| **Advertise** | ~100 | 仅 Skill 名称和描述 |
| **Load** | 按需 | 用户问什么，加载什么 |
| **Read resource** | 按需 | 仅读取相关 resource |

### 与 RAG 的对比

| 特性 | Skills | RAG |
|------|--------|-----|
| 加载方式 | 整块加载 | 向量检索 |
| 适用场景 | 结构化知识（规则、手册） | 非结构化文档 |
| Token 控制 | 精确可控 | 依赖检索质量 |
| 更新方式 | Skill 版本化 | 向量索引重建 |

### Skill 组合策略

```python
# 按领域分组的大型 Skill
finance_skill = Skill(
    name="finance",
    description="财务相关知识",
    resources=[
        SkillResource(name="expense", content="..."),
        SkillResource(name="budget", content="..."),
        SkillResource(name="invoice", content="..."),
    ],
)

# 按场景分组的小型 Skill
# 用户问题匹配 → 选择性加载
```

### 企业级考虑

```python
# 1. Skill 版本管理
expense_skill = Skill(
    name="expense-rules",
    version="2024-Q1",  # 带版本号
    content="...",
)

# 2. Skill 访问控制
from agent_framework import SkillAccessPolicy

policy = SkillAccessPolicy(
    allowed_roles=["finance-team", "admin"],
    denied_users=["intern-2024"],
)

# 3. Skill 变更追踪
# Skill 更新时记录变更日志，便于审计
```

## Things to Remember

- Skills 解决的是"知识太多，一次性加载太贵"的问题
- Skills = **名称** + **描述** + **内容/资源**，按需渐进加载
- `SkillsProvider` 管理多个 Skill，通过 `context_providers` 注入 Agent
- 加载粒度：问什么加载什么，不是加载整个 Skill
- **Advertise 阶段**只消耗 ~100 tokens，告诉 Agent"你有哪些技能"
- Skills 适合结构化知识（规则、手册、流程），RAG 适合非结构化文档
- Skill 内容应该模块化拆分（按 topic 或场景），而不是做成一个大文件
- 生产环境中 Skill 应版本化管理，便于回滚和审计
