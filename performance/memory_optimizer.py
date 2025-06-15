"""
内存优化器
提供内存监控、泄漏检测、垃圾回收优化等功能
"""

import gc
import sys
import time
import threading
import weakref
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import tracemalloc
import psutil
import os

logger = logging.getLogger(__name__)

@dataclass
class MemorySnapshot:
    """内存快照"""
    timestamp: str
    total_memory_mb: float
    available_memory_mb: float
    process_memory_mb: float
    memory_percent: float
    gc_stats: Dict[str, int]
    object_counts: Dict[str, int]
    top_allocations: List[Dict[str, Any]]

class MemoryTracker:
    """内存跟踪器"""
    
    def __init__(self, max_snapshots: int = 100):
        self.max_snapshots = max_snapshots
        self.snapshots = deque(maxlen=max_snapshots)
        self.object_registry: Dict[int, weakref.ref] = {}
        self.allocation_tracking = False
        
        # 内存阈值
        self.memory_warning_threshold = 80.0  # 80%
        self.memory_critical_threshold = 90.0  # 90%
        
        # 监控状态
        self.monitoring_active = False
        self.monitor_thread = None
        self.monitor_interval = 30  # 秒
        
        # 统计信息
        self.stats = {
            "peak_memory_mb": 0.0,
            "memory_warnings": 0,
            "gc_collections": 0,
            "objects_tracked": 0
        }
        
    def start_monitoring(self):
        """开始内存监控"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # 启用内存分配跟踪
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            self.allocation_tracking = True
        
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """停止内存监控"""
        self.monitoring_active = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        if self.allocation_tracking:
            tracemalloc.stop()
            self.allocation_tracking = False
        
        logger.info("Memory monitoring stopped")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                self.take_snapshot()
                self._check_memory_thresholds()
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(self.monitor_interval)
    
    def take_snapshot(self) -> MemorySnapshot:
        """拍摄内存快照"""
        try:
            # 系统内存信息
            memory = psutil.virtual_memory()
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info()
            
            # 垃圾回收统计
            gc_stats = {
                f"generation_{i}": gc.get_count()[i] for i in range(len(gc.get_count()))
            }
            gc_stats["total_collections"] = sum(gc.get_stats()[i]["collections"] for i in range(len(gc.get_stats())))
            
            # 对象计数
            object_counts = self._get_object_counts()
            
            # 内存分配追踪
            top_allocations = []
            if self.allocation_tracking:
                top_allocations = self._get_top_allocations()
            
            snapshot = MemorySnapshot(
                timestamp=datetime.now().isoformat(),
                total_memory_mb=memory.total / (1024 * 1024),
                available_memory_mb=memory.available / (1024 * 1024),
                process_memory_mb=process_memory.rss / (1024 * 1024),
                memory_percent=memory.percent,
                gc_stats=gc_stats,
                object_counts=object_counts,
                top_allocations=top_allocations
            )
            
            self.snapshots.append(snapshot)
            
            # 更新统计
            self.stats["peak_memory_mb"] = max(
                self.stats["peak_memory_mb"], 
                snapshot.process_memory_mb
            )
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to take memory snapshot: {e}")
            return None
    
    def _get_object_counts(self) -> Dict[str, int]:
        """获取对象计数"""
        object_counts = defaultdict(int)
        
        try:
            for obj in gc.get_objects():
                obj_type = type(obj).__name__
                object_counts[obj_type] += 1
        except Exception as e:
            logger.warning(f"Failed to count objects: {e}")
        
        # 返回前10个最多的对象类型
        sorted_counts = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_counts[:10])
    
    def _get_top_allocations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取内存分配排行"""
        try:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            
            allocations = []
            for stat in top_stats[:limit]:
                allocations.append({
                    "filename": stat.traceback.format()[-1] if stat.traceback else "unknown",
                    "size_mb": stat.size / (1024 * 1024),
                    "count": stat.count
                })
            
            return allocations
            
        except Exception as e:
            logger.warning(f"Failed to get allocations: {e}")
            return []
    
    def _check_memory_thresholds(self):
        """检查内存阈值"""
        if not self.snapshots:
            return
        
        latest = self.snapshots[-1]
        
        if latest.memory_percent > self.memory_critical_threshold:
            logger.critical(f"Critical memory usage: {latest.memory_percent:.1f}%")
            self.stats["memory_warnings"] += 1
            self._trigger_emergency_cleanup()
            
        elif latest.memory_percent > self.memory_warning_threshold:
            logger.warning(f"High memory usage: {latest.memory_percent:.1f}%")
            self.stats["memory_warnings"] += 1
            self._trigger_cleanup()
    
    def _trigger_cleanup(self):
        """触发清理"""
        logger.info("Triggering memory cleanup")
        
        # 强制垃圾回收
        collected = gc.collect()
        self.stats["gc_collections"] += 1
        
        logger.info(f"Garbage collection freed {collected} objects")
    
    def _trigger_emergency_cleanup(self):
        """触发紧急清理"""
        logger.warning("Triggering emergency memory cleanup")
        
        # 多次垃圾回收
        for generation in range(3):
            collected = gc.collect()
            self.stats["gc_collections"] += 1
        
        # 清理弱引用
        self._cleanup_weak_references()
        
        logger.warning(f"Emergency cleanup completed")
    
    def _cleanup_weak_references(self):
        """清理弱引用"""
        dead_refs = []
        for obj_id, ref in self.object_registry.items():
            if ref() is None:
                dead_refs.append(obj_id)
        
        for obj_id in dead_refs:
            del self.object_registry[obj_id]
        
        logger.debug(f"Cleaned up {len(dead_refs)} dead weak references")
    
    def register_object(self, obj: Any, name: str = None):
        """注册对象用于跟踪"""
        obj_id = id(obj)
        self.object_registry[obj_id] = weakref.ref(obj)
        self.stats["objects_tracked"] += 1
        
        if name:
            logger.debug(f"Registered object {name} (id: {obj_id})")
    
    def get_memory_analysis(self) -> Dict[str, Any]:
        """获取内存分析"""
        if not self.snapshots:
            return {"error": "No memory snapshots available"}
        
        latest = self.snapshots[-1]
        
        # 计算内存趋势
        if len(self.snapshots) > 1:
            first = self.snapshots[0]
            memory_trend = latest.process_memory_mb - first.process_memory_mb
            time_span = (datetime.fromisoformat(latest.timestamp) - 
                        datetime.fromisoformat(first.timestamp)).total_seconds()
            memory_rate = memory_trend / (time_span / 3600) if time_span > 0 else 0  # MB/hour
        else:
            memory_trend = 0
            memory_rate = 0
        
        # 分析对象增长
        object_growth = {}
        if len(self.snapshots) > 1:
            prev_objects = self.snapshots[-2].object_counts
            curr_objects = latest.object_counts
            
            for obj_type, count in curr_objects.items():
                prev_count = prev_objects.get(obj_type, 0)
                growth = count - prev_count
                if growth > 0:
                    object_growth[obj_type] = growth
        
        return {
            "timestamp": latest.timestamp,
            "current_memory": {
                "process_memory_mb": latest.process_memory_mb,
                "memory_percent": latest.memory_percent,
                "available_memory_mb": latest.available_memory_mb
            },
            "trends": {
                "memory_trend_mb": memory_trend,
                "memory_rate_mb_per_hour": memory_rate,
                "object_growth": object_growth
            },
            "statistics": self.stats,
            "gc_stats": latest.gc_stats,
            "top_objects": latest.object_counts,
            "top_allocations": latest.top_allocations,
            "recommendations": self._generate_recommendations(latest)
        }
    
    def _generate_recommendations(self, snapshot: MemorySnapshot) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if snapshot.memory_percent > 85:
            recommendations.append("内存使用率过高，建议优化内存使用或增加内存")
        
        if snapshot.gc_stats.get("total_collections", 0) > 100:
            recommendations.append("垃圾回收频繁，检查是否有内存泄漏")
        
        # 检查对象数量
        total_objects = sum(snapshot.object_counts.values())
        if total_objects > 100000:
            recommendations.append("对象数量过多，考虑使用对象池或优化数据结构")
        
        # 检查大内存分配
        large_allocations = [a for a in snapshot.top_allocations if a["size_mb"] > 10]
        if large_allocations:
            recommendations.append("发现大内存分配，检查是否可以优化")
        
        return recommendations

class ResourceManager:
    """资源管理器"""
    
    def __init__(self):
        self.resources: Dict[str, Any] = {}
        self.resource_locks: Dict[str, threading.Lock] = {}
        self.cleanup_callbacks: Dict[str, List[callable]] = defaultdict(list)
        
    def register_resource(self, name: str, resource: Any, cleanup_callback: callable = None):
        """注册资源"""
        self.resources[name] = resource
        self.resource_locks[name] = threading.Lock()
        
        if cleanup_callback:
            self.cleanup_callbacks[name].append(cleanup_callback)
        
        logger.debug(f"Registered resource: {name}")
    
    def get_resource(self, name: str) -> Any:
        """获取资源"""
        return self.resources.get(name)
    
    def cleanup_resource(self, name: str) -> bool:
        """清理资源"""
        if name not in self.resources:
            return False
        
        with self.resource_locks[name]:
            try:
                # 执行清理回调
                for callback in self.cleanup_callbacks[name]:
                    try:
                        callback(self.resources[name])
                    except Exception as e:
                        logger.error(f"Resource cleanup callback failed: {e}")
                
                # 移除资源
                del self.resources[name]
                del self.resource_locks[name]
                del self.cleanup_callbacks[name]
                
                logger.debug(f"Cleaned up resource: {name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to cleanup resource {name}: {e}")
                return False
    
    def cleanup_all(self):
        """清理所有资源"""
        resource_names = list(self.resources.keys())
        
        for name in resource_names:
            self.cleanup_resource(name)
        
        logger.info(f"Cleaned up {len(resource_names)} resources")

class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self):
        self.memory_tracker = MemoryTracker()
        self.resource_manager = ResourceManager()
        
        # 优化配置
        self.optimization_config = {
            "auto_gc_threshold": 80.0,  # 内存使用率超过80%时自动GC
            "gc_interval": 300,  # 5分钟
            "cleanup_interval": 600,  # 10分钟
        }
        
        # 优化统计
        self.optimization_stats = {
            "auto_gc_count": 0,
            "memory_freed_mb": 0.0,
            "resources_cleaned": 0
        }
        
    def start_optimization(self):
        """开始内存优化"""
        self.memory_tracker.start_monitoring()
        logger.info("Memory optimization started")
    
    def stop_optimization(self):
        """停止内存优化"""
        self.memory_tracker.stop_monitoring()
        self.resource_manager.cleanup_all()
        logger.info("Memory optimization stopped")
    
    def optimize_memory(self) -> Dict[str, Any]:
        """执行内存优化"""
        start_memory = self._get_current_memory()
        
        # 强制垃圾回收
        collected = gc.collect()
        self.optimization_stats["auto_gc_count"] += 1
        
        # 清理资源
        self.resource_manager.cleanup_all()
        
        end_memory = self._get_current_memory()
        memory_freed = start_memory - end_memory
        self.optimization_stats["memory_freed_mb"] += memory_freed
        
        return {
            "objects_collected": collected,
            "memory_freed_mb": memory_freed,
            "current_memory_mb": end_memory
        }
    
    def _get_current_memory(self) -> float:
        """获取当前内存使用"""
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        memory_analysis = self.memory_tracker.get_memory_analysis()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "memory_analysis": memory_analysis,
            "optimization_stats": self.optimization_stats,
            "resource_count": len(self.resource_manager.resources),
            "configuration": self.optimization_config
        }

# 全局内存优化器实例
memory_optimizer = MemoryOptimizer()

def start_memory_optimization():
    """启动内存优化"""
    memory_optimizer.start_optimization()

def stop_memory_optimization():
    """停止内存优化"""
    memory_optimizer.stop_optimization()

def get_memory_optimization_report():
    """获取内存优化报告"""
    return memory_optimizer.get_optimization_report()

def optimize_memory():
    """执行内存优化"""
    return memory_optimizer.optimize_memory()
