# Item 9: Use Skills for Progressive Knowledge Loading

Skills 让 Agent 按需加载专业知识，而不是把所有知识一股脑塞进 context。

## 问题

把大量知识写进 instructions：

```python
agent = Agent(
    client=client,
    instructions="""
    你是报销专家，请遵循以下规则：
    1. 国内出差：机票报销...
    2. 国外出差：机票报销...
    3. 住宿标准：...
    ... (10000 字规则)
    """
)
```

每次调用都带 10000 字，浪费 token。

## 解决方案

用 Skills 渐进式加载：

```python
from agent_framework import Skill, SkillResource, SkillsProvider

expense_skill = Skill(
    name="expense-rules",
    description="报销规则咨询",
    content="当用户询问报销规则时加载此技能",
    resources=[
        SkillResource(
            name="domestic",
            content="- 国内出差：机票报销标准：经济舱...\n",
        ),
    ],
)

provider = SkillsProvider(skills=[expense_skill])

agent = Agent(
    client=client,
    context_providers=[provider],
    instructions="你是一个报销助手"
)
```

## 加载阶段

| 阶段 | Token 消耗 | 说明 |
|------|-----------|------|
| Advertise | ~100 | 仅名称和描述 |
| Load | <5000 | 按需加载完整指令 |
| Read resources | 按需 | 读文件内容 |

## Things to Remember

- Skill = 名称 + 描述 + 内容 + 资源，按需渐进加载
- SkillsProvider 管理多个 Skill，通过 context_providers 注入 Agent
- 先用少的 token 告诉 Agent 有什么技能，真的需要时再加载完整内容
- 文件技能用 SKILL.md 目录，代码技能用 Python 定义
