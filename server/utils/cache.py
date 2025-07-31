"""
缓存管理模块
支持内存缓存和Redis缓存
"""

import asyncio
import json
import hashlib
import time
from typing import Optional, Dict, Any
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)

class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, max_size: int = 10000, ttl: int = 86400):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
    
    def _is_expired(self, key: str) -> bool:
        """检查缓存项是否过期"""
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl
    
    def _cleanup_expired(self):
        """清理过期的缓存项"""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in self.timestamps.items():
            if current_time - timestamp > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
    
    def _ensure_capacity(self):
        """确保缓存容量不超过限制"""
        while len(self.cache) >= self.max_size:
            # 删除最旧的缓存项
            oldest_key = next(iter(self.cache))
            self.cache.pop(oldest_key)
            self.timestamps.pop(oldest_key, None)
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        self._cleanup_expired()
        
        if key in self.cache and not self._is_expired(key):
            # 移动到末尾（LRU）
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        
        return None
    
    async def set(self, key: str, value: Any):
        """设置缓存值"""
        self._cleanup_expired()
        self._ensure_capacity()
        
        # 如果key已存在，先删除
        if key in self.cache:
            self.cache.pop(key)
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    async def delete(self, key: str):
        """删除缓存项"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
    
    async def clear(self):
        """清空所有缓存"""
        self.cache.clear()
        self.timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        self._cleanup_expired()
        return {
            "total_items": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "memory_usage_estimate": len(str(self.cache))
        }

class RedisCache:
    """Redis缓存实现"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, 
                 db: int = 0, password: str = "", ttl: int = 86400):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.ttl = ttl
        self.redis_client = None
    
    async def _get_client(self):
        """获取Redis客户端"""
        if self.redis_client is None:
            try:
                import aioredis
                self.redis_client = aioredis.from_url(
                    f"redis://{self.host}:{self.port}/{self.db}",
                    password=self.password if self.password else None,
                    decode_responses=True
                )
                # 测试连接
                await self.redis_client.ping()
                logger.info("Redis连接成功")
            except ImportError:
                logger.error("未安装aioredis，请运行: pip install aioredis")
                raise
            except Exception as e:
                logger.error(f"Redis连接失败: {str(e)}")
                raise
        
        return self.redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            client = await self._get_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis获取缓存失败: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any):
        """设置缓存值"""
        try:
            client = await self._get_client()
            await client.setex(key, self.ttl, json.dumps(value, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Redis设置缓存失败: {str(e)}")
    
    async def delete(self, key: str):
        """删除缓存项"""
        try:
            client = await self._get_client()
            await client.delete(key)
        except Exception as e:
            logger.error(f"Redis删除缓存失败: {str(e)}")
    
    async def clear(self):
        """清空所有缓存"""
        try:
            client = await self._get_client()
            await client.flushdb()
        except Exception as e:
            logger.error(f"Redis清空缓存失败: {str(e)}")
    
    async def close(self):
        """关闭Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            client = await self._get_client()
            info = await client.info("memory")
            return {
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            logger.error(f"获取Redis统计信息失败: {str(e)}")
            return {}

class CacheManager:
    """缓存管理器 - 统一缓存接口"""
    
    def __init__(self):
        self.cache_backend = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0
        }
    
    async def initialize(self):
        """初始化缓存后端"""
        from config import settings
        
        if settings.redis_enabled:
            try:
                self.cache_backend = RedisCache(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password,
                    ttl=settings.cache_ttl
                )
                # 测试Redis连接
                await self.cache_backend._get_client()
                logger.info("使用Redis缓存")
            except Exception as e:
                logger.warning(f"Redis初始化失败，使用内存缓存: {str(e)}")
                self.cache_backend = MemoryCache(
                    max_size=settings.max_cache_size,
                    ttl=settings.cache_ttl
                )
        else:
            self.cache_backend = MemoryCache(
                max_size=settings.max_cache_size,
                ttl=settings.cache_ttl
            )
            logger.info("使用内存缓存")
    
    def generate_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """生成缓存键"""
        # 使用MD5哈希生成固定长度的缓存键
        content = f"{text}:{source_lang}:{target_lang}"
        return f"translate:{hashlib.md5(content.encode('utf-8')).hexdigest()}"
    
    async def get_cached_translation(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取缓存的翻译结果"""
        if not self.cache_backend:
            await self.initialize()
        
        try:
            result = await self.cache_backend.get(cache_key)
            if result:
                self.stats["hits"] += 1
                return result
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            logger.error(f"获取缓存失败: {str(e)}")
            self.stats["misses"] += 1
            return None
    
    async def cache_translation(self, cache_key: str, translation_result: Dict[str, Any]):
        """缓存翻译结果"""
        if not self.cache_backend:
            await self.initialize()
        
        try:
            await self.cache_backend.set(cache_key, translation_result)
            self.stats["sets"] += 1
        except Exception as e:
            logger.error(f"缓存翻译结果失败: {str(e)}")
    
    async def clear_cache(self):
        """清空缓存"""
        if self.cache_backend:
            await self.cache_backend.clear()
    
    async def close(self):
        """关闭缓存连接"""
        if hasattr(self.cache_backend, 'close'):
            await self.cache_backend.close()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total_requests
        }