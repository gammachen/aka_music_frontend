#!/usr/bin/env python3
"""
SQLite缓存实现 - L2本地持久化缓存
支持复杂查询和事务的本地数据库缓存
"""

import sqlite3
import json
import time
import threading
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import hashlib

class SQLiteCache:
    """SQLite本地缓存实现"""
    
    def __init__(self, db_path: str = "cache.db", table_name: str = "cache_data"):
        self.db_path = db_path
        self.table_name = table_name
        self._lock = threading.RLock()
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    data_type TEXT DEFAULT 'json',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    access_count INTEGER DEFAULT 1,
                    ttl INTEGER DEFAULT 86400,
                    tags TEXT DEFAULT '[]'
                )
            """)
            
            # 创建索引
            conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{self.table_name}_ttl 
                ON {self.table_name}(ttl)
            """)
            
            conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{self.table_name}_updated 
                ON {self.table_name}(updated_at)
            """)
    
    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def set(self, key: str, value: Any, ttl: int = 3600, tags: List[str] = None) -> bool:
        """设置缓存值"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                value_str = json.dumps(value, ensure_ascii=False)
                data_type = type(value).__name__
                current_time = time.time()
                tags_str = json.dumps(tags or [])
                
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(f"""
                        INSERT OR REPLACE INTO {self.table_name} 
                        (key, value, data_type, created_at, updated_at, access_count, ttl, tags)
                        VALUES (?, ?, ?, ?, ?, COALESCE(
                            (SELECT access_count + 1 FROM {self.table_name} WHERE key = ?), 1
                        ), ?, ?)
                    """, (cache_key, value_str, data_type, current_time, current_time, 
                          cache_key, ttl, tags_str))
                
                return True
            except Exception as e:
                print(f"SQLite缓存设置错误: {e}")
                return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                
                with sqlite3.connect(self.db_path) as conn:
                    result = conn.execute(f"""
                        SELECT value, data_type, updated_at, ttl, access_count
                        FROM {self.table_name}
                        WHERE key = ?
                    """, (cache_key,)).fetchone()
                    
                    if not result:
                        return None
                    
                    value_str, data_type, updated_at, ttl, access_count = result
                    
                    # 检查过期
                    if time.time() - updated_at > ttl:
                        self.delete(key)
                        return None
                    
                    # 更新访问计数
                    conn.execute(f"""
                        UPDATE {self.table_name} 
                        SET access_count = access_count + 1, updated_at = ?
                        WHERE key = ?
                    """, (time.time(), cache_key))
                    
                    return json.loads(value_str)
                    
            except Exception as e:
                print(f"SQLite缓存获取错误: {e}")
                return None
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            try:
                cache_key = self._generate_key(key)
                with sqlite3.connect(self.db_path) as conn:
                    result = conn.execute(f"""
                        DELETE FROM {self.table_name} WHERE key = ?
                    """, (cache_key,))
                    return result.rowcount > 0
            except Exception as e:
                print(f"SQLite缓存删除错误: {e}")
                return False
    
    def delete_by_tags(self, tags: List[str]) -> int:
        """按标签删除缓存"""
        with self._lock:
            try:
                tags_str = json.dumps(tags)
                with sqlite3.connect(self.db_path) as conn:
                    result = conn.execute(f"""
                        DELETE FROM {self.table_name}
                        WHERE tags LIKE ? OR tags LIKE ? OR tags LIKE ?
                    """, (f'%"{tags[0]}"%', f'%"{tags[-1]}"%', f'%"{tags[0]}"%'))
                    return result.rowcount
            except Exception as e:
                print(f"SQLite标签删除错误: {e}")
                return 0
    
    def clear_expired(self) -> int:
        """清理过期缓存"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    result = conn.execute(f"""
                        DELETE FROM {self.table_name}
                        WHERE updated_at + ttl < ?
                    """, (time.time(),))
                    return result.rowcount
            except Exception as e:
                print(f"SQLite清理过期错误: {e}")
                return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    stats = conn.execute(f"""
                        SELECT 
                            COUNT(*) as total_items,
                            AVG(access_count) as avg_access,
                            SUM(LENGTH(value)) as total_size,
                            MIN(created_at) as oldest_item,
                            MAX(updated_at) as newest_item
                        FROM {self.table_name}
                    """).fetchone()
                    
                    return {
                        "total_items": stats[0] or 0,
                        "avg_access_count": stats[1] or 0,
                        "total_size_bytes": stats[2] or 0,
                        "oldest_item": datetime.fromtimestamp(stats[3]).isoformat() if stats[3] else None,
                        "newest_item": datetime.fromtimestamp(stats[4]).isoformat() if stats[4] else None
                    }
            except Exception as e:
                print(f"SQLite统计错误: {e}")
                return {}

class AdvancedSQLiteCache(SQLiteCache):
    """高级SQLite缓存，支持批量操作和复杂查询"""
    
    def batch_set(self, items: List[Dict[str, Any]]) -> int:
        """批量设置缓存"""
        with self._lock:
            try:
                current_time = time.time()
                with sqlite3.connect(self.db_path) as conn:
                    conn.executemany(f"""
                        INSERT OR REPLACE INTO {self.table_name} 
                        (key, value, data_type, created_at, updated_at, ttl, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, [
                        (self._generate_key(item["key"]), 
                         json.dumps(item["value"], ensure_ascii=False),
                         type(item["value"]).__name__,
                         current_time, current_time,
                         item.get("ttl", 3600),
                         json.dumps(item.get("tags", [])))
                        for item in items
                    ])
                    return conn.total_changes
            except Exception as e:
                print(f"SQLite批量设置错误: {e}")
                return 0
    
    def search_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """按模式搜索缓存"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    results = conn.execute(f"""
                        SELECT key, value, data_type, created_at, updated_at, access_count, tags
                        FROM {self.table_name}
                        WHERE key LIKE ? OR value LIKE ?
                        ORDER BY access_count DESC, updated_at DESC
                    """, (f"%{pattern}%", f"%{pattern}%"))
                    
                    items = []
                    for row in results.fetchall():
                        items.append({
                            "key": row[0],
                            "value": json.loads(row[1]),
                            "data_type": row[2],
                            "created_at": datetime.fromtimestamp(row[3]).isoformat(),
                            "updated_at": datetime.fromtimestamp(row[4]).isoformat(),
                            "access_count": row[5],
                            "tags": json.loads(row[6])
                        })
                    
                    return items
            except Exception as e:
                print(f"SQLite搜索错误: {e}")
                return []

# 使用示例
if __name__ == "__main__":
    cache = SQLiteCache("test_cache.db")
    
    # 设置缓存
    cache.set("user:123", {"name": "李四", "email": "lisi@example.com"}, 
              ttl=7200, tags=["user", "profile"])
    
    # 获取缓存
    user_data = cache.get("user:123")
    print(f"用户数据: {user_data}")
    
    # 获取统计
    stats = cache.get_stats()
    print(f"缓存统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 清理过期缓存
    cleared = cache.clear_expired()
    print(f"清理过期缓存: {cleared} 项")