#!/usr/bin/env python3
"""
LangChain RAG检索器生产级实现
包含多种检索器类型、优化策略和实际应用示例
"""

import os
import json
import time
import hashlib
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# 模拟LangChain组件
class MockDocument:
    """模拟Document类"""
    def __init__(self, page_content: str, metadata: Optional[Dict] = None):
        self.page_content = page_content
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"MockDocument(content='{self.page_content[:50]}...', metadata={self.metadata})"

class MockEmbeddings:
    """模拟嵌入模型"""
    def __init__(self, model: str = "mock-embedding"):
        self.model = model
    
    def embed_query(self, text: str) -> List[float]:
        """生成查询向量（模拟）"""
        # 使用简单的哈希生成模拟向量
        hash_obj = hashlib.md5(text.encode())
        vector = [int(b) / 255.0 for b in hash_obj.digest()]
        return vector
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成文档向量（模拟）"""
        return [self.embed_query(text) for text in texts]

class MockVectorStore:
    """模拟向量存储"""
    def __init__(self):
        self.documents = []
        self.vectors = []
        self.metadata = []
    
    def add_documents(self, documents: List[MockDocument]) -> List[str]:
        """添加文档到向量存储"""
        ids = []
        for doc in documents:
            doc_id = hashlib.md5(doc.page_content.encode()).hexdigest()
            vector = MockEmbeddings().embed_query(doc.page_content)
            
            self.documents.append(doc)
            self.vectors.append(vector)
            self.metadata.append(doc.metadata)
            ids.append(doc_id)
        return ids
    
    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = 4,
        **kwargs
    ) -> List[Tuple[MockDocument, float]]:
        """相似度搜索"""
        query_vector = MockEmbeddings().embed_query(query)
        
        # 计算余弦相似度
        scores = []
        for i, doc_vector in enumerate(self.vectors):
            similarity = np.dot(query_vector, doc_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(doc_vector)
            )
            scores.append((i, similarity))
        
        # 排序并返回前k个
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in scores[:k]:
            results.append((self.documents[idx], score))
        
        return results
    
    def similarity_search(self, query: str, k: int = 4) -> List[MockDocument]:
        """相似度搜索（无分数）"""
        results = self.similarity_search_with_score(query, k)
        return [doc for doc, _ in results]
    
    def count(self) -> int:
        """获取文档数量"""
        return len(self.documents)

@dataclass
class RetrievalConfig:
    """检索器配置"""
    top_k: int = 5
    score_threshold: float = 0.7
    chunk_size: int = 1000
    chunk_overlap: int = 200
    cache_ttl: int = 3600
    enable_compression: bool = True
    enable_reranking: bool = True
    batch_size: int = 100

class BaseRetriever:
    """基础检索器类"""
    
    def __init__(self, config: RetrievalConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def get_relevant_documents(self, query: str) -> List[MockDocument]:
        """获取相关文档"""
        raise NotImplementedError
    
    def log_retrieval(self, query: str, results: List[MockDocument], duration: float):
        """记录检索日志"""
        self.logger.info(
            f"Query: {query[:50]}... | Results: {len(results)} | Duration: {duration:.3f}s"
        )

class VectorStoreRetriever(BaseRetriever):
    """向量存储检索器"""
    
    def __init__(self, vectorstore: MockVectorStore, config: RetrievalConfig):
        super().__init__(config)
        self.vectorstore = vectorstore
    
    def get_relevant_documents(self, query: str) -> List[MockDocument]:
        """从向量存储检索相关文档"""
        start_time = time.time()
        
        # 执行相似度搜索
        results = self.vectorstore.similarity_search(
            query=query,
            k=self.config.top_k
        )
        
        duration = time.time() - start_time
        self.log_retrieval(query, results, duration)
        
        return results

class BM25Retriever(BaseRetriever):
    """BM25稀疏检索器"""
    
    def __init__(self, documents: List[MockDocument], config: RetrievalConfig):
        super().__init__(config)
        self.documents = documents
        self.inverted_index = self._build_inverted_index()
    
    def _build_inverted_index(self) -> Dict[str, List[int]]:
        """构建倒排索引"""
        inverted_index = {}
        
        for idx, doc in enumerate(self.documents):
            words = doc.page_content.lower().split()
            for word in set(words):
                if word not in inverted_index:
                    inverted_index[word] = []
                inverted_index[word].append(idx)
        
        return inverted_index
    
    def _calculate_bm25_score(self, query: str, doc_idx: int) -> float:
        """计算BM25分数"""
        query_terms = query.lower().split()
        doc = self.documents[doc_idx]
        doc_terms = doc.page_content.lower().split()
        
        score = 0.0
        doc_length = len(doc_terms)
        avg_doc_length = sum(len(d.page_content.split()) for d in self.documents) / len(self.documents)
        
        k1 = 1.5
        b = 0.75
        
        for term in query_terms:
            if term in doc_terms:
                tf = doc_terms.count(term)
                df = len(self.inverted_index.get(term, []))
                idf = np.log((len(self.documents) - df + 0.5) / (df + 0.5))
                
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * doc_length / avg_doc_length)
                score += idf * (numerator / denominator)
        
        return score
    
    def get_relevant_documents(self, query: str) -> List[MockDocument]:
        """BM25检索"""
        start_time = time.time()
        
        # 获取候选文档
        candidate_indices = set()
        query_terms = query.lower().split()
        
        for term in query_terms:
            if term in self.inverted_index:
                candidate_indices.update(self.inverted_index[term])
        
        # 计算BM25分数
        scores = []
        for idx in candidate_indices:
            score = self._calculate_bm25_score(query, idx)
            scores.append((idx, score))
        
        # 排序并返回前k个
        scores.sort(key=lambda x: x[1], reverse=True)
        results = [self.documents[idx] for idx, _ in scores[:self.config.top_k]]
        
        duration = time.time() - start_time
        self.log_retrieval(query, results, duration)
        
        return results

class EnsembleRetriever(BaseRetriever):
    """集成检索器（混合检索）"""
    
    def __init__(self, retrievers: List[BaseRetriever], weights: List[float], config: RetrievalConfig):
        super().__init__(config)
        self.retrievers = retrievers
        self.weights = weights
    
    def _reciprocal_rank_fusion(self, results_list: List[List[MockDocument]], k: int = 60) -> List[MockDocument]:
        """倒数排名融合"""
        scores = {}
        
        for retriever_idx, results in enumerate(results_list):
            weight = self.weights[retriever_idx]
            
            for rank, doc in enumerate(results, 1):
                doc_key = doc.page_content
                if doc_key not in scores:
                    scores[doc_key] = {"doc": doc, "score": 0.0}
                
                # 倒数排名融合公式
                rrf_score = weight / (k + rank)
                scores[doc_key]["score"] += rrf_score
        
        # 排序并返回
        sorted_results = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return [item["doc"] for item in sorted_results[:self.config.top_k]]
    
    def get_relevant_documents(self, query: str) -> List[MockDocument]:
        """集成检索"""
        start_time = time.time()
        
        # 并行执行多个检索器
        all_results = []
        for retriever in self.retrievers:
            results = retriever.get_relevant_documents(query)
            all_results.append(results)
        
        # 融合结果
        final_results = self._reciprocal_rank_fusion(all_results)
        
        duration = time.time() - start_time
        self.log_retrieval(query, final_results, duration)
        
        return final_results

class ContextualCompressionRetriever(BaseRetriever):
    """上下文压缩检索器"""
    
    def __init__(self, base_retriever: BaseRetriever, config: RetrievalConfig):
        super().__init__(config)
        self.base_retriever = base_retriever
    
    def _compress_document(self, doc: MockDocument, query: str) -> MockDocument:
        """压缩文档内容"""
        content = doc.page_content
        
        # 简单的压缩逻辑：提取包含查询关键词的句子
        sentences = content.replace('。', '.').split('.')
        query_terms = query.lower().split()
        
        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in query_terms):
                relevant_sentences.append(sentence.strip())
        
        compressed_content = '. '.join(relevant_sentences[:3])  # 限制句子数量
        
        return MockDocument(
            page_content=compressed_content,
            metadata={**doc.metadata, "compressed": True}
        )
    
    def get_relevant_documents(self, query: str) -> List[MockDocument]:
        """压缩检索"""
        start_time = time.time()
        
        # 基础检索
        base_results = self.base_retriever.get_relevant_documents(query)
        
        # 压缩结果
        compressed_results = [
            self._compress_document(doc, query) 
            for doc in base_results
        ]
        
        duration = time.time() - start_time
        self.log_retrieval(query, compressed_results, duration)
        
        return compressed_results

class MultiQueryRetriever(BaseRetriever):
    """多查询扩展检索器"""
    
    def __init__(self, base_retriever: BaseRetriever, config: RetrievalConfig):
        super().__init__(config)
        self.base_retriever = base_retriever
    
    def _generate_variations(self, query: str) -> List[str]:
        """生成查询变体"""
        variations = [query]  # 包含原始查询
        
        # 简单的查询扩展
        keywords = query.split()
        
        # 添加同义词
        synonym_map = {
            "机器学习": ["ML", "人工智能"],
            "深度学习": ["DL", "神经网络"],
            "框架": ["工具", "库", "平台"]
        }
        
        for original, synonyms in synonym_map.items():
            if original in query:
                for synonym in synonyms:
                    variations.append(query.replace(original, synonym))
        
        return variations[:3]  # 限制变体数量
    
    def get_relevant_documents(self, query: str) -> List[MockDocument]:
        """多查询检索"""
        start_time = time.time()
        
        # 生成查询变体
        variations = self._generate_variations(query)
        
        # 并行执行所有查询
        all_results = []
        for variation in variations:
            results = self.base_retriever.get_relevant_documents(variation)
            all_results.extend(results)
        
        # 去重
        seen = set()
        unique_results = []
        for doc in all_results:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_results.append(doc)
        
        duration = time.time() - start_time
        self.log_retrieval(query, unique_results, duration)
        
        return unique_results[:self.config.top_k]

class CachedRetriever(BaseRetriever):
    """缓存检索器包装器"""
    
    def __init__(self, base_retriever: BaseRetriever, cache_ttl: int = 3600):
        super().__init__(RetrievalConfig())
        self.base_retriever = base_retriever
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.stats = {"hits": 0, "misses": 0}
    
    def _get_cache_key(self, query: str) -> str:
        """生成缓存键"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """检查缓存是否有效"""
        return time.time() - timestamp < self.cache_ttl
    
    def get_relevant_documents(self, query: str) -> List[MockDocument]:
        """带缓存的检索"""
        cache_key = self._get_cache_key(query)
        
        # 检查缓存
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                self.stats["hits"] += 1
                return cached_result
        
        # 执行检索
        results = self.base_retriever.get_relevant_documents(query)
        
        # 缓存结果
        self.cache[cache_key] = (results, time.time())
        self.stats["misses"] += 1
        
        return results
    
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        return self.stats.copy()

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            "total_queries": 0,
            "total_time": 0.0,
            "error_count": 0,
            "query_times": []
        }
    
    def record_query(self, duration: float, error: bool = False):
        """记录查询指标"""
        self.metrics["total_queries"] += 1
        self.metrics["total_time"] += duration
        self.metrics["query_times"].append(duration)
        
        if error:
            self.metrics["error_count"] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if self.metrics["total_queries"] == 0:
            return {"message": "No queries recorded"}
        
        times = self.metrics["query_times"]
        return {
            "total_queries": self.metrics["total_queries"],
            "total_time": self.metrics["total_time"],
            "average_time": self.metrics["total_time"] / self.metrics["total_queries"],
            "median_time": np.median(times),
            "p95_time": np.percentile(times, 95),
            "error_rate": self.metrics["error_count"] / self.metrics["total_queries"]
        }

class ProductionRAGSystem:
    """生产级RAG系统"""
    
    def __init__(self, config: RetrievalConfig):
        self.config = config
        self.vectorstore = MockVectorStore()
        self.monitor = PerformanceMonitor()
        self.setup_retrievers()
    
    def setup_retrievers(self):
        """设置检索器链"""
        # 基础向量检索器
        self.vector_retriever = VectorStoreRetriever(self.vectorstore, self.config)
        
        # BM25检索器
        self.bm25_retriever = None  # 将在添加文档后初始化
        
        # 集成检索器
        self.ensemble_retriever = None
        
        # 压缩检索器
        self.compression_retriever = ContextualCompressionRetriever(
            self.vector_retriever, self.config
        )
        
        # 多查询检索器
        self.multi_query_retriever = MultiQueryRetriever(
            self.vector_retriever, self.config
        )
        
        # 缓存包装器
        self.cached_retriever = CachedRetriever(self.vector_retriever)
    
    def add_documents(self, documents: List[MockDocument]) -> None:
        """添加文档到系统"""
        print(f"正在索引 {len(documents)} 个文档...")
        
        # 添加到向量存储
        self.vectorstore.add_documents(documents)
        
        # 初始化BM25检索器
        self.bm25_retriever = BM25Retriever(documents, self.config)
        
        # 设置集成检索器
        self.ensemble_retriever = EnsembleRetriever(
            [self.vector_retriever, self.bm25_retriever],
            weights=[0.7, 0.3],
            config=self.config
        )
        
        print("文档索引完成")
    
    def search(self, query: str, retriever_type: str = "vector") -> List[MockDocument]:
        """执行搜索"""
        start_time = time.time()
        
        try:
            # 选择检索器
            retriever_map = {
                "vector": self.vector_retriever,
                "bm25": self.bm25_retriever,
                "ensemble": self.ensemble_retriever,
                "compression": self.compression_retriever,
                "multi": self.multi_query_retriever,
                "cached": self.cached_retriever
            }
            
            retriever = retriever_map.get(retriever_type, self.vector_retriever)
            
            if retriever is None:
                raise ValueError(f"未知的检索器类型: {retriever_type}")
            
            # 执行检索
            results = retriever.get_relevant_documents(query)
            
            duration = time.time() - start_time
            self.monitor.record_query(duration)
            
            return results
            
        except Exception as e:
            duration = time.time() - start_time
            self.monitor.record_query(duration, error=True)
            raise e
    
    async def search_async(self, query: str, retriever_type: str = "vector") -> List[MockDocument]:
        """异步搜索"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.search, query, retriever_type)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        return {
            "document_count": self.vectorstore.count(),
            "performance_stats": self.monitor.get_performance_stats(),
            "cache_stats": self.cached_retriever.get_cache_stats() if hasattr(self, 'cached_retriever') else None,
            "config": asdict(self.config)
        }

# 示例文档
SAMPLE_DOCUMENTS = [
    MockDocument(
        page_content="LangChain是一个用于构建基于大语言模型应用的框架，提供了标准化接口和丰富的工具链。",
        metadata={"source": "tech_doc", "category": "framework", "date": "2024-01-15"}
    ),
    MockDocument(
        page_content="RAG（Retrieval-Augmented Generation）通过检索外部知识来增强大语言模型的能力，减少幻觉问题。",
        metadata={"source": "tech_doc", "category": "rag", "date": "2024-01-16"}
    ),
    MockDocument(
        page_content="向量数据库如Chroma、Pinecone和Weaviate为RAG系统提供了高效的相似度搜索能力。",
        metadata={"source": "tech_doc", "category": "vector_db", "date": "2024-01-17"}
    ),
    MockDocument(
        page_content="嵌入模型将文本转换为向量表示，使得计算机能够理解和计算文本之间的相似度。",
        metadata={"source": "tech_doc", "category": "embeddings", "date": "2024-01-18"}
    ),
    MockDocument(
        page_content="BM25是一种基于概率排序函数的检索算法，广泛应用于搜索引擎和文档检索系统。",
        metadata={"source": "tech_doc", "category": "retrieval", "date": "2024-01-19"}
    )
]

def demonstrate_retrievers():
    """演示各种检索器功能"""
    print("🚀 LangChain RAG检索器演示")
    print("=" * 50)
    
    # 初始化系统
    config = RetrievalConfig(top_k=3)
    rag_system = ProductionRAGSystem(config)
    
    # 添加示例文档
    rag_system.add_documents(SAMPLE_DOCUMENTS)
    
    # 测试查询
    test_queries = [
        "什么是LangChain？",
        "RAG系统如何工作？",
        "向量数据库有哪些？",
        "嵌入模型的作用是什么？",
        "BM25算法的原理"
    ]
    
    retriever_types = ["vector", "bm25", "compression", "multi", "cached"]
    
    for query in test_queries:
        print(f"\n📋 查询: {query}")
        print("-" * 30)
        
        for retriever_type in retriever_types:
            try:
                results = rag_system.search(query, retriever_type)
                print(f"  {retriever_type.upper()}: {len(results)}个结果")
                for i, doc in enumerate(results[:2], 1):
                    print(f"    {i}. {doc.page_content[:60]}...")
            except Exception as e:
                print(f"  {retriever_type.upper()}: 错误 - {str(e)}")
    
    # 性能测试
    print(f"\n📊 系统统计")
    print("-" * 30)
    stats = rag_system.get_system_stats()
    print(f"文档总数: {stats['document_count']}")
    print(f"性能统计: {stats['performance_stats']}")
    print(f"缓存统计: {stats['cache_stats']}")

def benchmark_retrievers():
    """检索器性能基准测试"""
    print("\n⚡ 性能基准测试")
    print("=" * 50)
    
    config = RetrievalConfig(top_k=5)
    rag_system = ProductionRAGSystem(config)
    rag_system.add_documents(SAMPLE_DOCUMENTS)
    
    test_query = "RAG系统的工作原理是什么？"
    iterations = 100
    
    retriever_types = ["vector", "bm25", "compression", "multi", "cached"]
    
    for retriever_type in retriever_types:
        times = []
        
        for _ in range(iterations):
            start = time.time()
            rag_system.search(test_query, retriever_type)
            times.append(time.time() - start)
        
        avg_time = np.mean(times)
        p95_time = np.percentile(times, 95)
        
        print(f"{retriever_type.upper()}:")
        print(f"  平均时间: {avg_time:.4f}s")
        print(f"  P95时间: {p95_time:.4f}s")

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    print("使用模拟实现，无需外部依赖")
    print("=" * 50)
    
    # 运行演示
    demonstrate_retrievers()
    
    # 运行基准测试
    benchmark_retrievers()
    
    # 保存结果
    with open("rag_retrievers_demo_results.json", "w", encoding="utf-8") as f:
        config = RetrievalConfig()
        rag_system = ProductionRAGSystem(config)
        rag_system.add_documents(SAMPLE_DOCUMENTS)
        
        test_queries = [
            "RAG系统的工作原理是什么？",
            "如何提高检索准确性？",
            "向量数据库与传统数据库的区别？",
            "LangChain中的检索器类型有哪些？",
            "上下文压缩检索器的优势是什么？"
        ]
        
        results = {
            "system_stats": rag_system.get_system_stats(),
            "sample_queries": test_queries,
            "retriever_types": ["vector", "bm25", "compression", "multi", "cached"],
            "config": asdict(config)
        }
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 演示完成！结果已保存到 rag_retrievers_demo_results.json")