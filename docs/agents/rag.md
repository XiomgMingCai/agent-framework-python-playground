# Item 12: Implement RAG Pattern with ContextProvider

## 问题

你想让 Agent 基于你的文档回答问题，但 Agent 不知道你的文档内容：

```python
# 你的文档：公司内部报销规则（100 页 PDF）
# Agent：只知道通用知识，不知道你们的报销规则

result = await agent.run("国内出差机票报销标准是什么？")
# Agent: "抱歉，我不知道你公司的具体报销标准..."
```

或者你尝试把整个文档塞进 Instructions：

```python
agent = Agent(
    instructions="""
    # 你的文档内容（100 页 PDF，转成文本 ~50000 tokens）
    第一章 报销规则...
    第二章 差旅标准...
    ...（太长了，context window 装不下）
    """
)
# 问题：token 消耗巨大，大部分用不上
```

## 深入解释

RAG = **Retrieval Augmented Generation**（检索增强生成），核心思想是**按需检索，而非全量加载**：

```
┌─────────────────────────────────────────────────────────────┐
│              全量加载（Inefficient）                           │
├─────────────────────────────────────────────────────────────┤
│  用户问题："机票报销标准"                                     │
│                     ↓                                        │
│  把 50000 tokens 的文档全部塞进 context                      │
│                     ↓                                        │
│  LLM 处理 50000 tokens，99% 无关                            │
│                     ↓                                        │
│  回答 "机票报销标准"                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              RAG（Efficient）                                 │
├─────────────────────────────────────────────────────────────┤
│  用户问题："机票报销标准"                                     │
│                     ↓                                        │
│  检索相关段落（~500 tokens）                                 │
│                     ↓                                        │
│  把 500 tokens 注入 context                                 │
│                     ↓                                        │
│  LLM 处理 500 tokens，精准回答                               │
└─────────────────────────────────────────────────────────────┘
```

**ContextProvider 是实现 RAG 的最佳位置**——它在 `before_run()` 中拦截请求，检索相关文档，注入 context。

**心智模型**：RAG 就像图书馆的**索引系统**——不问读者把整本书都背下来，而是按问题检索相关章节。

## 推荐做法

### 简化版：关键词检索 RAG

```python
from agent_framework import ContextProvider

class SimpleRAGProvider(ContextProvider):
    """基于关键词匹配的简化 RAG 实现"""

    def __init__(self, documents: list[str]):
        super().__init__("simple-rag")
        self.documents = documents

    async def before_run(self, *, agent, session, context, state):
        # 1. 从用户输入提取查询
        query = self._extract_query(context)
        if not query:
            return

        # 2. 检索相关文档（简化：关键词匹配）
        relevant = self._keyword_search(query, top_k=3)
        if not relevant:
            return

        # 3. 注入检索结果到 context
        context.extend_instructions(
            self.source_id,
            f"\n【参考文档】\n{relevant}\n"
        )

    def _extract_query(self, context) -> str:
        """从 context 中提取用户查询"""
        for msg in context.input_messages:
            if hasattr(msg, 'contents'):
                for c in msg.contents:
                    if hasattr(c, 'text') and c.text:
                        return c.text
        return ""

    def _keyword_search(self, query: str, top_k: int) -> str:
        """简化搜索：关键词匹配"""
        query_words = set(query.lower().split())

        scored = []
        for i, doc in enumerate(self.documents):
            doc_words = set(doc.lower().split())
            score = len(query_words & doc_words)
            if score > 0:
                scored.append((score, i, doc))

        scored.sort(reverse=True)
        results = [doc for _, _, doc in scored[:top_k]]
        return "\n---\n".join(results)


# 使用
documents = [
    "国内出差报销标准：机票经济舱实报实销，高铁二等座实报实销...",
    "国外出差报销标准：机票需 VP 审批，住宿参照外事标准...",
    "日常报销标准：单笔 1000 元以下无需审批...",
]

agent = Agent(
    client=client,
    instructions="你是报销助手，基于提供的参考文档回答问题。",
    context_providers=[SimpleRAGProvider(documents)],
)

result = await agent.run("国内出差机票报销标准是什么？")
# Agent 会基于 "国内出差报销标准..." 文档回答
```

### 生产版：向量检索 RAG

```python
from agent_framework import ContextProvider

class VectorRAGProvider(ContextProvider):
    """使用向量相似度搜索的 RAG 实现"""

    def __init__(self, documents: list[str], embeddings_client):
        super().__init__("vector-rag")
        self.documents = documents
        self.embeddings_client = embeddings_client
        self.doc_embeddings = self._index_documents()

    def _index_documents(self):
        """为文档生成向量索引"""
        # 实际使用：Pinecone/Milvus/Chroma 等向量数据库
        return [self.embeddings_client.embed(doc) for doc in self.documents]

    def _search(self, query: str, top_k: int = 3) -> list[tuple[float, int, str]]:
        """向量相似度搜索"""
        query_embedding = self.embeddings_client.embed(query)

        scored = []
        for i, doc_emb in enumerate(self.doc_embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_emb)
            scored.append((similarity, i, self.documents[i]))

        scored.sort(reverse=True)
        return scored[:top_k]

    def _cosine_similarity(self, a: list, b: list) -> float:
        import math
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        return dot / (norm_a * norm_b)

    async def before_run(self, *, agent, session, context, state):
        query = self._extract_query(context)
        if not query:
            return

        results = self._search(query, top_k=3)
        if not results:
            return

        relevant_docs = "\n---\n".join(doc for _, _, doc in results)
        context.extend_instructions(
            self.source_id,
            f"\n【相关文档】\n{relevant_docs}\n"
        )

    def _extract_query(self, context) -> str:
        for msg in context.input_messages:
            if hasattr(msg, 'contents'):
                for c in msg.contents:
                    if hasattr(c, 'text') and c.text:
                        return c.text
        return ""
```

## 好 vs 坏对比

```python
# 坏做法 1：把所有文档塞进 Instructions
agent = Agent(
    instructions="""
    # 50000 tokens 的文档内容...
    """
)
# token 消耗巨大，大部分用不上，context window 溢出

# 坏做法 2：让 Agent 自己"想"答案
result = await agent.run("你公司的报销标准是什么？")
# Agent 瞎编，不知道你公司的具体规则

# 好做法：用 RAG 按需检索
documents = load_your_documents()
agent = Agent(
    instructions="你是报销助手，基于提供的参考文档回答。",
    context_providers=[SimpleRAGProvider(documents)],
)
result = await agent.run("国内出差机票报销标准？")
# Agent 基于检索到的相关段落回答，精准且省 token
```

## 扩展讨论

### RAG vs Skills vs Fine-tuning

| 特性 | RAG | Skills | Fine-tuning |
|------|-----|--------|-------------|
| 知识更新 | 实时（换文档即可）| 需改 Skill 定义 | 需重新训练 |
| token 消耗 | 按需检索 | 按需加载 | 固定（模型权重）|
| 适用场景 | 动态文档/知识库 | 规则/流程/手册 | 风格/领域适应 |
| 准确性 | 依赖检索质量 | 高（精确控制）| 中（依赖训练数据）|
| 延迟 | 增加检索延迟 | 低 | 无（推理时）|

### 检索策略选择

```python
# 1. 关键词检索（BM25）- 简单场景
from rank_bm25 import BM25Ok

class BM25RAGProvider(ContextProvider):
    def __init__(self, documents: list[str]):
        super().__init__("bm25-rag")
        self.documents = documents
        self.bm25 = BM25Ok([doc.split() for doc in documents])

    def search(self, query: str, top_k: int = 3) -> list[str]:
        tokens = query.split()
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [self.documents[i] for i in top_indices]

# 2. 向量检索 - 生产环境
# 使用：Pinecone / Milvus / Weaviate / ChromaDB
```

### 混合检索

```python
class HybridRAGProvider(ContextProvider):
    """关键词 + 向量混合检索"""

    def __init__(self, documents: list[str], embeddings_client):
        super().__init__("hybrid-rag")
        self.documents = documents
        self.embeddings_client = embeddings_client
        self.bm25 = BM25Ok([doc.split() for doc in documents])
        self.doc_embeddings = [embeddings_client.embed(doc) for doc in documents]

    def search(self, query: str, top_k: int = 3) -> list[str]:
        # 关键词得分
        keyword_scores = self.bm25.get_scores(query.split())

        # 向量得分
        query_emb = self.embeddings_client.embed(query)
        vector_scores = [self._cosine_similarity(query_emb, doc_emb)
                        for doc_emb in self.doc_embeddings]

        # 融合
        final_scores = [0.4 * kw + 0.6 * vec for kw, vec in zip(keyword_scores, vector_scores)]

        top_indices = sorted(range(len(final_scores)), key=lambda i: final_scores[i], reverse=True)[:top_k]
        return [self.documents[i] for i in top_indices]
```

### 企业级考虑

```python
# 1. 文档更新时重建索引
class VersionedRAGProvider(ContextProvider):
    def __init__(self, docs_path: str, embeddings_client):
        self.embeddings_client = embeddings_client
        self.docs_path = Path(docs_path)
        self._reindex()

    def _reindex(self):
        """文档变更时重建索引"""
        self.documents = list(self.docs_path.glob("*.txt"))
        self.doc_embeddings = [self.embeddings_client.embed(doc.read_text())
                             for doc in self.documents]

# 2. 查询缓存
class CachedRAGProvider(ContextProvider):
    def __init__(self, documents: list[str]):
        super().__init__("cached-rag")
        self.documents = documents
        self.cache = {}

    def _search(self, query: str) -> str:
        if query in self.cache:
            return self.cache[query]

        result = self._do_search(query)
        self.cache[query] = result
        return result

# 3. 检索结果重排序
class RerankedRAGProvider(ContextProvider):
    def __init__(self, documents: list[str], reranker):
        self.documents = documents
        self.reranker = reranker  # Cross-Encoder 重排序模型

    def search(self, query: str, top_k: int = 10, rerank_top: int = 3):
        # 第一阶段：向量检索出 top_k
        candidates = self._vector_search(query, top_k)

        # 第二阶段：Cross-Encoder 重排序
        reranked = self.reranker.rerank(query, candidates)[:rerank_top]
        return reranked
```

## Things to Remember

- RAG = **检索 + 生成**，不是让 Agent 自己编答案
- **检索在 `before_run()` 中**，按需将相关文档注入 context
- ContextProvider 是实现 RAG 的标准位置
- `context.extend_instructions()` 将检索结果注入
- RAG 适合**动态文档/知识库**，Skills 适合**结构化规则**
- 简化版可用关键词匹配（BM25），生产用向量检索（Pinecone/Milvus）
- 检索质量直接影响生成质量——好的检索策略很重要
- 文档更新时需重建索引，向量数据库支持增量更新
- 混合检索（关键词 + 向量）通常效果更好
- 检索结果需要重排序（Re-ranker）以提升相关性
