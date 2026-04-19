# Item 15: Use Tool Approval to Guard Dangerous Operations

有些工具调用是不可逆的——删除数据、转账、发送消息。需要人工审批机制来防止 Agent 误操作。

## 审批心智模型

```
Agent 选择工具 → 暂停等待审批 → 人工通过/拒绝 → 执行或终止
```

## 审批流程

```python
from agent_framework import Agent, ToolApproval

class HumanApprover:
    async def approve(self, tool_call):
        print(f"工具调用请求: {tool_call.name}")
        print(f"参数: {tool_call.arguments}")
        response = input("批准? (y/n): ")
        return response.lower() == "y"

agent = Agent(
    client=client,
    tools=[delete_database, send_email, transfer_money],
    tool_approval=ToolApproval(approver=HumanApprover()),
)
```

## 审批类型

| 类型 | 场景 | 行为 |
|------|------|------|
| **每工具审批** | 高风险操作 | 每次调用前暂停 |
| **首次审批** | 中风险操作 | 首次调用时审批，后续自动 |
| **批量审批** | 低风险操作 | 一批调用后统一审批 |

## 条件触发审批

```python
class ConditionalApprover:
    async def should_approve(self, tool_call):
        # 超过阈值才审批
        return tool_call.name in ["delete", "send", "transfer"]

    async def approve(self, tool_call):
        return input(f"批准 {tool_call.name}? (y/n): ").lower() == "y"
```

## Things to Remember

- 高风险工具（删、改、发）必须审批
- 审批是 Agent 暂停执行、人工介入的机制
- 可以基于工具名、参数值、调用频率条件触发审批
- 审批结果：批准则执行，拒绝则抛出异常
