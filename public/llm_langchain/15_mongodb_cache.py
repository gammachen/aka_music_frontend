#!/usr/bin/env python3
"""
MongoDB自定义缓存实现
支持文档存储、复杂查询和聚合分析的MongoDB缓存系统
"""

import pymongo
from pymongo import MongoClient, IndexModel
from pymongo.errors import PyMongoError
import json
import hashlib
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import logging
from bson import ObjectId
from gridfs import GridFS

class MongoDBCache:
    """MongoDB缓存实现"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.db = None
        self.collection = None
        self.gridfs = None
        self._init_connection()
        self._create_indexes()
    
    def _init_connection(self):
        """初始化MongoDB连接"""
        try:
            connection_string = self.config.get("connection_string", "mongodb://localhost:27017/")
            
            self.client = MongoClient(
                connection_string,
                maxPoolSize=self.config.get("max_pool_size", 100),
                minPoolSize=self.config.get("min_pool_size", 10),
                maxIdleTimeMS=self.config.get("max_idle_time", 30000),
                **self.config.get("options", {})
            )
            
            db_name = self.config.get("database", "cache_db")
            collection_name = self.config.get("collection", "cache_items")
            
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            self.gridfs = GridFS(self.db, collection=f"{collection_name}_files")
            
            # 测试连接
            self.client.admin.command('ping')
            
        except PyMongoError as e:
            logging.error(f"MongoDB连接失败: {e}")
            raise
    
    def _create_indexes(self):
        """创建索引"""
        try:
            indexes = [
                IndexModel([("cache_key", pymongo.ASCENDING)], unique=True),
                IndexModel([("expire_at", pymongo.ASCENDING)], expireAfterSeconds=0),
                IndexModel([("tags", pymongo.ASCENDING)]),
                IndexModel([("created_at", pymongo.DESCENDING)]),
                IndexModel([("access_count", pymongo.DESCENDING)]),
                IndexModel([("last_accessed", pymongo.DESCENDING)])
            ]
            
            self.collection.create_indexes(indexes)
            
        except PyMongoError as e:
            logging.error(f"MongoDB索引创建失败: {e}")
    
    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        prefix = self.config.get("key_prefix", "cache")
        return f"{prefix}_{hashlib.sha256(key.encode()).hexdigest()}"
    
    def set(self, key: str, value: Any, ttl: int = 3600, 
            tags: List[str] = None, metadata: Dict = None, 
            use_gridfs: bool = False) -> bool:
        """设置缓存值"""
        try:
            cache_key = self._generate_key(key)
            expire_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            # 检查数据大小
            data_size = len(json.dumps(value, ensure_ascii=False).encode('utf-8'))
            max_size = self.config.get("max_document_size", 16777216)  # 16MB
            
            if use_gridfs or data_size > max_size:
                # 使用GridFS存储大文件
                value_str = json.dumps(value, ensure_ascii=False)
                file_id = self.gridfs.put(
                    value_str.encode('utf-8'),
                    filename=cache_key,
                    content_type="application/json",
                    metadata=metadata or {}
                )
                
                cache_doc = {
                    "cache_key": cache_key,
                    "original_key": key,
                    "file_id": file_id,
                    "is_gridfs": True,
                    "data_type": type(value).__name__,
                    "data_size": data_size,
                    "tags": tags or [],
                    "metadata": metadata or {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "last_accessed": datetime.utcnow(),
                    "access_count": 0,
                    "expire_at": expire_at
                }
            else:
                # 直接存储在文档中
                cache_doc = {
                    "cache_key": cache_key,
                    "original_key": key,
                    "value": value,
                    "is_gridfs": False,
                    "data_type": type(value).__name__,
                    "data_size": data_size,
                    "tags": tags or [],
                    "metadata": metadata or {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "last_accessed": datetime.utcnow(),
                    "access_count": 0,
                    "expire_at": expire_at
                }
            
            # 使用upsert更新或插入
            result = self.collection.replace_one(
                {"cache_key": cache_key},
                cache_doc,
                upsert=True
            )
            
            return result.acknowledged
            
        except PyMongoError as e:
            logging.error(f"MongoDB缓存设置错误: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            cache_key = self._generate_key(key)
            cache_doc = self.collection.find_one({"cache_key": cache_key})
            
            if not cache_doc:
                return None
            
            # 更新访问统计
            self.collection.update_one(
                {"cache_key": cache_key},
                {
                    "$inc": {"access_count": 1},
                    "$set": {"last_accessed": datetime.utcnow()}
                }
            )
            
            if cache_doc.get("is_gridfs", False):
                # 从GridFS获取数据
                file_id = cache_doc["file_id"]
                file_data = self.gridfs.get(file_id).read()
                return json.loads(file_data.decode('utf-8'))
            else:
                # 直接从文档获取数据
                return cache_doc.get("value")
                
        except PyMongoError as e:
            logging.error(f"MongoDB缓存获取错误: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        try:
            cache_key = self._generate_key(key)
            cache_doc = self.collection.find_one({"cache_key": cache_key})
            
            if cache_doc:
                # 删除GridFS文件
                if cache_doc.get("is_gridfs", False) and "file_id" in cache_doc:
                    self.gridfs.delete(cache_doc["file_id"])
                
                # 删除缓存文档
                result = self.collection.delete_one({"cache_key": cache_key})
                return result.deleted_count > 0
            
            return False
            
        except PyMongoError as e:
            logging.error(f"MongoDB缓存删除错误: {e}")
            return False
    
    def delete_by_tags(self, tags: List[str]) -> int:
        """按标签删除缓存"""
        try:
            cursor = self.collection.find({"tags": {"$in": tags}})
            deleted_count = 0
            
            for doc in cursor:
                cache_key = doc["cache_key"]
                
                # 删除GridFS文件
                if doc.get("is_gridfs", False) and "file_id" in doc:
                    self.gridfs.delete(doc["file_id"])
                
                # 删除缓存文档
                result = self.collection.delete_one({"cache_key": cache_key})
                deleted_count += result.deleted_count
            
            return deleted_count
            
        except PyMongoError as e:
            logging.error(f"MongoDB标签删除错误: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            cache_key = self._generate_key(key)
            return self.collection.count_documents({"cache_key": cache_key}) > 0
        except PyMongoError as e:
            logging.error(f"MongoDB存在检查错误: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """获取剩余TTL（秒）"""
        try:
            cache_key = self._generate_key(key)
            cache_doc = self.collection.find_one({"cache_key": cache_key})
            
            if not cache_doc:
                return -2  # 不存在
            
            expire_at = cache_doc.get("expire_at")
            if not expire_at:
                return -1  # 永不过期
            
            remaining = (expire_at - datetime.utcnow()).total_seconds()
            return max(0, int(remaining))
            
        except PyMongoError as e:
            logging.error(f"MongoDB TTL获取错误: {e}")
            return -2
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            # 删除所有GridFS文件
            prefix = self.config.get("key_prefix", "cache")
            collection_name = self.config.get("collection", "cache_items")
            
            cursor = self.collection.find({})
            for doc in cursor:
                if doc.get("is_gridfs", False) and "file_id" in doc:
                    try:
                        self.gridfs.delete(doc["file_id"])
                    except:
                        pass
            
            # 清空集合
            result = self.collection.delete_many({})
            return result.acknowledged
            
        except PyMongoError as e:
            logging.error(f"MongoDB清空错误: {e}")
            return False
    
    def search(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """搜索缓存"""
        try:
            cursor = self.collection.find(query).limit(limit)
            results = []
            
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                if "file_id" in doc:
                    doc["file_id"] = str(doc["file_id"])
                results.append(doc)
            
            return results
            
        except PyMongoError as e:
            logging.error(f"MongoDB搜索错误: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        try:
            total_count = self.collection.count_documents({})
            
            # 聚合统计
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_size": {"$sum": "$data_size"},
                        "avg_size": {"$avg": "$data_size"},
                        "max_size": {"$max": "$data_size"},
                        "min_size": {"$min": "$data_size"},
                        "total_access": {"$sum": "$access_count"},
                        "avg_access": {"$avg": "$access_count"}
                    }
                }
            ]
            
            stats_result = list(self.collection.aggregate(pipeline))
            stats = stats_result[0] if stats_result else {}
            
            # 标签统计
            tag_pipeline = [
                {"$unwind": "$tags"},
                {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            tag_stats = list(self.collection.aggregate(tag_pipeline))
            
            # 数据类型统计
            type_pipeline = [
                {"$group": {"_id": "$data_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            type_stats = list(self.collection.aggregate(type_pipeline))
            
            return {
                "total_items": total_count,
                "storage_stats": {
                    "total_size_bytes": stats.get("total_size", 0),
                    "average_size_bytes": stats.get("avg_size", 0),
                    "max_size_bytes": stats.get("max_size", 0),
                    "min_size_bytes": stats.get("min_size", 0)
                },
                "access_stats": {
                    "total_access": stats.get("total_access", 0),
                    "average_access": stats.get("avg_access", 0)
                },
                "top_tags": [{"tag": t["_id"], "count": t["count"]} for t in tag_stats],
                "type_distribution": [{"type": t["_id"], "count": t["count"]} for t in type_stats],
                "database_stats": self.db.command("dbStats")
            }
            
        except PyMongoError as e:
            logging.error(f"MongoDB统计错误: {e}")
            return {}

class MongoDBCacheAdvanced(MongoDBCache):
    """高级MongoDB缓存，支持复杂查询和聚合"""
    
    def set_with_versioning(self, key: str, value: Any, ttl: int = 3600,
                           tags: List[str] = None, metadata: Dict = None) -> bool:
        """设置带版本控制的缓存"""
        try:
            cache_key = self._generate_key(key)
            
            # 获取当前版本号
            current_doc = self.collection.find_one(
                {"cache_key": cache_key},
                sort=[("version", -1)]
            )
            
            version = (current_doc.get("version", 0) + 1) if current_doc else 1
            
            # 设置新版本
            return self.set(key, value, ttl, tags, {
                **(metadata or {}),
                "version": version,
                "previous_version": current_doc.get("version") if current_doc else None
            })
            
        except PyMongoError as e:
            logging.error(f"MongoDB版本控制设置错误: {e}")
            return False
    
    def get_version_history(self, key: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取版本历史"""
        try:
            cache_key = self._generate_key(key)
            cursor = self.collection.find(
                {"cache_key": cache_key},
                sort=[("created_at", -1)]
            ).limit(limit)
            
            history = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                if "file_id" in doc:
                    doc["file_id"] = str(doc["file_id"])
                history.append(doc)
            
            return history
            
        except PyMongoError as e:
            logging.error(f"MongoDB版本历史获取错误: {e}")
            return []

# 使用示例
if __name__ == "__main__":
    mongodb_config = {
        "connection_string": "mongodb://localhost:27017/",
        "database": "cache_system",
        "collection": "cache_items",
        "key_prefix": "app"
    }
    
    cache = MongoDBCache(mongodb_config)
    
    # 基本缓存操作
    cache.set("user:profile:123", {
        "user_id": 123,
        "username": "test_user",
        "email": "test@example.com",
        "preferences": {
            "theme": "dark",
            "language": "zh-CN",
            "notifications": True
        }
    }, ttl=3600, tags=["user", "profile", "settings"])
    
    profile = cache.get("user:profile:123")
    print(f"用户资料: {json.dumps(profile, indent=2, ensure_ascii=False)}")
    
    # 搜索缓存
    search_results = cache.search({"tags": {"$in": ["user"]}})
    print(f"搜索到 {len(search_results)} 个用户相关缓存")
    
    # 统计信息
    stats = cache.get_stats()
    print(f"MongoDB缓存统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 高级功能
    advanced_cache = MongoDBCacheAdvanced(mongodb_config)
    
    # 版本控制
    advanced_cache.set_with_versioning("config:app", {
        "version": "1.0.0",
        "features": ["feature1", "feature2"]
    }, tags=["config", "app"])
    
    advanced_cache.set_with_versioning("config:app", {
        "version": "1.1.0",
        "features": ["feature1", "feature2", "feature3"]
    }, tags=["config", "app"])
    
    history = advanced_cache.get_version_history("config:app")
    print(f"配置版本历史: {json.dumps(history, indent=2, ensure_ascii=False)}")