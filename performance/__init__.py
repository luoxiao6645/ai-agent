"""
性能优化模块

提供缓存、连接池、异步处理等性能优化功能
"""

try:
    from .cache_manager import CacheManager, get_cache_manager

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

try:
    from .connection_pool import ConnectionPoolManager, get_connection_pool

    CONNECTION_POOL_AVAILABLE = True
except ImportError:
    CONNECTION_POOL_AVAILABLE = False

try:
    from .async_processor import AsyncProcessor, get_async_processor

    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    from .performance_monitor import PerformanceMonitor, get_performance_monitor

    MONITOR_AVAILABLE = True
except ImportError:
    MONITOR_AVAILABLE = False

try:
    from .optimization_config import OptimizationConfig

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

__all__ = []

# 动态导出可用的组件
if CACHE_AVAILABLE:
    __all__.extend(['CacheManager', 'get_cache_manager'])

if CONNECTION_POOL_AVAILABLE:
    __all__.extend(['ConnectionPoolManager', 'get_connection_pool'])

if ASYNC_AVAILABLE:
    __all__.extend(['AsyncProcessor', 'get_async_processor'])

if MONITOR_AVAILABLE:
    __all__.extend(['PerformanceMonitor', 'get_performance_monitor'])

if CONFIG_AVAILABLE:
    __all__.extend(['OptimizationConfig'])

# 版本信息
__version__ = "1.0.0"
__author__ = "AI Agent Performance Team"
__description__ = "Performance optimization module for multimodal AI agent"

# 可用性检查
PERFORMANCE_AVAILABLE = any([
    CACHE_AVAILABLE,
    CONNECTION_POOL_AVAILABLE,
    ASYNC_AVAILABLE,
    MONITOR_AVAILABLE,
    CONFIG_AVAILABLE
])
