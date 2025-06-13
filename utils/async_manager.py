"""
异步处理管理器
优化并发处理能力，提升用户体验
"""
import asyncio
import concurrent.futures
import time
from typing import Any, Callable, Dict, List, Optional
import streamlit as st
from datetime import datetime

class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_workers: int = 3):
        """
        初始化异步任务管理器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
        # 初始化任务状态
        if 'async_tasks' not in st.session_state:
            st.session_state.async_tasks = {}
        
        if 'task_results' not in st.session_state:
            st.session_state.task_results = {}
    
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> str:
        """
        提交异步任务
        
        Args:
            task_id: 任务ID
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            任务ID
        """
        future = self.executor.submit(func, *args, **kwargs)
        
        st.session_state.async_tasks[task_id] = {
            'future': future,
            'status': 'running',
            'start_time': time.time(),
            'created_at': datetime.now().isoformat()
        }
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        if task_id not in st.session_state.async_tasks:
            return {'status': 'not_found'}
        
        task = st.session_state.async_tasks[task_id]
        future = task['future']
        
        if future.done():
            if future.exception():
                task['status'] = 'error'
                task['error'] = str(future.exception())
            else:
                task['status'] = 'completed'
                task['result'] = future.result()
                task['end_time'] = time.time()
                task['duration'] = task['end_time'] - task['start_time']
        
        return {
            'status': task['status'],
            'start_time': task['start_time'],
            'created_at': task['created_at'],
            'duration': task.get('duration'),
            'error': task.get('error')
        }
    
    def get_task_result(self, task_id: str) -> Any:
        """获取任务结果"""
        if task_id not in st.session_state.async_tasks:
            return None
        
        task = st.session_state.async_tasks[task_id]
        future = task['future']
        
        if future.done() and not future.exception():
            return future.result()
        
        return None

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self):
        """初始化进度跟踪器"""
        if 'progress_data' not in st.session_state:
            st.session_state.progress_data = {}
    
    def start_progress(self, task_id: str, total_steps: int, description: str = "") -> None:
        """开始进度跟踪"""
        st.session_state.progress_data[task_id] = {
            'total_steps': total_steps,
            'current_step': 0,
            'description': description,
            'start_time': time.time(),
            'status': 'running'
        }
    
    def update_progress(self, task_id: str, step: int, description: str = "") -> None:
        """更新进度"""
        if task_id in st.session_state.progress_data:
            progress = st.session_state.progress_data[task_id]
            progress['current_step'] = step
            if description:
                progress['description'] = description
    
    def complete_progress(self, task_id: str) -> None:
        """完成进度"""
        if task_id in st.session_state.progress_data:
            progress = st.session_state.progress_data[task_id]
            progress['status'] = 'completed'
            progress['end_time'] = time.time()
            progress['duration'] = progress['end_time'] - progress['start_time']
    
    def get_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取进度信息"""
        return st.session_state.progress_data.get(task_id)
    
    def render_progress_bar(self, task_id: str, container=None) -> None:
        """渲染进度条"""
        progress = self.get_progress(task_id)
        if not progress:
            return
        
        if container is None:
            container = st
        
        percentage = progress['current_step'] / progress['total_steps']
        
        container.progress(
            percentage, 
            text=f"{progress['description']} ({progress['current_step']}/{progress['total_steps']})"
        )

# 全局实例
async_manager = AsyncTaskManager()
progress_tracker = ProgressTracker()

def get_async_manager() -> AsyncTaskManager:
    """获取异步任务管理器"""
    return async_manager

def get_progress_tracker() -> ProgressTracker:
    """获取进度跟踪器"""
    return progress_tracker
