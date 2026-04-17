# 工具调用

让 Agent 具备调用外部函数的能力，扩展 AI 的实际执行能力。

## 前置知识

- 已完成[环境配置](index.md)
- 了解 Python 装饰器与类型注解

## 核心概念

```
User Input → Agent → 判断是否需要工具
                         ↓
                    调用工具函数
                         ↓
                    工具返回结果
                         ↓
                    Agent 整合结果 → 最终回复
```

## 示例代码

**文件：** `examples/tool_use/main.py`

```python
import asyncio
import os
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

from agent_framework import Agent, tool
from agent_framework.openai import OpenAIChatCompletionClient


# ── 工具定义 ──────────────────────────────────────────────

@tool
def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """
    获取指定时区的当前时间。

    Args:
        timezone: 时区名称，例如 Asia/Shanghai、UTC、America/New_York

    Returns:
        格式化的当前时间字符串
    """
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.strftime(f"%Y-%m-%d %H:%M:%S ({timezone})")
    except Exception as e:
        return f"错误：无效的时区 '{timezone}'，原因：{e}"


@tool
def calculate(expression: str) -> str:
    """
    计算数学表达式。

    Args:
        expression: 数学表达式字符串，例如 "2 + 3 * 4"

    Returns:
        计算结果字符串
    """
    import re
    if not re.match(r'^[\d\s\+\-\*\/\.\(\)]+$', expression):
        return f"错误：表达式包含非法字符：{expression}"
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算失败：{e}"


@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息（模拟数据）。

    Args:
        city: 城市名称，例如 北京、上海、Tokyo

    Returns:
        天气信息字符串
    """
    mock_data = {
        "北京":  "晴，18°C，东风 3 级，湿度 40%",
        "上海":  "多云，22°C，东南风 2 级，湿度 65%",
        "广州":  "阵雨，26°C，南风 4 级，湿度 80%",
        "东京":  "Cloudy, 20°C, NE wind, Humidity 55%",
        "tokyo": "Cloudy, 20°C, NE wind, Humidity 55%",
    }
    key = city.strip().lower()
    return mock_data.get(city, mock_data.get(key, f"{city}：暂无天气数据"))


# ── Agent 运行 ────────────────────────────────────────────

async def main(prompt: str):
    load_dotenv()

    api_key  = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model    = os.getenv("AI_MODEL")

    if not all([api_key, base_url, model]):
        raise ValueError("请在 .env 中配置 AI_API_KEY、AI_BASE_URL、AI_MODEL")

    client = OpenAIChatCompletionClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    agent = Agent(
        client=client,
        name="ToolAgent",
        instructions=(
            "你是一个实用助手，拥有以下工具：\n"
            "- get_current_time：查询时区时间\n"
            "- calculate：计算数学表达式\n"
            "- get_weather：查询城市天气\n"
            "根据用户问题自动选择合适的工具。"
        ),
        tools=[get_current_time, calculate, get_weather],
    )

    print(f"User : {prompt}")
    print("Agent: ", end="", flush=True)

    stream = await agent.run(prompt, stream=True)
    async for update in stream:
        if update.contents:
            for content in update.contents:
                if content.text:
                    print(content.text, end="", flush=True)

    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", type=str, required=True)
    args = parser.parse_args()
    asyncio.run(main(args.prompt))
```

## 运行示例

```bash
# 查询时间
uv run examples/tool_use/main.py -p "现在北京时间是几点？"

# 数学计算
uv run examples/tool_use/main.py -p "计算 (128 + 256) * 3.14"

# 天气查询
uv run examples/tool_use/main.py -p "上海今天天气怎么样？"

# 组合调用
uv run examples/tool_use/main.py -p "现在几点了？上海天气如何？顺便算一下 99 * 99"
```

## 预期输出

```
User : 现在北京时间是几点？
Agent: 当前北京时间是 2025-01-15 14:30:22 (Asia/Shanghai)

User : 计算 (128 + 256) * 3.14
Agent: (128 + 256) * 3.14 = 1205.76

User : 上海今天天气怎么样？
Agent: 上海当前天气：多云，22°C，东南风 2 级，湿度 65%
```

## 核心要点

| 组件 | 说明 |
|------|------|
| `@tool` | 装饰器，将普通函数注册为 Agent 可调用工具 |
| `Docstring` | Agent 通过 docstring 理解工具用途，**必须清晰描述** |
| `tools=[...]` | 在 `Agent` 构造时注入工具列表 |
| `Args 类型注解` | 帮助 Agent 正确传入参数，建议始终添加 |

## 工具编写规范

```python
@tool
def my_tool(param1: str, param2: int = 0) -> str:
    """
    工具的简短描述（Agent 依赖此描述决定是否调用）

    Args:
        param1: 参数1的说明
        param2: 参数2的说明，默认值为 0

    Returns:
        返回值说明
    """
    # 工具实现
    return "result"
```

!!! warning "规范要点"
    1. **Docstring 必须清晰** — Agent 读取 docstring 判断工具用途
    2. **参数类型注解** — 帮助 Agent 生成正确的参数
    3. **返回值为字符串** — Agent 将返回值作为文本上下文处理
    4. **做好异常处理** — 工具内部捕获异常，返回错误描述而非抛出

## 工具调用流程详解

```
1. User: "上海天气如何？"
        ↓
2. Agent 分析 prompt，匹配工具描述
        ↓
3. Agent 生成工具调用：get_weather(city="上海")
        ↓
4. Framework 执行工具函数，获取返回值
        ↓
5. 返回值注入 Agent 上下文
        ↓
6. Agent 生成最终自然语言回复
```
