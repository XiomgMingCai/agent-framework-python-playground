# Item 27: Handle Exceptions in Middleware Without Swallowing Them

Middleware 的异常处理需要在**隔离**和**传播**之间取得平衡：记录错误但不让它们静默消失。

## 异常处理心智模型

```
异常发生 → Middleware 捕获 → 记录/转换 → 决定传播/处理
```

## 正确模式

```python
class ErrorHandlingMiddleware(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        try:
            return await call_next()
        except RetryableError as e:
            # 可重试错误：记录并重试
            logger.warning(f"Retryable error: {e}")
            raise  # 重新抛出让上层处理
        except FatalError as e:
            # 致命错误：记录并转换
            logger.error(f"Fatal error: {e}")
            return AgentResponse(error=str(e))
        except Exception as e:
            # 未知错误：记录、上报、转换
            logger.exception("Unexpected error")
            metrics.increment("errors")
            return AgentResponse(error="内部错误")
```

## 不要这样做

```python
# 反模式：静默吞噬异常
class BadMiddleware(AgentMiddleware):
    async def process(self, context, call_next):
        try:
            await call_next()
        except:
            pass  # 错误消失了！
```

## 异常转换

```python
class ExceptionTransformingMiddleware(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        try:
            return await call_next()
        except APIError as e:
            # 转换为用户友好的响应
            return AgentResponse(
                text=f"API 调用失败: {e.message}",
                error_code=e.code
            )
```

## Things to Remember

- 记录所有异常（logger.exception）
- 可重试错误重新抛出
- 致命错误转换为友好响应
- 未知错误上报指标后转换
- 永远不要静默吞噬异常
