# Item 3: Write Tool Docstrings Like You're Explaining to a New Colleague

@tool 装饰器让普通函数变成 Agent 可调用的工具。但 Agent 看不见函数内部——它只靠 docstring 决定什么时候调用、传什么参数。

## 问题

```python
# Agent 不知道 tz 是什么格式
@tool
def get_time(tz):
    """获取时间"""
    ...
```

## 解决方案

```python
@tool
def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """
    获取指定时区的当前时间。

    Args:
        timezone: 时区名称，例如 Asia/Shanghai、UTC、America/New_York

    Returns:
        格式化的当前时间字符串，例如 "2025-01-15 14:30:22 (Asia/Shanghai)"
    """
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    return now.strftime(f"%Y-%m-%d %H:%M:%S ({timezone})")
```

## 工具编写规范

| 要素 | 要求 | 原因 |
|------|------|------|
| 参数类型注解 | 必须加 | Agent 靠这个生成调用参数 |
| Docstring | 清晰描述 | Agent 靠这个决定是否调用 |
| 返回值说明 | 必须加 | Agent 把返回值当上下文 |
| 异常处理 | 内部捕获 | 工具异常会导致整个调用失败 |

## 注册工具

```python
agent = Agent(
    client=client,
    name="ToolAgent",
    instructions="你是一个实用助手，拥有时间查询、计算、天气查询工具。",
    tools=[get_current_time, calculate, get_weather],
)
```

## Things to Remember

- Docstring 是 Agent 的眼睛，写不清楚 Agent 就会乱调用
- 参数类型注解必须加
- 返回值是字符串，会被注入为 Agent 的上下文
- 工具内部做好异常处理，返回错误描述而非抛出
