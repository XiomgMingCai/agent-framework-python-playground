# Item 13: Use Declarative Agents for YAML-Based Configuration Management

## 问题

你写了多个 Agent，每个 Agent 的配置（instructions、tools、middleware）都在 Python 代码里硬编码：

```python
# agent_sales.py
sales_agent = Agent(
    client=client,
    name="SalesAgent",
    instructions="你是销售助手，帮助用户选择产品...",
    tools=[get_product_tool, calculate_discount_tool],
)

# agent_support.py
support_agent = Agent(
    client=client,
    name="SupportAgent",
    instructions="你是客服助手，帮助用户解决问题...",
    tools=[search_kb_tool, create_ticket_tool],
)

# agent_analytics.py
analytics_agent = Agent(
    client=client,
    name="AnalyticsAgent",
    instructions="你是分析助手，帮助用户分析数据...",
    tools=[query_db_tool, generate_chart_tool],
)
```

**问题来了**：

1. **修改配置要改代码**——非技术人员无法调整 Agent 行为
2. **版本管理困难**——配置变更无法 code review
3. **环境切换麻烦**——dev/staging/prod 需要不同配置

## 深入解释

Declarative Agent 的核心理念：**配置与代码分离**（Configuration as Code）。

```
┌─────────────────────────────────────────────────────────────┐
│           硬编码方式（Imperative）                            │
├─────────────────────────────────────────────────────────────┤
│  Agent(...)  ← 配置藏在代码里                              │
│  Agent(...)  ← 改配置 = 改代码                              │
│  Agent(...)  ← 无法交给非技术人员                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│           Declarative 方式（声明式）                         │
├─────────────────────────────────────────────────────────────┤
│  agent.yaml ← 配置文件，任何人能改                          │
│     ↓                                                      │
│  DeclarativeAgent.load("agent.yaml") ← Python 只负责加载    │
│     ↓                                                      │
│  Agent instance ← 配置驱动，而非代码驱动                      │
└─────────────────────────────────────────────────────────────┘
```

**心智模型**：Declarative 就像 Kubernetes 的 Pod 配置——你声明"我要一个什么状态的 Pod"，Kubernetes 负责让它变成那样，而不是写步骤让 Kubernetes 执行。

## 推荐做法

### YAML 配置文件

```yaml
# configs/sales-agent.yaml
name: SalesAgent
description: 销售助手，帮助用户选择产品并计算折扣

instructions: |
  你是一个专业的销售助手。

  职责：
  - 了解用户需求，推荐合适的产品
  - 清晰解释产品功能和价格
  - 计算折扣并给出最优方案

  回答风格：
  - 专业但不晦涩
  - 主动询问需求，不强行推销
  - 对于复杂问题，列出选项让用户选择

tools:
  - name: get_product
    description: 根据用户需求查询产品列表
    function: get_product_tool

  - name: calculate_discount
    description: 计算订单折扣
    function: calculate_discount_tool

middleware:
  - type: logging
    config:
      level: info

  - type: result_validator
    config:
      max_length: 2000
```

### DeclarativeAgent 实现

```python
import yaml
from pathlib import Path
from agent_framework import Agent, tool
from agent_framework.agents import FunctionTool

class DeclarativeAgent:
    """从 YAML 配置加载并创建 Agent"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))

        self.name = self.config["name"]
        self.description = self.config.get("description", "")
        self.instructions = self.config["instructions"]
        self.tools = self._load_tools()
        self.middleware = self._load_middleware()

    def _load_tools(self):
        """将 YAML 中的工具配置转换为实际工具"""
        tools = []
        for tool_config in self.config.get("tools", []):
            # 从全局命名空间获取函数
            func = globals().get(tool_config["function"])
            if func:
                tools.append(FunctionTool.from_function(func))
        return tools

    def _load_middleware(self):
        """加载中间件配置"""
        # 简化实现
        return []

    def create_agent(self, client) -> Agent:
        """基于配置创建 Agent 实例"""
        return Agent(
            client=client,
            name=self.name,
            description=self.description,
            instructions=self.instructions,
            tools=self.tools,
            middleware=self.middleware,
        )


# 使用
agent_loader = DeclarativeAgent("configs/sales-agent.yaml")
agent = agent_loader.create_agent(client)
result = await agent.run("我想买一个数据分析工具")
```

### 完整示例

```python
# main.py
from pathlib import Path

def create_agent_from_config(client, config_name: str):
    config_path = Path("configs") / f"{config_name}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    loader = DeclarativeAgent(str(config_path))
    return loader.create_agent(client)


# 使用
sales_agent = create_agent_from_config(client, "sales-agent")
support_agent = create_agent_from_config(client, "support-agent")
analytics_agent = create_agent_from_config(client, "analytics-agent")
```

## 好 vs 坏对比

```python
# 坏做法：配置硬编码在 Python 里
sales_agent = Agent(
    client=client,
    name="SalesAgent",
    instructions="你是销售助手...",
    tools=[get_product, calculate_discount],
)

# 非技术人员想改成"只推荐高价产品" → 要改代码

# 好做法：YAML 配置，配置与代码分离
# configs/sales-agent.yaml
# instructions: | 你是一个销售助手，只推荐高价产品...
agent = DeclarativeAgent("configs/sales-agent.yaml").create_agent(client)

# 非技术人员可以直接改 YAML，无需懂 Python
```

## 扩展讨论

### 多环境配置

```yaml
# configs/sales-agent.yaml
name: SalesAgent
environment_overrides:
  production:
    instructions: |
      你是专业销售助手。生产环境注意事项：
      - 不承诺无法交付的功能
      - 折扣权限有限...
  staging:
    instructions: |
      你是销售助手（测试环境）。
```

```python
import os

def create_agent(client, config_name: str):
    config_path = Path("configs") / f"{config_name}.yaml"
    loader = DeclarativeAgent(str(config_path))

    # 环境变量覆盖
    env = os.getenv("ENV", "development")
    if env == "production" and "production" in loader.config.get("environment_overrides", {}):
        override = loader.config["environment_overrides"]["production"]
        loader.instructions = override.get("instructions", loader.instructions)

    return loader.create_agent(client)
```

### 配置版本化

```bash
# Git 管理配置
configs/
├── sales-agent.yaml       # 当前版本
├── sales-agent.v1.yaml    # 历史版本
└── sales-agent.v2.yaml   # 历史版本
```

```yaml
# configs/sales-agent.yaml
version: "2024-Q1"
last_modified: "2024-01-15"
modified_by: "zhangsan"
changelog:
  - date: "2024-01-15"
    author: "zhangsan"
    change: "新增产品推荐逻辑"
```

### 配置验证

```python
from pydantic import BaseModel, ValidationError

class AgentConfig(BaseModel):
    name: str
    instructions: str
    tools: list[dict] = []

    class Config:
        extra = "allow"

def validate_config(config_path: str) -> bool:
    try:
        config = yaml.safe_load(Path(config_path).read_text())
        AgentConfig(**config)
        return True
    except ValidationError as e:
        print(f"Config validation failed: {e}")
        return False
```

### 企业级考虑

```python
# 1. 配置集中化管理
class ConfigServer:
    def get_agent_config(self, agent_name: str, environment: str) -> dict:
        # 从配置中心（Consul/Etcd）获取配置
        return self.config_store.get(f"agents/{environment}/{agent_name}")

# 2. 配置变更审计
class AuditingDeclarativeAgent(DeclarativeAgent):
    def __init__(self, config_path: str, audit_log: AuditLog):
        super().__init__(config_path)
        self.audit_log = audit_log
        self.audit_log.record(
            action="agent_loaded",
            config_path=config_path,
            timestamp=datetime.now(),
        )

# 3. 配置热更新
async def hot_reload_agent(agent: Agent, config_path: str):
    """不重启服务，更新 Agent 配置"""
    loader = DeclarativeAgent(config_path)
    new_agent = loader.create_agent(agent.client)
    # 替换旧 Agent（需要应用层配合）
    return new_agent
```

## Things to Remember

- Declarative Agent = **YAML 配置 + 代码解析器**，配置与代码分离
- 适合场景：**非技术人员需要调整 Agent 行为**、配置需要版本化管理、多环境切换
- 解析器负责将 YAML 转换为实际的 `Agent` 对象
- YAML 中声明 Instructions、Tools、Middleware，解析器负责实例化
- **不是**用 YAML 直接执行 Agent，而是用 YAML **描述** Agent
- 多环境配置可以用 `environment_overrides` 或配置中心实现
- 生产环境中配置应纳入审计日志，便于追踪变更
- 配置验证（Schema validation）能提前发现配置错误
