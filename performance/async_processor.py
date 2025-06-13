"""
异步处理器

提供异步任务处理、队列管理等功能
"""

import time
import threading
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import queue
import concurrent.futures

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AsyncTask:
    """异步任务"""
    task_id: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = 0
    result: Any = None
    error: Optional[Exception] = None

    def __post_init__(self):
        if self.created_at == 0:
            self.created_at = time.time()

class AsyncProcessor:
    """异步处理器"""
    
    def __init__(self, max_workers: int = 4, queue_size: int = 100):
        """初始化异步处理器"""
        self.max_workers = max_workers
        self.queue_size = queue_size
        
        # 任务队列
        self.task_queue = queue.PriorityQueue(maxsize=queue_size)
        self.tasks: Dict[str, AsyncTask] = {}
        self.task_lock = threading.Lock()
        
        # 线程池
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.worker_threads = []
        
        # 控制标志
        self.running = False
        self.shutdown_event = threading.Event()
        
        # 统计信息
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'cancelled_tasks': 0,
            'active_tasks': 0,
            'queue_size': 0
        }
        
        # 启动工作线程
        self.start()
    
    def start(self):
        """启动异步处理器"""
        if self.running:
            return
        
        self.running = True
        self.shutdown_event.clear()
        
        # 启动工作线程
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"AsyncWorker-{i}",
                daemon=True
            )
            worker.start()
            self.worker_threads.append(worker)
    
    def stop(self, timeout: float = 10.0):
        """停止异步处理器"""
        if not self.running:
            return
        
        self.running = False
        self.shutdown_event.set()
        
        # 等待工作线程结束
        for worker in self.worker_threads:
            worker.join(timeout=timeout)
        
        # 关闭线程池
        self.executor.shutdown(wait=True, timeout=timeout)
        self.worker_threads.clear()
    
    def submit_task(self, func: Callable, *args, priority: TaskPriority = TaskPriority.NORMAL, **kwargs) -> str:
        """提交异步任务"""
        task_id = f"task_{int(time.time() * 1000000)}_{len(self.tasks)}"
        
        task = AsyncTask(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority
        )
        
        with self.task_lock:
            self.tasks[task_id] = task
            self.stats['total_tasks'] += 1
            self.stats['queue_size'] += 1
        
        # 添加到队列（优先级队列，数值越小优先级越高）
        priority_value = 5 - priority.value
        self.task_queue.put((priority_value, time.time(), task))
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        with self.task_lock:
            task = self.tasks.get(task_id)
            return task.status if task else None
    
    def get_task_result(self, task_id: str) -> Any:
        """获取任务结果"""
        with self.task_lock:
            task = self.tasks.get(task_id)
            if not task:
                return None
            
            if task.status == TaskStatus.COMPLETED:
                return task.result
            elif task.status == TaskStatus.FAILED:
                raise task.error
            else:
                return None
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """等待任务完成"""
        start_time = time.time()
        
        while True:
            status = self.get_task_status(task_id)
            
            if status == TaskStatus.COMPLETED:
                return self.get_task_result(task_id)
            elif status == TaskStatus.FAILED:
                raise self.get_task_result(task_id)
            elif status == TaskStatus.CANCELLED:
                raise Exception("Task was cancelled")
            elif status is None:
                raise ValueError(f"Task {task_id} not found")
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} timed out")
            
            time.sleep(0.1)
    
    def _worker_loop(self):
        """工作线程循环"""
        while self.running and not self.shutdown_event.is_set():
            try:
                # 获取任务（超时1秒）
                try:
                    priority, timestamp, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # 更新统计
                with self.task_lock:
                    self.stats['queue_size'] -= 1
                    self.stats['active_tasks'] += 1
                
                # 执行任务
                self._execute_task(task)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except Exception:
                pass
    
    def _execute_task(self, task: AsyncTask):
        """执行任务"""
        task.status = TaskStatus.RUNNING
        
        try:
            result = task.func(*task.args, **task.kwargs)
            task.result = result
            task.status = TaskStatus.COMPLETED
            
            with self.task_lock:
                self.stats['completed_tasks'] += 1
                self.stats['active_tasks'] -= 1
            
        except Exception as e:
            task.error = e
            task.status = TaskStatus.FAILED
            
            with self.task_lock:
                self.stats['failed_tasks'] += 1
                self.stats['active_tasks'] -= 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.task_lock:
            success_rate = 0
            if self.stats['total_tasks'] > 0:
                success_rate = self.stats['completed_tasks'] / self.stats['total_tasks'] * 100
            
            return {
                **self.stats,
                'success_rate': round(success_rate, 2)
            }

# 全局实例
async_processor = AsyncProcessor()

def get_async_processor() -> AsyncProcessor:
    """获取异步处理器实例"""
    return async_processor
