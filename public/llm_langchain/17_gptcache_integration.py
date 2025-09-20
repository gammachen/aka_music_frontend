#!/usr/bin/env python3
"""
GPTCache第三方缓存集成
集成GPTCache实现智能LLM缓存，支持语义缓存、自适应缓存和高级缓存策略
"""

import os
import json
import hashlib
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

# GPTCache相关导入
try:
    from gptcache import cache
    from gptcache.adapter import openai
    from gptcache.embedding import OpenAI, SentenceTransformer
    from gptcache.manager import CacheBase, VectorBase, get_data_manager
    from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation
    from gptcache.similarity_evaluation.onnx import OnnxModelEvaluation
    from gptcache.processor.pre import get_prompt
    from gptcache.processor.post import temperature_softmax
    from gptcache.utils.error import CacheError
    HAS_GPTCACHE = True
except ImportError:
    HAS_GPTCACHE = False
    logging.warning("GPTCache未安装，请运行: pip install gptcache")

class CacheStrategy(Enum):
    """缓存策略枚举"""
    EXACT = "exact"
    SEMANTIC = "semantic"
    SIMILARITY = "similarity"
    ADAPTIVE = "adaptive"

@dataclass
class CacheConfig:
    """缓存配置数据类"""
    cache_dir: str = ".cache"
    strategy: CacheStrategy = CacheStrategy.SEMANTIC
    threshold: float = 0.8
    embedding_model: str = "text-embedding-ada-002"
    vector_store: str = "faiss"
    max_size: int = 1000
    ttl: int = 3600
    enable_evaluation: bool = True
    evaluation_model: str = "onnx"

class GPTCacheManager:
    """GPTCache管理器"""
    
    def __init__(self, config: CacheConfig):
        if not HAS_GPTCACHE:
            raise ImportError("GPTCache未安装，请运行: pip install gptcache")
        
        self.config = config
        self.cache_initialized = False
        self._init_cache()
    
    def _init_cache(self):
        """初始化GPTCache"""
        try:
            # 创建缓存目录
            os.makedirs(self.config.cache_dir, exist_ok=True)
            
            # 配置嵌入模型
            if self.config.embedding_model == "text-embedding-ada-002":
                embedding = OpenAI()
            else:
                embedding = SentenceTransformer(self.config.embedding_model)
            
            # 配置数据管理器
            data_manager = get_data_manager(
                CacheBase("sqlite", 
                         sql_url=f"sqlite:///{self.config.cache_dir}/cache.db"),
                VectorBase(self.config.vector_store, 
                          dimension=embedding.dimension)
            )
            
            # 配置相似度评估
            if self.config.evaluation_model == "onnx":
                evaluation = OnnxModelEvaluation()
            else:
                evaluation = SearchDistanceEvaluation()
            
            # 初始化缓存
            cache.init(
                pre_embedding_func=get_prompt,
                embedding_func=embedding.to_embeddings,
                data_manager=data_manager,
                similarity_evaluation=evaluation,
                post_process_messages_func=temperature_softmax
            )
            
            self.cache_initialized = True
            logging.info("GPTCache初始化成功")
            
        except Exception as e:
            logging.error(f"GPTCache初始化失败: {e}")
            raise

class GPTCacheIntegration:
    """GPTCache集成实现"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache_manager = GPTCacheManager(config)
        self.custom_handlers = {}
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_requests": 0,
            "cache_hit_rate": 0.0
        }
    
    def _update_metrics(self, is_hit: bool):
        """更新缓存指标"""
        self.metrics["total_requests"] += 1
        if is_hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1
        
        self.metrics["cache_hit_rate"] = (
            self.metrics["cache_hits"] / self.metrics["total_requests"]
        )
    
    def cache_llm_request(self, 
                         prompt: str,
                         llm_function: Callable,
                         *args,
                         **kwargs) -> Dict[str, Any]:
        """缓存LLM请求"""
        try:
            import gptcache
            
            # 创建缓存键
            cache_key = hashlib.sha256(prompt.encode()).hexdigest()
            
            # 检查缓存
            cached_response = None
            try:
                # 尝试从缓存获取
                cached_response = gptcache.adapter.api.get(prompt)
                if cached_response:
                    self._update_metrics(True)
                    return {
                        "response": cached_response,
                        "cached": True,
                        "cache_key": cache_key,
                        "similarity": 1.0,
                        "metadata": {
                            "prompt": prompt,
                            "cached_at": datetime.now().isoformat()
                        }
                    }
            except CacheError:
                pass
            
            # 调用LLM获取响应
            response = llm_function(prompt, *args, **kwargs)
            
            # 缓存响应
            try:
                gptcache.adapter.api.put(prompt, response)
            except CacheError as e:
                logging.warning(f"缓存存储失败: {e}")
            
            self._update_metrics(False)
            
            return {
                "response": response,
                "cached": False,
                "cache_key": cache_key,
                "similarity": 0.0,
                "metadata": {
                    "prompt": prompt,
                    "generated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logging.error(f"GPTCache请求处理错误: {e}")
            # 回退到直接调用LLM
            response = llm_function(prompt, *args, **kwargs)
            return {
                "response": response,
                "cached": False,
                "cache_key": None,
                "error": str(e)
            }
    
    def batch_cache_requests(self,
                            prompts: List[str],
                            llm_function: Callable,
                            *args,
                            **kwargs) -> List[Dict[str, Any]]:
        """批量缓存LLM请求"""
        results = []
        
        for prompt in prompts:
            result = self.cache_llm_request(prompt, llm_function, *args, **kwargs)
            results.append(result)
        
        return results
    
    def search_similar_queries(self, 
                              query: str,
                              limit: int = 5) -> List[Dict[str, Any]]:
        """搜索相似的查询"""
        try:
            import gptcache
            
            # 获取相似查询
            similar_queries = gptcache.adapter.api.search(query, top_k=limit)
            
            results = []
            for item in similar_queries:
                results.append({
                    "query": item.question,
                    "response": item.answer,
                    "similarity": item.similarity,
                    "metadata": {
                        "cached_at": str(item.create_on) if hasattr(item, 'create_on') else None
                    }
                })
            
            return results
            
        except Exception as e:
            logging.error(f"相似查询搜索错误: {e}")
            return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        try:
            import gptcache
            
            # 获取缓存统计
            cache_info = gptcache.adapter.api.get_cache_status()
            
            return {
                **self.metrics,
                "cache_size": cache_info.get("total_count", 0),
                "cache_memory": cache_info.get("memory_usage", 0),
                "cache_strategy": self.config.strategy.value,
                "threshold": self.config.threshold,
                "embedding_model": self.config.embedding_model,
                "vector_store": self.config.vector_store
            }
            
        except Exception as e:
            logging.error(f"获取缓存统计错误: {e}")
            return self.metrics
    
    def clear_cache(self) -> bool:
        """清空缓存"""
        try:
            import gptcache
            gptcache.adapter.api.clear()
            
            # 重置指标
            self.metrics = {
                "cache_hits": 0,
                "cache_misses": 0,
                "total_requests": 0,
                "cache_hit_rate": 0.0
            }
            
            return True
            
        except Exception as e:
            logging.error(f"清空缓存错误: {e}")
            return False
    
    def delete_by_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        try:
            import gptcache
            
            # 搜索匹配的缓存
            matching_keys = []
            # 这里应该实现基于模式的搜索逻辑
            
            deleted_count = 0
            for key in matching_keys:
                try:
                    gptcache.adapter.api.delete(key)
                    deleted_count += 1
                except:
                    pass
            
            return deleted_count
            
        except Exception as e:
            logging.error(f"按模式删除缓存错误: {e}")
            return 0

class GPTCacheWithCustomHandler:
    """带自定义处理器的GPTCache"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache = GPTCacheIntegration(config)
        self.custom_handlers = {}
    
    def register_handler(self, prompt_type: str, handler: Callable):
        """注册自定义处理器"""
        self.custom_handlers[prompt_type] = handler
    
    def process_with_handler(self, prompt: str, *args, **kwargs) -> Dict[str, Any]:
        """使用自定义处理器处理请求"""
        # 检测prompt类型
        prompt_type = self._detect_prompt_type(prompt)
        
        if prompt_type in self.custom_handlers:
            handler = self.custom_handlers[prompt_type]
            return handler(prompt, *args, **kwargs)
        else:
            # 使用默认缓存处理
            return self.cache.cache_llm_request(prompt, *args, **kwargs)
    
    def _detect_prompt_type(self, prompt: str) -> str:
        """检测prompt类型"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["code", "programming", "python", "javascript"]):
            return "code_generation"
        elif any(word in prompt_lower for word in ["explain", "what is", "how to"]):
            return "explanation"
        elif any(word in prompt_lower for word in ["translate", "translation"]):
            return "translation"
        else:
            return "general"

# 使用示例
if __name__ == "__main__" and HAS_GPTCACHE:
    
    # 模拟LLM函数
    def mock_llm_function(prompt: str, **kwargs):
        """模拟LLM响应"""
        responses = {
            "什么是机器学习": "机器学习是人工智能的一个子领域，专注于开发能够从数据中学习的算法...",
            "如何优化Python代码": "Python代码优化技巧：1) 使用内置函数 2) 避免全局变量 3) 使用列表推导式...",
            "解释量子计算": "量子计算利用量子力学原理进行计算，使用量子比特(qubit)作为基本信息单元..."
        }
        
        # 查找最匹配的响应
        for key, response in responses.items():
            if key in prompt or prompt in key:
                return response
        
        return f"这是关于'{prompt}'的LLM响应"
    
    # 配置GPTCache
    config = CacheConfig(
        cache_dir="./gptcache_data",
        strategy=CacheStrategy.SEMANTIC,
        threshold=0.85,
        embedding_model="text-embedding-ada-002",
        max_size=1000
    )
    
    # 初始化GPTCache集成
    gpt_cache = GPTCacheIntegration(config)
    
    # 测试缓存
    prompts = [
        "什么是机器学习",
        "机器学习是什么",
        "如何优化Python代码性能",
        "Python代码性能优化技巧",
        "解释量子计算原理",
        "量子计算是如何工作的"
    ]
    
    print("=== GPTCache集成测试 ===")
    
    for prompt in prompts:
        result = gpt_cache.cache_llm_request(prompt, mock_llm_function)
        
        print(f"\nPrompt: {prompt}")
        print(f"缓存命中: {result['cached']}")
        print(f"响应: {result['response'][:100]}...")
    
    # 获取统计信息
    stats = gpt_cache.get_cache_stats()
    print(f"\n=== 缓存统计 ===")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 搜索相似查询
    similar_queries = gpt_cache.search_similar_queries("机器学习", limit=3)
    print(f"\n=== 相似查询 ===")
    for query in similar_queries:
        print(f"- {query['query']} (相似度: {query.get('similarity', 0):.3f})")
    
    # 使用自定义处理器
    custom_cache = GPTCacheWithCustomHandler(config)
    
    # 注册自定义处理器
    def code_generation_handler(prompt: str, **kwargs):
        return {
            "response": f"[代码生成] {prompt}",
            "cached": False,
            "handler": "code_generation"
        }
    
    custom_cache.register_handler("code_generation", code_generation_handler)
    
    # 测试自定义处理器
    result = custom_cache.process_with_handler("请生成一个Python排序函数", mock_llm_function)
    print(f"\n=== 自定义处理器测试 ===")
    print(f"结果: {result}")
    
else:
    print("GPTCache未安装，请先安装：")
    print("pip install gptcache")
    print("pip install sentence-transformers")