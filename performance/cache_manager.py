"""
缓存管理器

提供多级缓存、智能过期、缓存预热等功能
"""

import time
import hashlib

from typing import Any, Dict, Optional, List

from datetime import datetime

from pathlib import Path
import threading


class CacheManager:
    """缓存管理器"""


    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """初始化缓存管理器"""
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict] = {}
        self.cache_lock = threading.RLock()

        # 统计信息
        self.stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'cache_size': 0
        }


    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        with self.cache_lock:
            self.stats['total_requests'] += 1

            if key in self.cache:
                entry = self.cache[key]

                # 检查是否过期
                if time.time() > entry['expires_at']:
                    del self.cache[key]
                    self.stats['misses'] += 1
                    return default

                # 更新访问统计
                entry['access_count'] += 1
                entry['last_accessed'] = time.time()
                self.stats['hits'] += 1

                return entry['value']

            self.stats['misses'] += 1
            return default


    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        with self.cache_lock:
            ttl = ttl or self.default_ttl
            current_time = time.time()

            # 检查是否需要清理空间
            if len(self.cache) >= self.max_size:
                self._evict_entries()

            # 存储到缓存
            self.cache[key] = {
                'value': value,
                'created_at': current_time,
                'expires_at': current_time + ttl,
                'access_count': 0,
                'last_accessed': current_time
            }

            self.stats['cache_size'] = len(self.cache)
            return True


    def delete(self, key: str) -> bool:
        """删除缓存条目"""
        with self.cache_lock:
            if key in self.cache:
                del self.cache[key]
                self.stats['cache_size'] = len(self.cache)
                return True
            return False


    def clear(self) -> int:
        """清空缓存"""
        with self.cache_lock:
            count = len(self.cache)
            self.cache.clear()
            self.stats['cache_size'] = 0
            return count


    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.cache_lock:
            hit_rate = 0
            if self.stats['total_requests'] > 0:
                hit_rate = self.stats['hits'] / self.stats['total_requests'] * 100

            return {
                **self.stats,
                'hit_rate_percent': round(hit_rate, 2)
            }


    def cache_response(self, prompt: str, model: str, temperature: float,
                      max_tokens: int, response: str, ttl: int = 1800) -> bool:
        """缓存AI响应"""
        cache_key = self._generate_response_key(prompt, model, temperature, max_tokens)
        return self.set(cache_key, response, ttl)


    def get_cached_response(self, prompt: str, model: str, temperature: float,
                           max_tokens: int) -> Optional[str]:
        """获取缓存的AI响应"""
        cache_key = self._generate_response_key(prompt, model, temperature, max_tokens)
        return self.get(cache_key)


    def _generate_response_key(self, prompt: str, model: str,
                              temperature: float, max_tokens: int) -> str:
        """生成响应缓存键"""
        key_data = f"{prompt}:{model}:{temperature}:{max_tokens}"
        return f"ai_response:{hashlib.md5(key_data.encode()).hexdigest()}"


    def _evict_entries(self) -> None:
        """清理缓存条目"""
        if not self.cache:
            return

        # 清理10%的条目
        entries_to_remove = max(1, len(self.cache) // 10)

        # 按最近最少使用排序
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1]['last_accessed']
        )

        for i in range(min(entries_to_remove, len(sorted_entries))):
            key = sorted_entries[i][0]
            del self.cache[key]

    def preload_cache(self, preload_data: Dict[str, Any], ttl: Optional[int] = None):
        """预加载缓存数据"""
        with self.cache_lock:
            for key, value in preload_data.items():
                self.set(key, value, ttl)

    def get_memory_usage(self) -> Dict[str, Any]:
        """获取内存使用情况"""
        with self.cache_lock:
            total_size = 0
            entry_count = len(self.cache)

            for entry in self.cache.values():
                # 估算内存使用
                value_size = len(str(entry['value']).encode('utf-8'))
                total_size += value_size

            return {
                "total_entries": entry_count,
                "estimated_memory_bytes": total_size,
                "estimated_memory_mb": round(total_size / (1024 * 1024), 2),
                "average_entry_size": round(total_size / entry_count, 2) if entry_count > 0 else 0
            }

    def cleanup_expired(self) -> int:
        """清理过期条目"""
        with self.cache_lock:
            current_time = time.time()
            expired_keys = []

            for key, entry in self.cache.items():
                if current_time > entry['expires_at']:
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]

            self.stats['cache_size'] = len(self.cache)
            return len(expired_keys)

    def get_cache_efficiency(self) -> Dict[str, Any]:
        """获取缓存效率分析"""
        with self.cache_lock:
            if not self.cache:
                return {"efficiency": "No data"}

            # 分析访问模式
            access_counts = [entry['access_count'] for entry in self.cache.values()]
            ages = [time.time() - entry['created_at'] for entry in self.cache.values()]

            return {
                "hit_rate": self.get_stats()['hit_rate_percent'],
                "avg_access_count": sum(access_counts) / len(access_counts),
                "max_access_count": max(access_counts),
                "avg_age_seconds": sum(ages) / len(ages),
                "oldest_entry_age": max(ages),
                "cache_utilization": len(self.cache) / self.max_size * 100
            }

# 全局实例
cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    return cache_manager
