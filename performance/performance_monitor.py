"""
性能监控器

提供系统性能监控、指标收集等功能
"""

import time
import threading
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from collections import deque

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class SystemMetrics:
    """系统指标"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    timestamp: float

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, collection_interval: int = 60, history_size: int = 1000):
        """初始化性能监控器"""
        self.collection_interval = collection_interval
        self.history_size = history_size
        
        # 指标存储
        self.system_metrics_history: deque = deque(maxlen=history_size)
        self.custom_metrics: Dict[str, deque] = {}
        
        # 监控线程
        self.monitor_thread = None
        self.running = False
        self.monitor_lock = threading.Lock()
        
        # 统计信息
        self.stats = {
            'total_metrics_collected': 0,
            'monitoring_uptime_seconds': 0,
            'last_collection_time': 0,
            'is_running': False
        }
        
        # 启动监控
        if PSUTIL_AVAILABLE:
            self.start_monitoring()
    
    def start_monitoring(self):
        """启动性能监控"""
        if self.running or not PSUTIL_AVAILABLE:
            return
        
        self.running = True
        self.stats['is_running'] = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            name="PerformanceMonitor",
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.running = False
        self.stats['is_running'] = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """监控循环"""
        start_time = time.time()
        
        while self.running:
            try:
                # 收集系统指标
                system_metrics = self._collect_system_metrics()
                
                with self.monitor_lock:
                    self.system_metrics_history.append(system_metrics)
                    self.stats['total_metrics_collected'] += 1
                    self.stats['last_collection_time'] = time.time()
                    self.stats['monitoring_uptime_seconds'] = time.time() - start_time
                
                time.sleep(self.collection_interval)
                
            except Exception:
                pass
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        if not PSUTIL_AVAILABLE:
            return SystemMetrics(0, 0, 0, 0, time.time())
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存信息
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / 1024 / 1024
        memory_available_mb = memory.available / 1024 / 1024
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_available_mb=memory_available_mb,
            timestamp=time.time()
        )
    
    def add_metric(self, name: str, value: float, unit: str = ""):
        """添加自定义指标"""
        metric_data = {
            'value': value,
            'timestamp': time.time(),
            'unit': unit
        }
        
        with self.monitor_lock:
            if name not in self.custom_metrics:
                self.custom_metrics[name] = deque(maxlen=self.history_size)
            
            self.custom_metrics[name].append(metric_data)
    
    def get_system_metrics(self, last_n: int = 10) -> List[SystemMetrics]:
        """获取系统指标"""
        with self.monitor_lock:
            return list(self.system_metrics_history)[-last_n:]
    
    def get_current_system_status(self) -> Dict[str, Any]:
        """获取当前系统状态"""
        if not self.system_metrics_history:
            if PSUTIL_AVAILABLE:
                # 实时获取
                latest = self._collect_system_metrics()
            else:
                return {}
        else:
            latest = self.system_metrics_history[-1]
        
        return {
            'cpu_percent': latest.cpu_percent,
            'memory_percent': latest.memory_percent,
            'memory_used_mb': round(latest.memory_used_mb, 2),
            'memory_available_mb': round(latest.memory_available_mb, 2),
            'timestamp': latest.timestamp,
            'status': self._get_system_health_status(latest)
        }
    
    def _get_system_health_status(self, metrics: SystemMetrics) -> str:
        """获取系统健康状态"""
        if metrics.cpu_percent > 90 or metrics.memory_percent > 95:
            return 'critical'
        elif metrics.cpu_percent > 70 or metrics.memory_percent > 80:
            return 'warning'
        else:
            return 'healthy'
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """获取监控统计"""
        return {
            **self.stats,
            'collection_interval_seconds': self.collection_interval,
            'history_size': len(self.system_metrics_history),
            'custom_metrics_count': len(self.custom_metrics),
            'psutil_available': PSUTIL_AVAILABLE
        }

# 全局实例
performance_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器实例"""
    return performance_monitor
