# Item 26: Override Results to Inject Custom Responses

Result Override 允许 Middleware 拦截并替换 Agent 的最终响应。这用于实现缓存、 fallback 逻辑、响应改写。

## 覆盖心智模型

```
Agent 生成响应 → Middleware 拦截 → 判断是否覆盖 → 返回自定义结果
```

## 缓存覆盖

```python
class CacheMiddleware(AgentMiddleware):
    def __init__(self, cache_store):
        self.cache = cache_store

    async def process(self, context: AgentContext, call_next):
        cache_key = self._compute_key(context)

        # 命中缓存则直接返回
        if cached := self.cache.get(cache_key):
            return cached

        # 未命中则调用 Agent
        response = await call_next()

        # 存入缓存
        self.cache.set(cache_key, response)
        return response
```

## Fallback 覆盖

```python
class FallbackMiddleware(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        try:
            return await call_next()
        except Exception as e:
            # 调用失败时返回 fallback 响应
            return AgentResponse(
                text="抱歉，服务暂时不可用，请稍后再试。",
                error=str(e)
            )
```

## 条件覆盖

```python
class ConditionalOverride(AgentMiddleware):
    async def process(self, context: AgentContext, call_next):
        response = await call_next()

        if self._should_override(response):
            return self._custom_response(response)

        return response
```

## Things to Remember

- Override 在响应生成后拦截
- 可以完全替换返回值
- 常用于缓存、fallback、监控
- Override 后的响应仍可被后续中间件处理
