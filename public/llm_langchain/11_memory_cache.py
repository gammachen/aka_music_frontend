#!/usr/bin/env python3
"""
内存缓存实现 - L1高速缓存
基于LRU淘汰策略的线程安全内存缓存
"""

import threading
import time
from typing import Any, Optional, Dict
from collections import OrderedDict
import json
import hashlib
from datetime import datetime, timedelta

class MemoryCache:
    """线程安全的内存缓存实现"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self._cache = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }
    
    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            cache_key = self._generate_key(key)
            
            if cache_key not in self._cache:
                self._stats["misses"] += 1
                return None
            
            value, timestamp = self._cache[cache_key]
            
            # 检查过期
            if time.time() - timestamp > self.ttl:
                del self._cache[cache_key]
                self._stats["misses"] += 1
                self._stats["size"] = len(self._cache)
                return None
            
            # 移动到末尾 (LRU)
            self._cache.move_to_end(cache_key)
            self._stats["hits"] += 1
            return value
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""
        with self._lock:
            cache_key = self._generate_key(key)
            
            # 如果已存在，先删除
            if cache_key in self._cache:
                del self._cache[cache_key]
            
            # 检查容量
            if len(self._cache) >= self.max_size:
                # 移除最旧的
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats["evictions"] += 1
            
            self._cache[cache_key] = (value, time.time())
            self._cache.move_to_end(cache_key)
            self._stats["size"] = len(self._cache)
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            cache_key = self._generate_key(key)
            if cache_key in self._cache:
                del self._cache[cache_key]
                self._stats["size"] = len(self._cache)
                return True
            return False
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._stats["size"] = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                **self._stats,
                "hit_rate": hit_rate,
                "memory_usage_mb": len(self._cache) * 0.001  # 估算
            }

class AdvancedMemoryCache:
    """支持TTL分级的内存缓存"""
    
    def __init__(self):
        self.caches = {
            "hot": MemoryCache(max_size=100, ttl=300),      # 5分钟
            "warm": MemoryCache(max_size=500, ttl=1800),  # 30分钟
            "cold": MemoryCache(max_size=1000, ttl=3600)  # 1小时
        }
    
    def get_tier(self, key: str) -> str:
        """根据访问频率决定缓存层级"""
        # 简化的实现，实际可基于访问频率统计
        return "hot"  # 默认热点
    
    def get(self, key: str) -> Optional[Any]:
        """分层获取"""
        for tier in ["hot", "warm", "cold"]:
            value = self.caches[tier].get(key)
            if value is not None:
                # 命中后升级到更高层级
                if tier != "hot":
                    self.caches[tier].delete(key)
                    self.caches["hot"].set(key, value)
                return value
        return None
    
    def set(self, key: str, value: Any, tier: str = "warm") -> None:
        """分层设置"""
        if tier in self.caches:
            self.caches[tier].set(key, value)

# 使用示例
if __name__ == "__main__":
    cache = MemoryCache(max_size=100, ttl=60)
    
    # 设置缓存
    cache.set("user:123", {"name": "张三", "age": 25})
    
    # 获取缓存
    user_data = cache.get("user:123")
    print(f"缓存数据: {user_data}")
    
    # 获取统计
    stats = cache.get_stats()
    print(f"缓存统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")