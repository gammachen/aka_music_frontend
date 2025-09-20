#!/usr/bin/env python3
"""
Redis缓存实现 - L4分布式缓存
支持集群、哨兵和发布订阅的Redis缓存系统
"""

import redis
import json
import hashlib
import threading
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import logging
from redis.cluster import RedisCluster
from redis.sentinel import Sentinel

class RedisCache:
    """Redis缓存实现"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection_type = config.get("type", "single")
        self.client = None
        self._lock = threading.RLock()
        self._init_client()
    
    def _init_client(self):
        """初始化Redis客户端"""
        try:
            if self.connection_type == "cluster":
                self.client = RedisCluster(
                    startup_nodes=self.config["nodes"],
                    decode_responses=True,
                    **self.config.get("cluster_options", {})
                )
            elif self.connection_type == "sentinel":
                sentinel = Sentinel(
                    self.config["sentinels"],
                    socket_timeout=0.1,
                    decode_responses=True
                )
                self.client = sentinel.master_for(
                    self.config["service_name"],
                    socket_timeout=0.1,
                    decode_responses=True
                )
            else:  # single
                self.client = redis.Redis(
                    host=self.config.get("host", "localhost"),
                    port=self.config.get("port", 6379),
                    db=self.config.get("db", 0),
                    password=self.config.get("password"),
                    decode_responses=True,
                    **self.config.get("options", {})
                )
        except Exception as e:
            logging.error(f"Redis客户端初始化失败: {e}")
            raise
    
    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        prefix = self.config.get("key_prefix", "cache")
        return f"{prefix}:{hashlib.sha256(key.encode()).hexdigest()}"
    
    def set(self, key: str, value: Any, ttl: int = 3600, 
            tags: List[str] = None, metadata: Dict = None) -> bool:
        """设置缓存值"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                
                # 构建缓存数据结构
                cache_data = {
                    "value": value,
                    "data_type": type(value).__name__,
                    "created_at": datetime.now().isoformat(),
                    "tags": tags or [],
                    "metadata": metadata or {}
                }
                
                # 序列化数据
                value_str = json.dumps(cache_data, ensure_ascii=False)
                
                # 设置缓存
                result = self.client.setex(cache_key, ttl, value_str)
                
                # 设置标签索引
                if tags:
                    for tag in tags:
                        tag_key = f"{self.config.get('key_prefix', 'cache')}:tag:{tag}"
                        self.client.sadd(tag_key, cache_key)
                        self.client.expire(tag_key, ttl)
                
                return bool(result)
            except Exception as e:
                logging.error(f"Redis缓存设置错误: {e}")
                return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                value_str = self.client.get(cache_key)
                
                if not value_str:
                    return None
                
                cache_data = json.loads(value_str)
                return cache_data["value"]
                
            except Exception as e:
                logging.error(f"Redis缓存获取错误: {e}")
                return None
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                result = self.client.delete(cache_key)
                return result > 0
            except Exception as e:
                logging.error(f"Redis缓存删除错误: {e}")
                return False
    
    def delete_by_tags(self, tags: List[str]) -> int:
        """按标签删除缓存"""
        with self._lock:
            try:
                deleted_count = 0
                prefix = self.config.get("key_prefix", "cache")
                
                for tag in tags:
                    tag_key = f"{prefix}:tag:{tag}"
                    keys = self.client.smembers(tag_key)
                    
                    if keys:
                        deleted_count += self.client.delete(*keys)
                        self.client.delete(tag_key)
                
                return deleted_count
            except Exception as e:
                logging.error(f"Redis标签删除错误: {e}")
                return 0
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            cache_key = self._generate_key(key)
            return bool(self.client.exists(cache_key))
        except Exception as e:
            logging.error(f"Redis存在检查错误: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取剩余TTL"""
        try:
            cache_key = self._generate_key(key)
            return self.client.ttl(cache_key)
        except Exception as e:
            logging.error(f"Redis TTL获取错误: {e}")
            return -2
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            prefix = self.config.get("key_prefix", "cache")
            pattern = f"{prefix}:*"
            keys = self.client.keys(pattern)
            
            if keys:
                self.client.delete(*keys)
            
            return True
        except Exception as e:
            logging.error(f"Redis清空错误: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        try:
            info = self.client.info()
            prefix = self.config.get("key_prefix", "cache")
            pattern = f"{prefix}:*"
            keys = self.client.keys(pattern)
            
            total_memory = 0
            for key in keys:
                total_memory += self.client.memory_usage(key) or 0
            
            return {
                "total_keys": len(keys),
                "total_memory_bytes": total_memory,
                "redis_info": {
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed"),
                    "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec")
                }
            }
        except Exception as e:
            logging.error(f"Redis统计错误: {e}")
            return {}

class RedisCacheAdvanced(RedisCache):
    """高级Redis缓存，支持复杂数据结构"""
    
    def set_hash(self, key: str, field: str, value: Any, ttl: int = 3600) -> bool:
        """设置哈希缓存"""
        try:
            cache_key = self._generate_key(key)
            value_str = json.dumps(value, ensure_ascii=False)
            result = self.client.hset(cache_key, field, value_str)
            
            if ttl > 0:
                self.client.expire(cache_key, ttl)
            
            return bool(result)
        except Exception as e:
            logging.error(f"Redis哈希设置错误: {e}")
            return False
    
    def get_hash(self, key: str, field: str) -> Optional[Any]:
        """获取哈希缓存"""
        try:
            cache_key = self._generate_key(key)
            value_str = self.client.hget(cache_key, field)
            
            if not value_str:
                return None
            
            return json.loads(value_str)
        except Exception as e:
            logging.error(f"Redis哈希获取错误: {e}")
            return None
    
    def set_list(self, key: str, values: List[Any], ttl: int = 3600) -> bool:
        """设置列表缓存"""
        try:
            cache_key = self._generate_key(key)
            value_strs = [json.dumps(v, ensure_ascii=False) for v in values]
            
            # 先清空现有列表
            self.client.delete(cache_key)
            
            # 批量添加
            result = self.client.lpush(cache_key, *reversed(value_strs))
            
            if ttl > 0:
                self.client.expire(cache_key, ttl)
            
            return bool(result)
        except Exception as e:
            logging.error(f"Redis列表设置错误: {e}")
            return False
    
    def get_list(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """获取列表缓存"""
        try:
            cache_key = self._generate_key(key)
            value_strs = self.client.lrange(cache_key, start, end)
            
            return [json.loads(v) for v in value_strs]
        except Exception as e:
            logging.error(f"Redis列表获取错误: {e}")
            return []
    
    def set_sorted_set(self, key: str, score: float, value: Any, ttl: int = 3600) -> bool:
        """设置有序集合缓存"""
        try:
            cache_key = self._generate_key(key)
            value_str = json.dumps(value, ensure_ascii=False)
            result = self.client.zadd(cache_key, {value_str: score})
            
            if ttl > 0:
                self.client.expire(cache_key, ttl)
            
            return bool(result)
        except Exception as e:
            logging.error(f"Redis有序集合设置错误: {e}")
            return False
    
    def get_sorted_set_range(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """获取有序集合范围"""
        try:
            cache_key = self._generate_key(key)
            value_strs = self.client.zrange(cache_key, start, end)
            
            return [json.loads(v) for v in value_strs]
        except Exception as e:
            logging.error(f"Redis有序集合获取错误: {e}")
            return []

class RedisCacheCluster:
    """Redis缓存集群管理"""
    
    def __init__(self, cluster_configs: List[Dict[str, Any]]):
        self.nodes = [RedisCache(config) for config in cluster_configs]
    
    def _get_node(self, key: str) -> RedisCache:
        """根据key选择节点"""
        import hashlib
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return self.nodes[hash_value % len(self.nodes)]
    
    def set(self, key: str, value: Any, **kwargs) -> bool:
        """设置缓存值"""
        node = self._get_node(key)
        return node.set(key, value, **kwargs)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        node = self._get_node(key)
        return node.get(key)

# 使用示例
if __name__ == "__main__":
    redis_config = {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "key_prefix": "app_cache"
    }
    
    cache = RedisCache(redis_config)
    
    # 基本缓存操作
    cache.set("session:user:123", {
        "user_id": 123,
        "username": "test_user",
        "login_time": datetime.now().isoformat()
    }, ttl=1800)
    
    session_data = cache.get("session:user:123")
    print(f"会话数据: {session_data}")
    
    # 高级操作
    advanced_cache = RedisCacheAdvanced(redis_config)
    
    # 哈希缓存
    advanced_cache.set_hash("user:profile:123", "settings", {
        "theme": "dark",
        "language": "zh-CN"
    })
    
    settings = advanced_cache.get_hash("user:profile:123", "settings")
    print(f"用户设置: {settings}")
    
    # 统计信息
    stats = cache.get_stats()
    print(f"Redis统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")