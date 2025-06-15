"""
API性能优化器
提供响应时间优化、吞吐量提升、请求压缩等功能
"""

import time
import asyncio
import gzip
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import logging
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class APIMetrics:
    """API指标"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    request_size: int
    response_size: int
    timestamp: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

class ResponseCache:
    """响应缓存"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict] = {}
        self.access_times: Dict[str, float] = {}
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # 检查过期
        if time.time() > entry["expires_at"]:
            self._remove(key)
            return None
        
        # 更新访问时间
        self.access_times[key] = time.time()
        return entry["data"]
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None):
        """设置缓存"""
        if ttl is None:
            ttl = self.default_ttl
        
        # 检查容量
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = {
            "data": data,
            "created_at": time.time(),
            "expires_at": time.time() + ttl
        }
        self.access_times[key] = time.time()
    
    def _remove(self, key: str):
        """移除缓存项"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
    
    def _evict_lru(self):
        """驱逐最久未使用的项"""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove(lru_key)
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        now = time.time()
        expired_count = sum(1 for entry in self.cache.values() if now > entry["expires_at"])
        
        return {
            "total_entries": len(self.cache),
            "expired_entries": expired_count,
            "cache_utilization": len(self.cache) / self.max_size * 100
        }

class RequestCompressor:
    """请求压缩器"""
    
    @staticmethod
    def compress_response(data: str, min_size: int = 1024) -> tuple[bytes, str]:
        """压缩响应数据"""
        if len(data) < min_size:
            return data.encode('utf-8'), 'identity'
        
        try:
            compressed = gzip.compress(data.encode('utf-8'))
            if len(compressed) < len(data) * 0.8:  # 至少压缩20%
                return compressed, 'gzip'
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
        
        return data.encode('utf-8'), 'identity'
    
    @staticmethod
    def should_compress(content_type: str, size: int) -> bool:
        """判断是否应该压缩"""
        compressible_types = [
            'application/json',
            'text/html',
            'text/plain',
            'text/css',
            'application/javascript',
            'text/xml'
        ]
        
        return (
            size > 1024 and  # 大于1KB
            any(ct in content_type for ct in compressible_types)
        )

class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
    
    def is_allowed(self, identifier: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # 清理过期请求
        request_times = self.requests[identifier]
        while request_times and request_times[0] < window_start:
            request_times.popleft()
        
        # 检查限制
        if len(request_times) >= self.max_requests:
            return False
        
        # 记录请求
        request_times.append(now)
        return True
    
    def get_remaining(self, identifier: str) -> int:
        """获取剩余请求数"""
        now = time.time()
        window_start = now - self.window_seconds
        
        request_times = self.requests[identifier]
        current_requests = sum(1 for t in request_times if t >= window_start)
        
        return max(0, self.max_requests - current_requests)

class APIOptimizer:
    """API优化器"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=10000)
        self.response_cache = ResponseCache()
        self.compressor = RequestCompressor()
        self.rate_limiter = RateLimiter()
        
        # 性能统计
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "compressed_responses": 0,
            "rate_limited_requests": 0,
            "total_response_time": 0.0,
            "avg_response_time": 0.0
        }
        
        # 慢端点阈值
        self.slow_endpoint_threshold = 2.0  # 2秒
        self.slow_endpoints = deque(maxlen=100)
        
    def record_request(self, endpoint: str, method: str, response_time: float,
                      status_code: int, request_size: int = 0, response_size: int = 0,
                      user_agent: str = None, ip_address: str = None):
        """记录请求指标"""
        metrics = APIMetrics(
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            request_size=request_size,
            response_size=response_size,
            timestamp=datetime.now().isoformat(),
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        self.metrics_history.append(metrics)
        
        # 更新统计
        self.stats["total_requests"] += 1
        self.stats["total_response_time"] += response_time
        self.stats["avg_response_time"] = self.stats["total_response_time"] / self.stats["total_requests"]
        
        # 检查慢端点
        if response_time > self.slow_endpoint_threshold:
            self.slow_endpoints.append(metrics)
            logger.warning(f"Slow API endpoint: {method} {endpoint} - {response_time:.3f}s")
    
    def cache_response(self, cache_key: str, response_data: Any, ttl: int = 300):
        """缓存响应"""
        self.response_cache.set(cache_key, response_data, ttl)
    
    def get_cached_response(self, cache_key: str) -> Optional[Any]:
        """获取缓存响应"""
        cached = self.response_cache.get(cache_key)
        
        if cached is not None:
            self.stats["cache_hits"] += 1
            return cached
        else:
            self.stats["cache_misses"] += 1
            return None
    
    def generate_cache_key(self, endpoint: str, method: str, params: Dict = None) -> str:
        """生成缓存键"""
        key_data = f"{method}:{endpoint}"
        
        if params:
            # 排序参数以确保一致性
            sorted_params = sorted(params.items())
            params_str = json.dumps(sorted_params, sort_keys=True)
            key_data += f":{params_str}"
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def compress_response_if_needed(self, data: str, content_type: str) -> tuple[bytes, str]:
        """根据需要压缩响应"""
        if self.compressor.should_compress(content_type, len(data)):
            compressed_data, encoding = self.compressor.compress_response(data)
            if encoding == 'gzip':
                self.stats["compressed_responses"] += 1
            return compressed_data, encoding
        
        return data.encode('utf-8'), 'identity'
    
    def check_rate_limit(self, identifier: str) -> bool:
        """检查速率限制"""
        allowed = self.rate_limiter.is_allowed(identifier)
        
        if not allowed:
            self.stats["rate_limited_requests"] += 1
        
        return allowed
    
    def get_endpoint_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """获取端点分析"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 过滤最近的指标
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No recent metrics available"}
        
        # 按端点分组
        endpoint_stats = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0,
            "status_codes": defaultdict(int),
            "methods": defaultdict(int)
        })
        
        for metrics in recent_metrics:
            stats = endpoint_stats[metrics.endpoint]
            stats["count"] += 1
            stats["total_time"] += metrics.response_time
            stats["min_time"] = min(stats["min_time"], metrics.response_time)
            stats["max_time"] = max(stats["max_time"], metrics.response_time)
            stats["status_codes"][metrics.status_code] += 1
            stats["methods"][metrics.method] += 1
        
        # 计算平均时间
        for stats in endpoint_stats.values():
            stats["avg_time"] = stats["total_time"] / stats["count"]
            stats["status_codes"] = dict(stats["status_codes"])
            stats["methods"] = dict(stats["methods"])
        
        # 排序
        sorted_endpoints = sorted(
            endpoint_stats.items(),
            key=lambda x: x[1]["avg_time"],
            reverse=True
        )
        
        return {
            "time_range_hours": hours,
            "total_requests": len(recent_metrics),
            "unique_endpoints": len(endpoint_stats),
            "slowest_endpoints": dict(sorted_endpoints[:10]),
            "fastest_endpoints": dict(sorted_endpoints[-10:])
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        cache_stats = self.response_cache.get_stats()
        
        # 计算缓存命中率
        total_cache_requests = self.stats["cache_hits"] + self.stats["cache_misses"]
        cache_hit_rate = (self.stats["cache_hits"] / total_cache_requests * 100) if total_cache_requests > 0 else 0
        
        # 分析状态码分布
        status_code_dist = defaultdict(int)
        for metrics in self.metrics_history:
            status_code_dist[metrics.status_code] += 1
        
        # 计算错误率
        error_requests = sum(count for code, count in status_code_dist.items() if code >= 400)
        error_rate = (error_requests / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "request_stats": {
                "total_requests": self.stats["total_requests"],
                "avg_response_time": self.stats["avg_response_time"],
                "error_rate_percent": error_rate,
                "rate_limited_requests": self.stats["rate_limited_requests"]
            },
            "cache_stats": {
                **cache_stats,
                "hit_rate_percent": cache_hit_rate,
                "total_hits": self.stats["cache_hits"],
                "total_misses": self.stats["cache_misses"]
            },
            "compression_stats": {
                "compressed_responses": self.stats["compressed_responses"],
                "compression_rate_percent": (self.stats["compressed_responses"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
            },
            "status_code_distribution": dict(status_code_dist),
            "slow_endpoints_count": len(self.slow_endpoints),
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 缓存建议
        cache_hit_rate = (self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"]) * 100) if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0 else 0
        
        if cache_hit_rate < 50:
            recommendations.append("缓存命中率较低，考虑优化缓存策略或增加缓存时间")
        
        # 响应时间建议
        if self.stats["avg_response_time"] > 1.0:
            recommendations.append("平均响应时间较长，建议优化数据库查询或增加缓存")
        
        # 慢端点建议
        if len(self.slow_endpoints) > 10:
            recommendations.append("发现多个慢端点，建议进行性能分析和优化")
        
        # 压缩建议
        compression_rate = (self.stats["compressed_responses"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
        if compression_rate < 30:
            recommendations.append("响应压缩率较低，考虑启用更多内容类型的压缩")
        
        # 错误率建议
        error_requests = sum(1 for m in self.metrics_history if m.status_code >= 400)
        error_rate = (error_requests / len(self.metrics_history) * 100) if self.metrics_history else 0
        
        if error_rate > 5:
            recommendations.append("错误率较高，需要检查API稳定性")
        
        return recommendations

# 全局API优化器实例
api_optimizer = APIOptimizer()

def record_api_request(endpoint: str, method: str, response_time: float, **kwargs):
    """记录API请求（全局函数）"""
    api_optimizer.record_request(endpoint, method, response_time, **kwargs)

def get_api_performance_summary():
    """获取API性能摘要（全局函数）"""
    return api_optimizer.get_performance_summary()

def cache_api_response(cache_key: str, response_data: Any, ttl: int = 300):
    """缓存API响应（全局函数）"""
    api_optimizer.cache_response(cache_key, response_data, ttl)

def get_cached_api_response(cache_key: str):
    """获取缓存的API响应（全局函数）"""
    return api_optimizer.get_cached_response(cache_key)
