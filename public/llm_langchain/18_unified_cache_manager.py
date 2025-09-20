#!/usr/bin/env python3
"""
统一缓存管理器
整合所有缓存类型的统一接口，支持多级缓存策略和智能路由
"""

import json
import logging
from typing import Any, Optional, Dict, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import threading
import time
from dataclasses import dataclass, asdict

# 导入所有缓存实现
from memory_cache import MemoryCache, AdvancedMemoryCache
from sqlite_cache import SQLiteCache, AdvancedSQLiteCache
from mysql_cache import MySQLCache, MySQLCacheCluster
from redis_cache import RedisCache, RedisCacheAdvanced
from mongodb_cache import MongoDBCache, MongoDBCacheAdvanced
from semantic_cache import SemanticCache, SemanticCacheWithPersistence
from gptcache_integration import GPTCacheIntegration, CacheConfig

class CacheLevel(Enum):
    """缓存层级枚举"""
    L1_MEMORY = "memory"
    L2_SQLITE = "sqlite"
    L3_MYSQL = "mysql"
    L4_REDIS = "redis"
    L5_MONGODB = "mongodb"
    L6_SEMANTIC = "semantic"
    L7_GPTCACHE = "gptcache"

@dataclass
class CacheItem:
    """缓存项数据类"""
    key: str
    value: Any
    level: CacheLevel
    ttl: int
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    accessed_at: datetime
    access_count: int
    size: int

class CacheStrategy:
    """缓存策略类"""
    
    def __init__(self, read_levels: List[CacheLevel], write_levels: List[CacheLevel]):
        self.read_levels = read_levels
        self.write_levels = write_levels
        self.cache_penetration_threshold = 100  # 防止缓存穿透的阈值
    
    def should_cache(self, key: str, value: Any) -> bool:
        """判断是否应该缓存"""
        # 检查值的大小
        value_size = len(str(value).encode('utf-8'))
        if value_size > 10 * 1024 * 1024:  # 10MB
            return False
        
        # 检查键的模式
        if key.startswith("temp_") or key.startswith("session_"):
            return False
        
        return True
    
    def select_write_levels(self, key: str, value: Any) -> List[CacheLevel]:
        """选择写入的缓存层级"""
        value_size = len(str(value).encode('utf-8'))
        
        if value_size < 1024:  # 1KB以下
            return [CacheLevel.L1_MEMORY, CacheLevel.L2_SQLITE]
        elif value_size < 100 * 1024:  # 100KB以下
            return [CacheLevel.L2_SQLITE, CacheLevel.L3_MYSQL]
        else:
            return [CacheLevel.L4_REDIS, CacheLevel.L5_MONGODB]

class UnifiedCacheManager:
    """统一缓存管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.caches = {}
        self.strategy = None
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "hit_by_level": {level.value: 0 for level in CacheLevel},
            "write_by_level": {level.value: 0 for level in CacheLevel},
            "evictions": 0,
            "errors": 0
        }
        self._lock = threading.RLock()
        self._init_caches()
        self._init_strategy()
    
    def _init_caches(self):
        """初始化所有缓存"""
        try:
            # L1: 内存缓存
            if "memory" in self.config:
                self.caches[CacheLevel.L1_MEMORY] = AdvancedMemoryCache(
                    max_size=self.config["memory"].get("max_size", 1000),
                    ttl=self.config["memory"].get("ttl", 3600)
                )
            
            # L2: SQLite缓存
            if "sqlite" in self.config:
                self.caches[CacheLevel.L2_SQLITE] = AdvancedSQLiteCache(
                    db_path=self.config["sqlite"].get("db_path", "cache.db")
                )
            
            # L3: MySQL缓存
            if "mysql" in self.config:
                self.caches[CacheLevel.L3_MYSQL] = MySQLCache(
                    config=self.config["mysql"]
                )
            
            # L4: Redis缓存
            if "redis" in self.config:
                self.caches[CacheLevel.L4_REDIS] = RedisCacheAdvanced(
                    config=self.config["redis"]
                )
            
            # L5: MongoDB缓存
            if "mongodb" in self.config:
                self.caches[CacheLevel.L5_MONGODB] = MongoDBCacheAdvanced(
                    config=self.config["mongodb"]
                )
            
            # L6: 语义缓存
            if "semantic" in self.config:
                from semantic_cache import TransformerSemanticEncoder
                encoder = TransformerSemanticEncoder(
                    self.config["semantic"].get("model", "all-MiniLM-L6-v2")
                )
                self.caches[CacheLevel.L6_SEMANTIC] = SemanticCache(
                    encoder=encoder,
                    threshold=self.config["semantic"].get("threshold", 0.85)
                )
            
            # L7: GPTCache
            if "gptcache" in self.config:
                cache_config = CacheConfig(**self.config["gptcache"])
                self.caches[CacheLevel.L7_GPTCACHE] = GPTCacheIntegration(cache_config)
            
            logging.info(f"已初始化 {len(self.caches)} 个缓存")
            
        except Exception as e:
            logging.error(f"缓存初始化错误: {e}")
            raise
    
    def _init_strategy(self):
        """初始化缓存策略"""
        default_strategy = CacheStrategy(
            read_levels=[
                CacheLevel.L1_MEMORY,
                CacheLevel.L2_SQLITE,
                CacheLevel.L4_REDIS,
                CacheLevel.L5_MONGODB
            ],
            write_levels=[
                CacheLevel.L1_MEMORY,
                CacheLevel.L2_SQLITE,
                CacheLevel.L4_REDIS
            ]
        )
        self.strategy = self.config.get("strategy", default_strategy)
    
    def get(self, key: str, use_semantic: bool = False) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            self.metrics["total_requests"] += 1
            
            # 语义缓存特殊处理
            if use_semantic and CacheLevel.L6_SEMANTIC in self.caches:
                semantic_cache = self.caches[CacheLevel.L6_SEMANTIC]
                result = semantic_cache.get(key)
                if result:
                    self.metrics["cache_hits"] += 1
                    self.metrics["hit_by_level"][CacheLevel.L6_SEMANTIC.value] += 1
                    return result["value"]
            
            # 按层级查找
            for level in self.strategy.read_levels:
                if level in self.caches:
                    try:
                        value = self.caches[level].get(key)
                        if value is not None:
                            self.metrics["cache_hits"] += 1
                            self.metrics["hit_by_level"][level.value] += 1
                            
                            # 回写到更高层级
                            self._write_up(key, value, level)
                            
                            return value
                    except Exception as e:
                        logging.error(f"从 {level.value} 获取缓存错误: {e}")
                        self.metrics["errors"] += 1
            
            self.metrics["cache_misses"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600, 
            tags: List[str] = None, metadata: Dict = None) -> bool:
        """设置缓存值"""
        with self._lock:
            if not self.strategy.should_cache(key, value):
                return False
            
            write_levels = self.strategy.select_write_levels(key, value)
            success = False
            
            for level in write_levels:
                if level in self.caches:
                    try:
                        result = self.caches[level].set(
                            key, value, ttl=ttl, tags=tags, metadata=metadata
                        )
                        if result:
                            self.metrics["write_by_level"][level.value] += 1
                            success = True
                    except Exception as e:
                        logging.error(f"写入 {level.value} 缓存错误: {e}")
                        self.metrics["errors"] += 1
            
            return success
    
    def delete(self, key: str, levels: List[CacheLevel] = None) -> int:
        """删除缓存"""
        with self._lock:
            deleted_count = 0
            target_levels = levels or self.strategy.read_levels
            
            for level in target_levels:
                if level in self.caches:
                    try:
                        result = self.caches[level].delete(key)
                        if result:
                            deleted_count += 1
                    except Exception as e:
                        logging.error(f"从 {level.value} 删除缓存错误: {e}")
            
            return deleted_count
    
    def delete_by_tags(self, tags: List[str], 
                      levels: List[CacheLevel] = None) -> int:
        """按标签删除缓存"""
        with self._lock:
            deleted_count = 0
            target_levels = levels or [CacheLevel.L2_SQLITE, CacheLevel.L3_MYSQL, 
                                     CacheLevel.L4_REDIS, CacheLevel.L5_MONGODB]
            
            for level in target_levels:
                if level in self.caches:
                    try:
                        result = self.caches[level].delete_by_tags(tags)
                        deleted_count += result
                    except Exception as e:
                        logging.error(f"从 {level.value} 按标签删除缓存错误: {e}")
            
            return deleted_count
    
    def clear(self, levels: List[CacheLevel] = None) -> bool:
        """清空缓存"""
        with self._lock:
            target_levels = levels or list(self.caches.keys())
            
            for level in target_levels:
                if level in self.caches:
                    try:
                        self.caches[level].clear()
                    except Exception as e:
                        logging.error(f"清空 {level.value} 缓存错误: {e}")
            
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            stats = {
                "overall": self.metrics,
                "by_level": {}
            }
            
            for level, cache in self.caches.items():
                try:
                    level_stats = cache.get_stats() if hasattr(cache, 'get_stats') else {}
                    stats["by_level"][level.value] = level_stats
                except Exception as e:
                    logging.error(f"获取 {level.value} 统计错误: {e}")
            
            return stats
    
    def _write_up(self, key: str, value: Any, from_level: CacheLevel):
        """向上级缓存回写"""
        try:
            write_levels = self.strategy.write_levels
            from_index = write_levels.index(from_level) if from_level in write_levels else -1
            
            if from_index >= 0:
                for level in write_levels[:from_index]:
                    if level in self.caches:
                        self.caches[level].set(key, value, ttl=3600)
                        
        except Exception as e:
            logging.error(f"向上级缓存回写错误: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {}
        
        for level, cache in self.caches.items():
            try:
                # 简单的健康检查
                test_key = f"health_check_{level.value}_{int(time.time())}"
                test_value = {"test": True, "timestamp": datetime.now().isoformat()}
                
                cache.set(test_key, test_value, ttl=10)
                retrieved = cache.get(test_key)
                
                health_status[level.value] = {
                    "status": "healthy" if retrieved else "unhealthy",
                    "response_time": 0.1  # 模拟响应时间
                }
                
                # 清理测试数据
                cache.delete(test_key)
                
            except Exception as e:
                health_status[level.value] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_status

class CacheMonitor:
    """缓存监控器"""
    
    def __init__(self, cache_manager: UnifiedCacheManager):
        self.cache_manager = cache_manager
        self.is_running = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval: int = 60):
        """开始监控"""
        self.is_running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval: int):
        """监控循环"""
        while self.is_running:
            try:
                stats = self.cache_manager.get_stats()
                health = self.cache_manager.health_check()
                
                # 记录监控数据
                logging.info(f"缓存监控 - 统计: {json.dumps(stats, indent=2)}")
                logging.info(f"缓存监控 - 健康: {json.dumps(health, indent=2)}")
                
                # 检查是否需要清理
                self._check_cleanup_needed(stats)
                
                time.sleep(interval)
                
            except Exception as e:
                logging.error(f"监控循环错误: {e}")
                time.sleep(interval)
    
    def _check_cleanup_needed(self, stats: Dict[str, Any]):
        """检查是否需要清理"""
        # 简单的清理逻辑
        total_items = sum(
            level_stats.get("total_items", 0) 
            for level_stats in stats.get("by_level", {}).values()
        )
        
        if total_items > 10000:  # 阈值
            logging.warning(f"缓存项目过多: {total_items}，考虑清理")

# 使用示例
if __name__ == "__main__":
    # 统一缓存配置
    unified_config = {
        "memory": {
            "max_size": 1000,
            "ttl": 3600
        },
        "sqlite": {
            "db_path": "./cache/unified_cache.db"
        },
        "redis": {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "key_prefix": "unified"
        },
        "mongodb": {
            "connection_string": "mongodb://localhost:27017/",
            "database": "unified_cache",
            "collection": "cache_items"
        },
        "semantic": {
            "model": "all-MiniLM-L6-v2",
            "threshold": 0.85
        },
        "strategy": CacheStrategy(
            read_levels=[
                CacheLevel.L1_MEMORY,
                CacheLevel.L2_SQLITE,
                CacheLevel.L4_REDIS,
                CacheLevel.L5_MONGODB
            ],
            write_levels=[
                CacheLevel.L1_MEMORY,
                CacheLevel.L2_SQLITE,
                CacheLevel.L4_REDIS
            ]
        )
    }
    
    # 初始化统一缓存管理器
    cache_manager = UnifiedCacheManager(unified_config)
    
    # 设置缓存
    cache_manager.set(
        "user:profile:123",
        {
            "user_id": 123,
            "username": "test_user",
            "email": "test@example.com",
            "created_at": datetime.now().isoformat()
        },
        ttl=3600,
        tags=["user", "profile"]
    )
    
    # 获取缓存
    profile = cache_manager.get("user:profile:123")
    print(f"用户资料: {json.dumps(profile, indent=2, ensure_ascii=False)}")
    
    # 获取统计信息
    stats = cache_manager.get_stats()
    print(f"\n缓存统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 健康检查
    health = cache_manager.health_check()
    print(f"\n健康检查: {json.dumps(health, indent=2, ensure_ascii=False)}")
    
    # 启动监控
    monitor = CacheMonitor(cache_manager)
    monitor.start_monitoring(interval=30)
    
    # 测试语义缓存
    semantic_result = cache_manager.get("用户123的个人信息", use_semantic=True)
    if semantic_result:
        print(f"\n语义缓存命中: {json.dumps(semantic_result, indent=2, ensure_ascii=False)}")
    
    # 等待监控运行
    time.sleep(5)
    monitor.stop_monitoring()