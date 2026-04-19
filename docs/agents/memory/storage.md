# Item 20: Choose the Right Storage Backend for Your Memory

Memory 的存储后端决定了检索性能和功能。向量数据库适合语义搜索，键值存储适合快速精确查找。

## 存储后端对比

| 后端 | 延迟 | 检索方式 | 适用场景 |
|------|------|----------|----------|
| **InMemory** | 最低 | 精确匹配 | 开发测试 |
| **FileStorage** | 低 | 关键词搜索 | 小规模数据 |
| **VectorStore** | 中 | 语义相似度 | 生产环境 |
| **Redis** | 最低 | 混合检索 | 高并发场景 |

## 基础用法

```python
from agent_framework.memory import Memory, InMemoryStorage

memory = Memory(storage=InMemoryStorage())
```

## 生产环境配置

```python
from agent_framework.memory import Memory
from agent_framework.memory.backends import PineconeStorage, RedisStorage

# Pinecone 向量存储
pinecone_storage = PineconeStorage(
    api_key=os.getenv("PINECONE_API_KEY"),
    index="agent-memory",
    dimension=1536,
)

memory = Memory(storage=pinecone_storage)
```

## 混合存储

```python
from agent_framework.memory import Memory, HybridStorage

storage = HybridStorage(
    vector_store=VectorStorage(),
    kv_store=RedisStorage(),
)

memory = Memory(storage=storage)
```

## Things to Remember

- 开发环境用 InMemory，生产用向量数据库
- 向量存储适合语义检索
- Redis 适合高并发低延迟场景
- 混合存储兼顾精确和语义检索
