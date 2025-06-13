"""
连接池管理器

提供HTTP连接池等资源管理功能
"""

import time
import threading
from typing import Dict, Any
import queue
import requests
from requests.adapters import HTTPAdapter

class HTTPConnectionPool:
    """HTTP连接池"""
    
    def __init__(self, pool_size: int = 10, max_retries: int = 3, timeout: int = 30):
        """初始化HTTP连接池"""
        self.pool_size = pool_size
        self.max_retries = max_retries
        self.timeout = timeout
        
        # 创建会话池
        self.session_pool = queue.Queue(maxsize=pool_size)
        self.pool_lock = threading.Lock()
        
        # 统计信息
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'idle_connections': 0,
            'failed_connections': 0,
            'total_requests': 0,
            'avg_response_time': 0.0
        }
        
        # 初始化连接池
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化连接池"""
        for _ in range(self.pool_size):
            session = self._create_session()
            self.session_pool.put(session)
            self.stats['total_connections'] += 1
            self.stats['idle_connections'] += 1
    
    def _create_session(self) -> requests.Session:
        """创建HTTP会话"""
        session = requests.Session()
        
        adapter = HTTPAdapter(
            pool_connections=self.pool_size,
            pool_maxsize=self.pool_size,
            max_retries=self.max_retries
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.timeout = self.timeout
        
        return session
    
    def get_session(self) -> requests.Session:
        """获取会话"""
        try:
            session = self.session_pool.get(timeout=5)
            with self.pool_lock:
                self.stats['active_connections'] += 1
                self.stats['idle_connections'] -= 1
            return session
        except queue.Empty:
            # 池已满，创建临时会话
            return self._create_session()
    
    def return_session(self, session: requests.Session):
        """归还会话"""
        try:
            self.session_pool.put(session, timeout=1)
            with self.pool_lock:
                self.stats['active_connections'] -= 1
                self.stats['idle_connections'] += 1
        except queue.Full:
            # 池已满，关闭会话
            session.close()
    
    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """发送HTTP请求"""
        session = self.get_session()
        start_time = time.time()
        
        try:
            response = session.request(method, url, **kwargs)
            
            # 更新统计
            response_time = time.time() - start_time
            with self.pool_lock:
                self.stats['total_requests'] += 1
                if self.stats['total_requests'] == 1:
                    self.stats['avg_response_time'] = response_time
                else:
                    self.stats['avg_response_time'] = (
                        (self.stats['avg_response_time'] * (self.stats['total_requests'] - 1) + response_time) 
                        / self.stats['total_requests']
                    )
            
            return response
            
        except Exception as e:
            with self.pool_lock:
                self.stats['failed_connections'] += 1
            raise
        finally:
            self.return_session(session)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计"""
        with self.pool_lock:
            success_rate = 0
            if self.stats['total_requests'] > 0:
                success_rate = (self.stats['total_requests'] - self.stats['failed_connections']) / self.stats['total_requests'] * 100
            
            return {
                **self.stats,
                'avg_response_time_ms': round(self.stats['avg_response_time'] * 1000, 2),
                'success_rate': round(success_rate, 2)
            }
    
    def close(self):
        """关闭连接池"""
        while not self.session_pool.empty():
            try:
                session = self.session_pool.get_nowait()
                session.close()
            except queue.Empty:
                break

class ConnectionPoolManager:
    """连接池管理器"""
    
    def __init__(self):
        """初始化连接池管理器"""
        self.http_pools: Dict[str, HTTPConnectionPool] = {}
        self.pool_lock = threading.Lock()
        
        # 默认HTTP连接池
        self.default_http_pool = HTTPConnectionPool()
        self.http_pools['default'] = self.default_http_pool
    
    def get_http_pool(self, name: str = 'default') -> HTTPConnectionPool:
        """获取HTTP连接池"""
        with self.pool_lock:
            if name not in self.http_pools:
                self.http_pools[name] = HTTPConnectionPool()
            return self.http_pools[name]
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有连接池统计"""
        with self.pool_lock:
            stats = {}
            for name, pool in self.http_pools.items():
                stats[f'http_pool_{name}'] = pool.get_stats()
            return stats
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            'status': 'healthy',
            'pools': {}
        }
        
        with self.pool_lock:
            for name, pool in self.http_pools.items():
                pool_stats = pool.get_stats()
                pool_health = {
                    'status': 'healthy',
                    'success_rate': pool_stats['success_rate']
                }
                
                if pool_stats['success_rate'] < 90:
                    pool_health['status'] = 'degraded'
                    health_status['status'] = 'degraded'
                
                health_status['pools'][name] = pool_health
        
        return health_status
    
    def close_all(self):
        """关闭所有连接池"""
        with self.pool_lock:
            for pool in self.http_pools.values():
                pool.close()
            self.http_pools.clear()

# 全局实例
connection_pool_manager = ConnectionPoolManager()

def get_connection_pool() -> ConnectionPoolManager:
    """获取连接池管理器实例"""
    return connection_pool_manager
