#!/usr/bin/env python3
"""
MySQL缓存实现 - L3数据库缓存
支持分片和集群的MySQL缓存系统
"""

import mysql.connector
from mysql.connector import pooling
import json
import hashlib
import threading
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import logging

class MySQLCache:
    """MySQL数据库缓存实现"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pool = None
        self.table_name = config.get("table_name", "cache_data")
        self._lock = threading.RLock()
        self._init_pool()
        self._init_table()
    
    def _init_pool(self):
        """初始化连接池"""
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mysql_cache_pool",
                pool_size=10,
                **self.config
            )
        except Exception as e:
            logging.error(f"MySQL连接池初始化失败: {e}")
            raise
    
    def _init_table(self):
        """初始化数据库表"""
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            cache_key VARCHAR(255) UNIQUE KEY,
            cache_value LONGTEXT,
            data_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            access_count BIGINT DEFAULT 1,
            tags JSON,
            metadata JSON,
            INDEX idx_key (cache_key),
            INDEX idx_expires (expires_at),
            INDEX idx_updated (updated_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            with self.pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_sql)
                    conn.commit()
        except Exception as e:
            logging.error(f"MySQL表初始化失败: {e}")
            raise
    
    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def set(self, key: str, value: Any, ttl: int = 3600, 
            tags: List[str] = None, metadata: Dict = None) -> bool:
        """设置缓存值"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                value_str = json.dumps(value, ensure_ascii=False)
                data_type = type(value).__name__
                expires_at = datetime.now() + timedelta(seconds=ttl)
                tags_json = json.dumps(tags or [])
                metadata_json = json.dumps(metadata or {})
                
                with self.pool.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(f"""
                            INSERT INTO {self.table_name} 
                            (cache_key, cache_value, data_type, expires_at, tags, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            cache_value = VALUES(cache_value),
                            data_type = VALUES(data_type),
                            expires_at = VALUES(expires_at),
                            tags = VALUES(tags),
                            metadata = VALUES(metadata),
                            access_count = access_count + 1,
                            updated_at = CURRENT_TIMESTAMP
                        """, (cache_key, value_str, data_type, expires_at, 
                              tags_json, metadata_json))
                        conn.commit()
                
                return True
            except Exception as e:
                logging.error(f"MySQL缓存设置错误: {e}")
                return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                
                with self.pool.get_connection() as conn:
                    with conn.cursor(dictionary=True) as cursor:
                        cursor.execute(f"""
                            SELECT cache_value, data_type, expires_at, access_count, tags, metadata
                            FROM {self.table_name}
                            WHERE cache_key = %s AND expires_at > NOW()
                        """, (cache_key,))
                        
                        result = cursor.fetchone()
                        
                        if not result:
                            return None
                        
                        # 更新访问计数
                        cursor.execute(f"""
                            UPDATE {self.table_name} 
                            SET access_count = access_count + 1
                            WHERE cache_key = %s
                        """, (cache_key,))
                        conn.commit()
                        
                        return json.loads(result["cache_value"])
                        
            except Exception as e:
                logging.error(f"MySQL缓存获取错误: {e}")
                return None
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                
                with self.pool.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(f"""
                            DELETE FROM {self.table_name} WHERE cache_key = %s
                        """, (cache_key,))
                        conn.commit()
                        return cursor.rowcount > 0
                        
            except Exception as e:
                logging.error(f"MySQL缓存删除错误: {e}")
                return False
    
    def delete_by_tags(self, tags: List[str]) -> int:
        """按标签删除缓存"""
        with self._lock:
            try:
                tags_condition = " OR ".join(["JSON_CONTAINS(tags, JSON_ARRAY(%s))"] * len(tags))
                
                with self.pool.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(f"""
                            DELETE FROM {self.table_name}
                            WHERE {tags_condition}
                        """, tags)
                        conn.commit()
                        return cursor.rowcount
                        
            except Exception as e:
                logging.error(f"MySQL标签删除错误: {e}")
                return 0
    
    def clear_expired(self) -> int:
        """清理过期缓存"""
        with self._lock:
            try:
                with self.pool.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(f"""
                            DELETE FROM {self.table_name}
                            WHERE expires_at <= NOW()
                        """)
                        conn.commit()
                        return cursor.rowcount
                        
            except Exception as e:
                logging.error(f"MySQL清理过期错误: {e}")
                return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            try:
                with self.pool.get_connection() as conn:
                    with conn.cursor(dictionary=True) as cursor:
                        cursor.execute(f"""
                            SELECT 
                                COUNT(*) as total_items,
                                SUM(LENGTH(cache_value)) as total_size,
                                AVG(access_count) as avg_access,
                                MIN(created_at) as oldest_item,
                                MAX(updated_at) as newest_item,
                                SUM(CASE WHEN expires_at <= NOW() THEN 1 ELSE 0 END) as expired_items
                            FROM {self.table_name}
                        """)
                        
                        stats = cursor.fetchone()
                        
                        cursor.execute(f"""
                            SELECT data_type, COUNT(*) as count
                            FROM {self.table_name}
                            GROUP BY data_type
                            ORDER BY count DESC
                        """)
                        
                        type_stats = cursor.fetchall()
                        
                        return {
                            "total_items": stats["total_items"] or 0,
                            "total_size_bytes": stats["total_size"] or 0,
                            "avg_access_count": float(stats["avg_access"] or 0),
                            "oldest_item": str(stats["oldest_item"]) if stats["oldest_item"] else None,
                            "newest_item": str(stats["newest_item"]) if stats["newest_item"] else None,
                            "expired_items": stats["expired_items"] or 0,
                            "data_type_distribution": {row["data_type"]: row["count"] for row in type_stats}
                        }
                        
            except Exception as e:
                logging.error(f"MySQL统计错误: {e}")
                return {}

class MySQLCacheCluster:
    """MySQL缓存集群"""
    
    def __init__(self, cluster_config: List[Dict[str, Any]]):
        self.nodes = [MySQLCache(config) for config in cluster_config]
        self._current_node = 0
    
    def _get_node(self, key: str) -> MySQLCache:
        """根据key选择节点 (一致性哈希)"""
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
    mysql_config = {
        "host": "localhost",
        "user": "cache_user",
        "password": "cache_password",
        "database": "cache_db",
        "table_name": "app_cache"
    }
    
    cache = MySQLCache(mysql_config)
    
    # 设置缓存
    cache.set("product:123", {
        "name": "iPhone 15 Pro",
        "price": 8999.00,
        "stock": 100
    }, ttl=7200, tags=["product", "electronics"], 
    metadata={"source": "api", "version": "1.0"})
    
    # 获取缓存
    product_data = cache.get("product:123")
    print(f"产品数据: {product_data}")
    
    # 获取统计
    stats = cache.get_stats()
    print(f"MySQL缓存统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")