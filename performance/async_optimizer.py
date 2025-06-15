"""
异步处理优化器
提供异步任务调度、并发控制、协程池管理等功能
"""

import asyncio
import time
import threading
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import logging
import weakref
from concurrent.futures import ThreadPoolExecutor
import functools

logger = logging.getLogger(__name__)

@dataclass
class TaskMetrics:
    """任务执行指标"""
    task_id: str
    task_name: str
    start_time: float
    end_time: Optional[float]
    execution_time: Optional[float]
    status: str  # pending, running, completed, failed, cancelled
    result_size: int = 0
    error_message: Optional[str] = None

class AsyncTaskPool:
    """异步任务池"""
    
    def __init__(self, max_concurrent_tasks: int = 100, max_queue_size: int = 1000):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_queue_size = max_queue_size
        
        # 任务管理
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_queue = asyncio.Queue(maxsize=max_queue_size)
        self.task_metrics: Dict[str, TaskMetrics] = {}
        self.task_history = deque(maxlen=1000)
        
        # 信号量控制并发
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        # 统计信息
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0,
            "avg_execution_time": 0.0,
            "peak_concurrent_tasks": 0
        }
        
        # 工作器状态
        self.workers_running = False
        self.worker_tasks: List[asyncio.Task] = []
        
    async def start_workers(self, num_workers: int = 5):
        """启动工作器"""
        if self.workers_running:
            return
        
        self.workers_running = True
        self.worker_tasks = []
        
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.worker_tasks.append(worker)
        
        logger.info(f"Started {num_workers} async workers")
    
    async def stop_workers(self):
        """停止工作器"""
        self.workers_running = False
        
        # 取消所有工作器
        for worker in self.worker_tasks:
            worker.cancel()
        
        # 等待工作器完成
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        self.worker_tasks.clear()
        logger.info("Stopped async workers")
    
    async def _worker(self, worker_name: str):
        """工作器协程"""
        logger.info(f"Worker {worker_name} started")
        
        try:
            while self.workers_running:
                try:
                    # 从队列获取任务
                    task_item = await asyncio.wait_for(
                        self.task_queue.get(), 
                        timeout=1.0
                    )
                    
                    task_id, coro, callback = task_item
                    
                    # 执行任务
                    await self._execute_task(task_id, coro, callback)
                    
                    # 标记任务完成
                    self.task_queue.task_done()
                    
                except asyncio.TimeoutError:
                    # 队列为空，继续等待
                    continue
                except Exception as e:
                    logger.error(f"Worker {worker_name} error: {e}")
                    
        except asyncio.CancelledError:
            logger.info(f"Worker {worker_name} cancelled")
        except Exception as e:
            logger.error(f"Worker {worker_name} failed: {e}")
        finally:
            logger.info(f"Worker {worker_name} stopped")
    
    async def submit_task(self, coro: Awaitable, task_name: str = "unknown", 
                         callback: Optional[Callable] = None) -> str:
        """提交异步任务"""
        task_id = f"task-{int(time.time() * 1000000)}"
        
        # 创建任务指标
        metrics = TaskMetrics(
            task_id=task_id,
            task_name=task_name,
            start_time=time.time(),
            end_time=None,
            execution_time=None,
            status="pending"
        )
        
        self.task_metrics[task_id] = metrics
        self.stats["total_tasks"] += 1
        
        try:
            # 添加到队列
            await self.task_queue.put((task_id, coro, callback))
            logger.debug(f"Task {task_id} ({task_name}) queued")
            return task_id
            
        except asyncio.QueueFull:
            # 队列满，直接执行
            logger.warning(f"Task queue full, executing {task_id} directly")
            await self._execute_task(task_id, coro, callback)
            return task_id
    
    async def _execute_task(self, task_id: str, coro: Awaitable, 
                           callback: Optional[Callable]):
        """执行单个任务"""
        metrics = self.task_metrics.get(task_id)
        if not metrics:
            return
        
        async with self.semaphore:
            try:
                # 更新状态
                metrics.status = "running"
                metrics.start_time = time.time()
                
                # 更新并发统计
                current_concurrent = len([m for m in self.task_metrics.values() 
                                        if m.status == "running"])
                self.stats["peak_concurrent_tasks"] = max(
                    self.stats["peak_concurrent_tasks"], 
                    current_concurrent
                )
                
                # 执行任务
                result = await coro
                
                # 计算结果大小
                result_size = len(str(result)) if result else 0
                
                # 更新指标
                metrics.end_time = time.time()
                metrics.execution_time = metrics.end_time - metrics.start_time
                metrics.status = "completed"
                metrics.result_size = result_size
                
                # 更新统计
                self.stats["completed_tasks"] += 1
                self._update_avg_execution_time()
                
                # 执行回调
                if callback:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(result)
                        else:
                            callback(result)
                    except Exception as e:
                        logger.error(f"Task callback failed: {e}")
                
                logger.debug(f"Task {task_id} completed in {metrics.execution_time:.3f}s")
                
            except asyncio.CancelledError:
                metrics.status = "cancelled"
                metrics.end_time = time.time()
                self.stats["cancelled_tasks"] += 1
                logger.debug(f"Task {task_id} cancelled")
                
            except Exception as e:
                metrics.status = "failed"
                metrics.end_time = time.time()
                metrics.error_message = str(e)
                self.stats["failed_tasks"] += 1
                logger.error(f"Task {task_id} failed: {e}")
                
            finally:
                # 移动到历史记录
                self.task_history.append(metrics)
                if task_id in self.task_metrics:
                    del self.task_metrics[task_id]
    
    def _update_avg_execution_time(self):
        """更新平均执行时间"""
        completed_tasks = [m for m in self.task_history 
                          if m.status == "completed" and m.execution_time]
        
        if completed_tasks:
            total_time = sum(m.execution_time for m in completed_tasks)
            self.stats["avg_execution_time"] = total_time / len(completed_tasks)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        # 检查运行中的任务
        if task_id in self.task_metrics:
            return asdict(self.task_metrics[task_id])
        
        # 检查历史任务
        for metrics in self.task_history:
            if metrics.task_id == task_id:
                return asdict(metrics)
        
        return None
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """获取任务池统计"""
        running_tasks = len([m for m in self.task_metrics.values() 
                           if m.status == "running"])
        pending_tasks = len([m for m in self.task_metrics.values() 
                           if m.status == "pending"])
        
        return {
            **self.stats,
            "current_running_tasks": running_tasks,
            "current_pending_tasks": pending_tasks,
            "queue_size": self.task_queue.qsize(),
            "workers_running": self.workers_running,
            "worker_count": len(self.worker_tasks)
        }

class ConcurrencyController:
    """并发控制器"""
    
    def __init__(self):
        self.semaphores: Dict[str, asyncio.Semaphore] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self.rate_limiters: Dict[str, 'RateLimiter'] = {}
        
    def get_semaphore(self, name: str, limit: int) -> asyncio.Semaphore:
        """获取信号量"""
        if name not in self.semaphores:
            self.semaphores[name] = asyncio.Semaphore(limit)
        return self.semaphores[name]
    
    def get_lock(self, name: str) -> asyncio.Lock:
        """获取锁"""
        if name not in self.locks:
            self.locks[name] = asyncio.Lock()
        return self.locks[name]
    
    def get_rate_limiter(self, name: str, rate: float, burst: int = 1) -> 'RateLimiter':
        """获取速率限制器"""
        if name not in self.rate_limiters:
            self.rate_limiters[name] = RateLimiter(rate, burst)
        return self.rate_limiters[name]

class RateLimiter:
    """速率限制器"""
    
    def __init__(self, rate: float, burst: int = 1):
        self.rate = rate  # 每秒允许的请求数
        self.burst = burst  # 突发请求数
        self.tokens = burst
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """获取令牌"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # 添加令牌
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            return False
    
    async def wait(self):
        """等待直到可以获取令牌"""
        while not await self.acquire():
            await asyncio.sleep(0.01)

class AsyncOptimizer:
    """异步优化器"""
    
    def __init__(self):
        self.task_pool = AsyncTaskPool()
        self.concurrency_controller = ConcurrencyController()
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
        # 性能监控
        self.performance_metrics = deque(maxlen=1000)
        
    async def start(self):
        """启动优化器"""
        await self.task_pool.start_workers()
        logger.info("Async optimizer started")
    
    async def stop(self):
        """停止优化器"""
        await self.task_pool.stop_workers()
        self.thread_pool.shutdown(wait=True)
        logger.info("Async optimizer stopped")
    
    async def optimize_coroutine(self, coro: Awaitable, timeout: Optional[float] = None):
        """优化协程执行"""
        start_time = time.time()
        
        try:
            if timeout:
                result = await asyncio.wait_for(coro, timeout=timeout)
            else:
                result = await coro
            
            execution_time = time.time() - start_time
            
            # 记录性能指标
            self.performance_metrics.append({
                "type": "coroutine",
                "execution_time": execution_time,
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            self.performance_metrics.append({
                "type": "coroutine",
                "execution_time": execution_time,
                "success": False,
                "error": "timeout",
                "timestamp": datetime.now().isoformat()
            })
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            self.performance_metrics.append({
                "type": "coroutine",
                "execution_time": execution_time,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    async def run_in_thread(self, func: Callable, *args, **kwargs):
        """在线程池中运行阻塞函数"""
        start_time = time.time()
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.thread_pool, 
                functools.partial(func, *args, **kwargs)
            )
            
            execution_time = time.time() - start_time
            
            self.performance_metrics.append({
                "type": "thread_pool",
                "execution_time": execution_time,
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.performance_metrics.append({
                "type": "thread_pool",
                "execution_time": execution_time,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        task_stats = self.task_pool.get_pool_stats()
        
        # 分析性能指标
        successful_metrics = [m for m in self.performance_metrics if m["success"]]
        failed_metrics = [m for m in self.performance_metrics if not m["success"]]
        
        performance_analysis = {
            "total_operations": len(self.performance_metrics),
            "successful_operations": len(successful_metrics),
            "failed_operations": len(failed_metrics),
            "success_rate": len(successful_metrics) / len(self.performance_metrics) if self.performance_metrics else 0,
        }
        
        if successful_metrics:
            execution_times = [m["execution_time"] for m in successful_metrics]
            performance_analysis.update({
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "min_execution_time": min(execution_times),
                "max_execution_time": max(execution_times)
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "task_pool": task_stats,
            "performance": performance_analysis,
            "concurrency": {
                "active_semaphores": len(self.concurrency_controller.semaphores),
                "active_locks": len(self.concurrency_controller.locks),
                "active_rate_limiters": len(self.concurrency_controller.rate_limiters)
            }
        }

# 全局异步优化器实例
async_optimizer = AsyncOptimizer()

async def start_async_optimization():
    """启动异步优化"""
    await async_optimizer.start()

async def stop_async_optimization():
    """停止异步优化"""
    await async_optimizer.stop()

def get_async_optimization_report():
    """获取异步优化报告"""
    return async_optimizer.get_optimization_report()
