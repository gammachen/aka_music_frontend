#!/usr/bin/env python3
"""
语义化缓存实现
基于向量相似度的智能缓存系统，支持语义理解、模糊匹配和智能推荐
"""

import numpy as np
import hashlib
import json
from typing import Any, Optional, Dict, List, Tuple, Union
from datetime import datetime, timedelta
import logging
from abc import ABC, abstractmethod
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from sentence_transformers import SentenceTransformer

class SemanticEncoder(ABC):
    """语义编码器抽象基类"""
    
    @abstractmethod
    def encode(self, text: str) -> np.ndarray:
        """将文本编码为向量"""
        pass
    
    @abstractmethod
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算向量相似度"""
        pass

class TfidfSemanticEncoder(SemanticEncoder):
    """基于TF-IDF的语义编码器"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.is_fitted = False
    
    def fit(self, texts: List[str]):
        """训练TF-IDF模型"""
        if texts:
            self.vectorizer.fit(texts)
            self.is_fitted = True
    
    def encode(self, text: str) -> np.ndarray:
        """编码文本为TF-IDF向量"""
        if not self.is_fitted:
            self.fit([text])
        
        return self.vectorizer.transform([text]).toarray()[0]
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        return float(cosine_similarity([vec1], [vec2])[0][0])

class TransformerSemanticEncoder(SemanticEncoder):
    """基于Transformer的语义编码器"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, text: str) -> np.ndarray:
        """编码文本为语义向量"""
        return self.model.encode([text])[0]
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        return float(cosine_similarity([vec1], [vec2])[0][0])

class OpenAISemanticEncoder(SemanticEncoder):
    """基于OpenAI的语义编码器"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        openai.api_key = api_key
        self.model = model
    
    def encode(self, text: str) -> np.ndarray:
        """编码文本为OpenAI向量"""
        response = openai.Embedding.create(
            input=text,
            model=self.model
        )
        return np.array(response['data'][0]['embedding'])
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        return float(cosine_similarity([vec1], [vec2])[0][0])

class SemanticCache:
    """语义化缓存实现"""
    
    def __init__(self, encoder: SemanticEncoder, threshold: float = 0.85):
        self.encoder = encoder
        self.threshold = threshold
        self.cache = {}
        self.vector_cache = {}
        self.index = []
        self.vectors = []
    
    def _generate_key(self, text: str) -> str:
        """生成语义键"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 清理文本
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s]', '', text.lower())
        return text
    
    def set(self, text: str, value: Any, metadata: Dict = None, 
            ttl: int = 3600) -> bool:
        """设置语义缓存"""
        try:
            processed_text = self._preprocess_text(text)
            cache_key = self._generate_key(processed_text)
            
            # 编码文本向量
            vector = self.encoder.encode(processed_text)
            
            cache_item = {
                "value": value,
                "text": processed_text,
                "vector": vector.tolist(),
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "expire_at": (datetime.now() + timedelta(seconds=ttl)).isoformat(),
                "access_count": 0
            }
            
            # 存储缓存
            self.cache[cache_key] = cache_item
            self.vector_cache[cache_key] = vector
            
            # 更新索引
            if cache_key not in self.index:
                self.index.append(cache_key)
                self.vectors.append(vector)
            
            return True
            
        except Exception as e:
            logging.error(f"语义缓存设置错误: {e}")
            return False
    
    def get(self, text: str, min_similarity: float = None) -> Optional[Dict[str, Any]]:
        """获取语义相似的缓存"""
        try:
            processed_text = self._preprocess_text(text)
            query_vector = self.encoder.encode(processed_text)
            
            threshold = min_similarity or self.threshold
            best_match = None
            best_similarity = 0.0
            
            # 查找最相似的缓存
            for cache_key, cached_vector in self.vector_cache.items():
                similarity = self.encoder.similarity(query_vector, cached_vector)
                
                if similarity >= threshold and similarity > best_similarity:
                    cache_item = self.cache[cache_key]
                    
                    # 检查是否过期
                    expire_at = datetime.fromisoformat(cache_item["expire_at"])
                    if datetime.now() > expire_at:
                        continue
                    
                    best_match = {
                        "value": cache_item["value"],
                        "original_text": cache_item["text"],
                        "similarity": similarity,
                        "metadata": cache_item["metadata"],
                        "access_count": cache_item["access_count"]
                    }
                    best_similarity = similarity
            
            if best_match:
                # 更新访问统计
                cache_key = self._generate_key(best_match["original_text"])
                self.cache[cache_key]["access_count"] += 1
                
            return best_match
            
        except Exception as e:
            logging.error(f"语义缓存获取错误: {e}")
            return None
    
    def search_similar(self, text: str, limit: int = 5, 
                      min_similarity: float = None) -> List[Dict[str, Any]]:
        """搜索语义相似的缓存"""
        try:
            processed_text = self._preprocess_text(text)
            query_vector = self.encoder.encode(processed_text)
            
            threshold = min_similarity or (self.threshold * 0.8)
            matches = []
            
            for cache_key, cached_vector in self.vector_cache.items():
                similarity = self.encoder.similarity(query_vector, cached_vector)
                
                if similarity >= threshold:
                    cache_item = self.cache[cache_key]
                    
                    # 检查是否过期
                    expire_at = datetime.fromisoformat(cache_item["expire_at"])
                    if datetime.now() > expire_at:
                        continue
                    
                    matches.append({
                        "value": cache_item["value"],
                        "original_text": cache_item["text"],
                        "similarity": similarity,
                        "metadata": cache_item["metadata"],
                        "access_count": cache_item["access_count"]
                    })
            
            # 按相似度排序
            matches.sort(key=lambda x: x["similarity"], reverse=True)
            
            return matches[:limit]
            
        except Exception as e:
            logging.error(f"语义搜索错误: {e}")
            return []
    
    def delete(self, text: str) -> bool:
        """删除语义缓存"""
        try:
            processed_text = self._preprocess_text(text)
            cache_key = self._generate_key(processed_text)
            
            if cache_key in self.cache:
                del self.cache[cache_key]
                del self.vector_cache[cache_key]
                
                # 更新索引
                if cache_key in self.index:
                    idx = self.index.index(cache_key)
                    del self.index[idx]
                    del self.vectors[idx]
                
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"语义缓存删除错误: {e}")
            return False
    
    def delete_by_tags(self, tags: List[str]) -> int:
        """按标签删除语义缓存"""
        try:
            deleted_count = 0
            keys_to_delete = []
            
            for cache_key, cache_item in self.cache.items():
                item_tags = cache_item.get("metadata", {}).get("tags", [])
                if any(tag in item_tags for tag in tags):
                    keys_to_delete.append(cache_key)
            
            for cache_key in keys_to_delete:
                self.delete(self.cache[cache_key]["text"])
                deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            logging.error(f"语义标签删除错误: {e}")
            return 0
    
    def clear_expired(self) -> int:
        """清理过期缓存"""
        try:
            now = datetime.now()
            expired_keys = []
            
            for cache_key, cache_item in self.cache.items():
                expire_at = datetime.fromisoformat(cache_item["expire_at"])
                if now > expire_at:
                    expired_keys.append(cache_key)
            
            for cache_key in expired_keys:
                self.delete(self.cache[cache_key]["text"])
            
            return len(expired_keys)
            
        except Exception as e:
            logging.error(f"语义缓存清理错误: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取语义缓存统计"""
        try:
            total_items = len(self.cache)
            
            if total_items == 0:
                return {"total_items": 0}
            
            # 计算统计信息
            access_counts = [item["access_count"] for item in self.cache.values()]
            data_sizes = [len(json.dumps(item["value"], ensure_ascii=False)) 
                         for item in self.cache.values()]
            
            # 标签统计
            tag_counts = {}
            for item in self.cache.values():
                tags = item.get("metadata", {}).get("tags", [])
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # 相似度统计
            similarities = []
            if total_items > 1:
                for i, (key1, vec1) in enumerate(self.vector_cache.items()):
                    for j, (key2, vec2) in enumerate(self.vector_cache.items()):
                        if i < j:
                            sim = self.encoder.similarity(vec1, vec2)
                            similarities.append(sim)
            
            return {
                "total_items": total_items,
                "total_memory_bytes": sum(data_sizes),
                "access_stats": {
                    "total_access": sum(access_counts),
                    "average_access": sum(access_counts) / len(access_counts),
                    "max_access": max(access_counts),
                    "min_access": min(access_counts)
                },
                "size_stats": {
                    "average_size": sum(data_sizes) / len(data_sizes),
                    "max_size": max(data_sizes),
                    "min_size": min(data_sizes)
                },
                "top_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                "similarity_stats": {
                    "average_similarity": sum(similarities) / len(similarities) if similarities else 0,
                    "max_similarity": max(similarities) if similarities else 0,
                    "min_similarity": min(similarities) if similarities else 0
                }
            }
            
        except Exception as e:
            logging.error(f"语义统计错误: {e}")
            return {}

class SemanticCacheWithPersistence:
    """带持久化的语义缓存"""
    
    def __init__(self, encoder: SemanticEncoder, storage_backend: Any, 
                 threshold: float = 0.85):
        self.semantic_cache = SemanticCache(encoder, threshold)
        self.storage = storage_backend
        self.load_from_storage()
    
    def load_from_storage(self):
        """从存储加载缓存"""
        try:
            # 这里应该实现从存储后端加载缓存的逻辑
            # 例如从Redis、MongoDB或文件系统加载
            pass
        except Exception as e:
            logging.error(f"加载缓存错误: {e}")
    
    def save_to_storage(self):
        """保存缓存到存储"""
        try:
            # 这里应该实现保存缓存到存储后端的逻辑
            pass
        except Exception as e:
            logging.error(f"保存缓存错误: {e}")
    
    def set(self, text: str, value: Any, **kwargs) -> bool:
        """设置缓存并持久化"""
        result = self.semantic_cache.set(text, value, **kwargs)
        if result:
            self.save_to_storage()
        return result
    
    def get(self, text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """获取缓存"""
        return self.semantic_cache.get(text, **kwargs)

# 使用示例
if __name__ == "__main__":
    # 使用TF-IDF编码器
    tfidf_encoder = TfidfSemanticEncoder()
    semantic_cache = SemanticCache(tfidf_encoder, threshold=0.8)
    
    # 设置缓存
    semantic_cache.set(
        "用户想了解如何优化Python代码性能",
        {
            "response": "Python性能优化建议：1) 使用内置数据结构 2) 避免全局变量 3) 使用列表推导式",
            "code_examples": [
                "# 使用内置函数\nsum(range(1000))",
                "# 列表推导式\nsquares = [x**2 for x in range(10)]"
            ]
        },
        tags=["python", "performance", "optimization"],
        ttl=7200
    )
    
    semantic_cache.set(
        "Python性能调优技巧和方法",
        {
            "response": "Python性能调优技巧：1) 使用Cython 2) 多进程处理 3) 内存优化",
            "code_examples": [
                "# 使用multiprocessing\nfrom multiprocessing import Pool",
                "# 内存优化\nimport gc\ngc.collect()"
            ]
        },
        tags=["python", "performance", "optimization"],
        ttl=7200
    )
    
    # 语义查询
    query = "如何提升Python程序运行速度"
    result = semantic_cache.get(query)
    
    if result:
        print(f"找到语义相似的结果：")
        print(f"原始文本: {result['original_text']}")
        print(f"相似度: {result['similarity']:.3f}")
        print(f"响应: {json.dumps(result['value'], ensure_ascii=False, indent=2)}")
    else:
        print("未找到语义相似的缓存")
    
    # 搜索相似结果
    similar_results = semantic_cache.search_similar(query, limit=3)
    print(f"\n搜索到 {len(similar_results)} 个相似结果:")
    for i, result in enumerate(similar_results, 1):
        print(f"{i}. 相似度: {result['similarity']:.3f}")
        print(f"   文本: {result['original_text']}")
    
    # 统计信息
    stats = semantic_cache.get_stats()
    print(f"\n语义缓存统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 使用Transformer编码器（需要安装sentence-transformers）
    try:
        transformer_encoder = TransformerSemanticEncoder("all-MiniLM-L6-v2")
        transformer_cache = SemanticCache(transformer_encoder, threshold=0.85)
        
        transformer_cache.set(
            "Explain quantum computing in simple terms",
            {
                "response": "Quantum computing uses quantum bits (qubits) that can exist in multiple states simultaneously...",
                "difficulty": "beginner",
                "category": "physics"
            }
        )
        
        result = transformer_cache.get("What is quantum computing for beginners")
        if result:
            print(f"\nTransformer语义匹配成功！相似度: {result['similarity']:.3f}")
            
    except ImportError:
        print("\n注意：需要安装sentence-transformers库来使用Transformer编码器")
        print("pip install sentence-transformers")