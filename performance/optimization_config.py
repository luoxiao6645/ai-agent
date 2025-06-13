"""
优化配置

提供性能优化相关的配置管理
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import os

@dataclass
class CacheConfig:
    """缓存配置"""
    max_size: int = 1000
    default_ttl: int = 3600
    eviction_policy: str = 'lru'
    enable_persistence: bool = True

@dataclass
class ConnectionPoolConfig:
    """连接池配置"""
    http_pool_size: int = 10
    max_retries: int = 3
    timeout: int = 30

@dataclass
class AsyncProcessorConfig:
    """异步处理器配置"""
    max_workers: int = 4
    queue_size: int = 100

@dataclass
class PerformanceMonitorConfig:
    """性能监控配置"""
    collection_interval: int = 60
    history_size: int = 1000

@dataclass
class OptimizationConfig:
    """优化配置"""
    cache: CacheConfig = None
    connection_pool: ConnectionPoolConfig = None
    async_processor: AsyncProcessorConfig = None
    performance_monitor: PerformanceMonitorConfig = None
    
    # 全局优化开关
    enable_caching: bool = True
    enable_connection_pooling: bool = True
    enable_async_processing: bool = True
    enable_performance_monitoring: bool = True
    
    # 性能优化级别
    optimization_level: str = 'balanced'  # minimal, balanced, aggressive
    
    def __post_init__(self):
        if self.cache is None:
            self.cache = CacheConfig()
        if self.connection_pool is None:
            self.connection_pool = ConnectionPoolConfig()
        if self.async_processor is None:
            self.async_processor = AsyncProcessorConfig()
        if self.performance_monitor is None:
            self.performance_monitor = PerformanceMonitorConfig()
        
        # 根据优化级别调整配置
        self._adjust_config_by_level()
    
    def _adjust_config_by_level(self):
        """根据优化级别调整配置"""
        if self.optimization_level == 'minimal':
            # 最小优化
            self.cache.max_size = 100
            self.cache.default_ttl = 1800
            self.connection_pool.http_pool_size = 5
            self.async_processor.max_workers = 2
            self.async_processor.queue_size = 50
            self.performance_monitor.collection_interval = 300
            
        elif self.optimization_level == 'aggressive':
            # 激进优化
            self.cache.max_size = 5000
            self.cache.default_ttl = 7200
            self.connection_pool.http_pool_size = 20
            self.async_processor.max_workers = 8
            self.async_processor.queue_size = 500
            self.performance_monitor.collection_interval = 30
        
        # balanced级别使用默认配置
    
    @classmethod
    def from_env(cls) -> 'OptimizationConfig':
        """从环境变量创建配置"""
        config = cls()
        
        # 缓存配置
        config.cache.max_size = int(os.getenv('CACHE_MAX_SIZE', config.cache.max_size))
        config.cache.default_ttl = int(os.getenv('CACHE_DEFAULT_TTL', config.cache.default_ttl))
        config.cache.eviction_policy = os.getenv('CACHE_EVICTION_POLICY', config.cache.eviction_policy)
        config.cache.enable_persistence = os.getenv('CACHE_ENABLE_PERSISTENCE', 'true').lower() == 'true'
        
        # 连接池配置
        config.connection_pool.http_pool_size = int(os.getenv('HTTP_POOL_SIZE', config.connection_pool.http_pool_size))
        config.connection_pool.max_retries = int(os.getenv('HTTP_MAX_RETRIES', config.connection_pool.max_retries))
        config.connection_pool.timeout = int(os.getenv('HTTP_TIMEOUT', config.connection_pool.timeout))
        
        # 异步处理器配置
        config.async_processor.max_workers = int(os.getenv('ASYNC_MAX_WORKERS', config.async_processor.max_workers))
        config.async_processor.queue_size = int(os.getenv('ASYNC_QUEUE_SIZE', config.async_processor.queue_size))
        
        # 性能监控配置
        config.performance_monitor.collection_interval = int(os.getenv('MONITOR_INTERVAL', config.performance_monitor.collection_interval))
        config.performance_monitor.history_size = int(os.getenv('MONITOR_HISTORY_SIZE', config.performance_monitor.history_size))
        
        # 全局开关
        config.enable_caching = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
        config.enable_connection_pooling = os.getenv('ENABLE_CONNECTION_POOLING', 'true').lower() == 'true'
        config.enable_async_processing = os.getenv('ENABLE_ASYNC_PROCESSING', 'true').lower() == 'true'
        config.enable_performance_monitoring = os.getenv('ENABLE_PERFORMANCE_MONITORING', 'true').lower() == 'true'
        
        # 优化级别
        config.optimization_level = os.getenv('OPTIMIZATION_LEVEL', config.optimization_level)
        config._adjust_config_by_level()
        
        return config

# 默认配置实例
default_optimization_config = OptimizationConfig.from_env()
