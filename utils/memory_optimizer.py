"""
内存优化管理器
监控和优化应用内存使用
"""
import gc
import sys
import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import threading
import time

# 尝试导入psutil，如果失败则使用简化版本
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class MemoryOptimizer:
    """内存优化管理器"""
    
    def __init__(self, max_memory_mb: int = 512, cleanup_interval: int = 300):
        """
        初始化内存优化器
        
        Args:
            max_memory_mb: 最大内存使用量(MB)
            cleanup_interval: 清理间隔(秒)
        """
        self.max_memory_mb = max_memory_mb
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = datetime.now()
        
        # 初始化内存监控数据
        if 'memory_stats' not in st.session_state:
            st.session_state.memory_stats = {
                'peak_usage': 0,
                'current_usage': 0,
                'cleanup_count': 0,
                'last_cleanup': None,
                'history': []
            }
    
    def get_memory_usage(self) -> Dict[str, float]:
        """获取当前内存使用情况"""
        try:
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                memory_info = process.memory_info()

                # 内存使用量(MB)
                rss_mb = memory_info.rss / (1024 * 1024)
                vms_mb = memory_info.vms / (1024 * 1024)

                # 系统内存信息
                system_memory = psutil.virtual_memory()

                usage_info = {
                    'rss_mb': round(rss_mb, 2),
                    'vms_mb': round(vms_mb, 2),
                    'percent': round(process.memory_percent(), 2),
                    'system_total_gb': round(system_memory.total / (1024**3), 2),
                    'system_available_gb': round(system_memory.available / (1024**3), 2),
                    'system_percent': system_memory.percent
                }

                # 更新统计
                st.session_state.memory_stats['current_usage'] = rss_mb
                if rss_mb > st.session_state.memory_stats['peak_usage']:
                    st.session_state.memory_stats['peak_usage'] = rss_mb

                return usage_info
            else:
                # 简化版本，使用估算值
                estimated_mb = len(str(st.session_state)) / (1024 * 100)  # 粗略估算

                usage_info = {
                    'rss_mb': round(estimated_mb, 2),
                    'vms_mb': round(estimated_mb * 1.5, 2),
                    'percent': 0,
                    'system_total_gb': 0,
                    'system_available_gb': 0,
                    'system_percent': 0,
                    'note': 'psutil不可用，使用估算值'
                }

                # 更新统计
                st.session_state.memory_stats['current_usage'] = estimated_mb
                if estimated_mb > st.session_state.memory_stats['peak_usage']:
                    st.session_state.memory_stats['peak_usage'] = estimated_mb

                return usage_info

        except Exception as e:
            return {
                'error': str(e),
                'rss_mb': 0,
                'vms_mb': 0,
                'percent': 0
            }
    
    def check_memory_pressure(self) -> bool:
        """检查内存压力"""
        usage = self.get_memory_usage()
        current_mb = usage.get('rss_mb', 0)
        
        return current_mb > self.max_memory_mb
    
    def cleanup_session_state(self) -> int:
        """清理session state中的大对象"""
        cleaned_items = 0
        
        # 清理缓存
        if 'cache_storage' in st.session_state:
            cache_size = len(st.session_state.cache_storage)
            if cache_size > 100:  # 如果缓存项目过多
                # 保留最近的50个缓存项
                sorted_cache = sorted(
                    st.session_state.cache_storage.items(),
                    key=lambda x: x[1].get('timestamp', 0),
                    reverse=True
                )
                
                st.session_state.cache_storage = dict(sorted_cache[:50])
                cleaned_items += cache_size - 50
        
        # 清理对话历史
        if 'messages' in st.session_state:
            messages_count = len(st.session_state.messages)
            if messages_count > 20:  # 保留最近20条消息
                st.session_state.messages = st.session_state.messages[-20:]
                cleaned_items += messages_count - 20
        
        # 清理对话历史记录
        if 'conversation_history' in st.session_state:
            history_count = len(st.session_state.conversation_history)
            if history_count > 10:  # 保留最近10条对话
                st.session_state.conversation_history = st.session_state.conversation_history[-10:]
                cleaned_items += history_count - 10
        
        # 清理临时文件引用
        temp_keys = [key for key in st.session_state.keys() if key.startswith('temp_')]
        for key in temp_keys:
            del st.session_state[key]
            cleaned_items += 1
        
        return cleaned_items
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """强制垃圾回收"""
        # 获取回收前的对象数量
        before_objects = len(gc.get_objects())
        
        # 执行垃圾回收
        collected = gc.collect()
        
        # 获取回收后的对象数量
        after_objects = len(gc.get_objects())
        
        return {
            'collected': collected,
            'before_objects': before_objects,
            'after_objects': after_objects,
            'freed_objects': before_objects - after_objects
        }
    
    def auto_cleanup(self) -> Dict[str, Any]:
        """自动清理内存"""
        now = datetime.now()
        
        # 检查是否需要清理
        if (now - self.last_cleanup).seconds < self.cleanup_interval:
            return {'skipped': True, 'reason': 'Too soon'}
        
        cleanup_result = {
            'timestamp': now.isoformat(),
            'memory_before': self.get_memory_usage(),
            'session_cleaned': 0,
            'gc_result': {},
            'memory_after': {}
        }
        
        # 清理session state
        cleanup_result['session_cleaned'] = self.cleanup_session_state()
        
        # 强制垃圾回收
        cleanup_result['gc_result'] = self.force_garbage_collection()
        
        # 获取清理后的内存使用
        cleanup_result['memory_after'] = self.get_memory_usage()
        
        # 更新统计
        st.session_state.memory_stats['cleanup_count'] += 1
        st.session_state.memory_stats['last_cleanup'] = now.isoformat()
        
        self.last_cleanup = now
        
        return cleanup_result
    
    def get_memory_recommendations(self) -> List[str]:
        """获取内存优化建议"""
        recommendations = []
        usage = self.get_memory_usage()
        current_mb = usage.get('rss_mb', 0)
        
        if current_mb > self.max_memory_mb * 0.8:
            recommendations.append("内存使用接近限制，建议清理缓存")
        
        if len(st.session_state.get('messages', [])) > 15:
            recommendations.append("对话历史较长，建议清理旧消息")
        
        if len(st.session_state.get('cache_storage', {})) > 80:
            recommendations.append("缓存项目过多，建议清理过期缓存")
        
        cache_size_mb = 0
        for entry in st.session_state.get('cache_storage', {}).values():
            cache_size_mb += len(str(entry)) / (1024 * 1024)
        
        if cache_size_mb > 50:
            recommendations.append("缓存占用内存过大，建议减少缓存时间")
        
        if not recommendations:
            recommendations.append("内存使用正常，无需特殊优化")
        
        return recommendations
    
    def monitor_memory_usage(self) -> None:
        """监控内存使用情况"""
        usage = self.get_memory_usage()
        
        # 记录历史数据
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'usage_mb': usage.get('rss_mb', 0),
            'percent': usage.get('percent', 0)
        }
        
        # 保留最近100条记录
        if 'history' not in st.session_state.memory_stats:
            st.session_state.memory_stats['history'] = []
        
        st.session_state.memory_stats['history'].append(history_entry)
        if len(st.session_state.memory_stats['history']) > 100:
            st.session_state.memory_stats['history'] = st.session_state.memory_stats['history'][-100:]
        
        # 自动清理检查
        if self.check_memory_pressure():
            self.auto_cleanup()
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        stats = st.session_state.memory_stats.copy()
        stats['current_usage'] = self.get_memory_usage()
        stats['recommendations'] = self.get_memory_recommendations()
        
        # 计算内存使用趋势
        if len(stats.get('history', [])) > 1:
            recent_usage = [entry['usage_mb'] for entry in stats['history'][-10:]]
            if len(recent_usage) > 1:
                trend = recent_usage[-1] - recent_usage[0]
                stats['trend'] = 'increasing' if trend > 5 else 'decreasing' if trend < -5 else 'stable'
            else:
                stats['trend'] = 'unknown'
        else:
            stats['trend'] = 'unknown'
        
        return stats

class SessionStateManager:
    """Session State管理器"""
    
    @staticmethod
    def get_session_size() -> Dict[str, Any]:
        """获取session state大小信息"""
        total_size = 0
        item_sizes = {}
        
        for key, value in st.session_state.items():
            try:
                size = sys.getsizeof(value)
                total_size += size
                item_sizes[key] = {
                    'size_bytes': size,
                    'size_mb': round(size / (1024 * 1024), 3),
                    'type': type(value).__name__
                }
            except:
                item_sizes[key] = {
                    'size_bytes': 0,
                    'size_mb': 0,
                    'type': type(value).__name__
                }
        
        return {
            'total_size_mb': round(total_size / (1024 * 1024), 3),
            'item_count': len(st.session_state),
            'items': item_sizes
        }
    
    @staticmethod
    def cleanup_large_items(threshold_mb: float = 10) -> List[str]:
        """清理大型session state项目"""
        cleaned_items = []
        session_info = SessionStateManager.get_session_size()
        
        for key, info in session_info['items'].items():
            if info['size_mb'] > threshold_mb and key not in ['memory_stats', 'cache_stats']:
                try:
                    del st.session_state[key]
                    cleaned_items.append(f"{key} ({info['size_mb']:.2f}MB)")
                except:
                    pass
        
        return cleaned_items

# 全局内存优化器实例
memory_optimizer = MemoryOptimizer()

def get_memory_optimizer() -> MemoryOptimizer:
    """获取内存优化器实例"""
    return memory_optimizer
