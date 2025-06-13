"""
API调用缓存管理器
实现智能缓存机制，减少重复API调用，提升性能
"""
import hashlib
import json
import time
from typing import Any, Dict, Optional
import streamlit as st
from datetime import datetime

class CacheManager:
    """API调用缓存管理器"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            default_ttl: 默认缓存时间（秒）
        """
        self.default_ttl = default_ttl
        self.cache_key_prefix = "api_cache_"
        
        # 初始化缓存存储
        if 'cache_storage' not in st.session_state:
            st.session_state.cache_storage = {}
        
        if 'cache_stats' not in st.session_state:
            st.session_state.cache_stats = {
                'hits': 0,
                'misses': 0,
                'total_requests': 0,
                'cache_size': 0
            }
    
    def _generate_cache_key(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """生成缓存键"""
        # 创建包含所有参数的字符串
        cache_data = {
            'prompt': prompt.strip().lower(),
            'model': model,
            'temperature': round(temperature, 2),
            'max_tokens': max_tokens
        }
        
        # 生成MD5哈希
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        
        return f"{self.cache_key_prefix}{cache_hash}"
    
    def get_cached_response(self, prompt: str, model: str, temperature: float, max_tokens: int) -> Optional[str]:
        """
        获取缓存的响应
        
        Args:
            prompt: 用户提示
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            
        Returns:
            缓存的响应或None
        """
        cache_key = self._generate_cache_key(prompt, model, temperature, max_tokens)
        
        # 更新统计
        st.session_state.cache_stats['total_requests'] += 1
        
        if cache_key in st.session_state.cache_storage:
            cache_entry = st.session_state.cache_storage[cache_key]
            
            # 检查是否过期
            if self._is_cache_valid(cache_entry):
                st.session_state.cache_stats['hits'] += 1
                return cache_entry['response']
            else:
                # 删除过期缓存
                del st.session_state.cache_storage[cache_key]
        
        st.session_state.cache_stats['misses'] += 1
        return None
    
    def cache_response(self, prompt: str, model: str, temperature: float, max_tokens: int, 
                      response: str, ttl: Optional[int] = None) -> None:
        """
        缓存API响应
        
        Args:
            prompt: 用户提示
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            response: API响应
            ttl: 缓存时间（秒）
        """
        cache_key = self._generate_cache_key(prompt, model, temperature, max_tokens)
        ttl = ttl or self.default_ttl
        
        cache_entry = {
            'response': response,
            'timestamp': time.time(),
            'ttl': ttl,
            'created_at': datetime.now().isoformat()
        }
        
        st.session_state.cache_storage[cache_key] = cache_entry
        st.session_state.cache_stats['cache_size'] = len(st.session_state.cache_storage)
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """检查缓存是否有效"""
        current_time = time.time()
        cache_time = cache_entry['timestamp']
        ttl = cache_entry['ttl']
        
        return (current_time - cache_time) < ttl
    
    def clear_cache(self) -> None:
        """清除所有缓存"""
        st.session_state.cache_storage = {}
        st.session_state.cache_stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'cache_size': 0
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = st.session_state.cache_stats.copy()
        
        # 计算命中率
        if stats['total_requests'] > 0:
            stats['hit_rate'] = round((stats['hits'] / stats['total_requests']) * 100, 2)
        else:
            stats['hit_rate'] = 0
        
        return stats
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取详细的缓存信息"""
        info = {
            'total_entries': len(st.session_state.cache_storage),
            'stats': self.get_cache_stats(),
            'recent_entries': []
        }
        
        # 获取最近的缓存条目
        sorted_entries = sorted(
            st.session_state.cache_storage.items(),
            key=lambda x: x[1]['timestamp'],
            reverse=True
        )
        
        for key, entry in sorted_entries[:5]:
            info['recent_entries'].append({
                'key': key[-8:],  # 只显示最后8位
                'created_at': entry['created_at'],
                'response_length': len(entry['response']),
                'valid': self._is_cache_valid(entry)
            })
        
        return info

# 全局缓存管理器实例
cache_manager = CacheManager()

def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    return cache_manager
