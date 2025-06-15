"""
基准测试套件
对核心功能模块进行性能基准测试
"""

import asyncio
import time
import statistics
import json
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, asdict
import logging

from .performance_monitor import performance_monitor

logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """基准测试结果"""
    test_name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    std_dev: float
    throughput: float  # operations per second
    success_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: str

class BenchmarkSuite:
    """基准测试套件"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.test_functions: Dict[str, Callable] = {}
        
    def register_test(self, name: str, test_func: Callable):
        """注册测试函数"""
        self.test_functions[name] = test_func
        
    async def run_benchmark(self, test_name: str, iterations: int = 100, 
                          warmup_iterations: int = 10) -> BenchmarkResult:
        """运行单个基准测试"""
        if test_name not in self.test_functions:
            raise ValueError(f"Test '{test_name}' not found")
        
        test_func = self.test_functions[test_name]
        
        logger.info(f"Running benchmark: {test_name} ({iterations} iterations)")
        
        # 预热
        logger.info(f"Warming up ({warmup_iterations} iterations)...")
        for _ in range(warmup_iterations):
            try:
                if asyncio.iscoroutinefunction(test_func):
                    await test_func()
                else:
                    test_func()
            except Exception as e:
                logger.warning(f"Warmup iteration failed: {e}")
        
        # 记录初始性能指标
        initial_metrics = performance_monitor.get_current_metrics()
        
        # 执行测试
        times = []
        successes = 0
        failures = 0
        
        start_time = time.time()
        
        for i in range(iterations):
            iteration_start = time.time()
            
            try:
                if asyncio.iscoroutinefunction(test_func):
                    await test_func()
                else:
                    test_func()
                successes += 1
            except Exception as e:
                failures += 1
                logger.warning(f"Iteration {i+1} failed: {e}")
            
            iteration_time = time.time() - iteration_start
            times.append(iteration_time)
        
        total_time = time.time() - start_time
        
        # 记录最终性能指标
        final_metrics = performance_monitor.get_current_metrics()
        
        # 计算统计信息
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        throughput = iterations / total_time
        success_rate = successes / iterations
        
        # 计算资源使用
        memory_usage = final_metrics.memory_used_mb if final_metrics else 0.0
        cpu_usage = final_metrics.cpu_percent if final_metrics else 0.0
        
        result = BenchmarkResult(
            test_name=test_name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            std_dev=std_dev,
            throughput=throughput,
            success_rate=success_rate,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            timestamp=datetime.now().isoformat()
        )
        
        self.results.append(result)
        
        logger.info(f"Benchmark completed: {test_name}")
        logger.info(f"  Average time: {avg_time*1000:.2f}ms")
        logger.info(f"  Throughput: {throughput:.2f} ops/sec")
        logger.info(f"  Success rate: {success_rate:.2%}")
        
        return result
    
    async def run_all_benchmarks(self, iterations: int = 100) -> List[BenchmarkResult]:
        """运行所有注册的基准测试"""
        logger.info(f"Running all benchmarks ({len(self.test_functions)} tests)")
        
        results = []
        for test_name in self.test_functions:
            try:
                result = await self.run_benchmark(test_name, iterations)
                results.append(result)
            except Exception as e:
                logger.error(f"Benchmark '{test_name}' failed: {e}")
        
        return results
    
    def compare_results(self, baseline_file: str = None) -> Dict[str, Any]:
        """比较基准测试结果"""
        if not self.results:
            return {"error": "No benchmark results available"}
        
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "current_results": {},
            "baseline_results": {},
            "improvements": {}
        }
        
        # 当前结果
        for result in self.results:
            comparison["current_results"][result.test_name] = {
                "avg_time": result.avg_time,
                "throughput": result.throughput,
                "success_rate": result.success_rate,
                "memory_usage_mb": result.memory_usage_mb
            }
        
        # 加载基线结果
        if baseline_file:
            try:
                with open(baseline_file, 'r', encoding='utf-8') as f:
                    baseline_data = json.load(f)
                
                comparison["baseline_results"] = baseline_data.get("results", {})
                
                # 计算改进
                for test_name, current in comparison["current_results"].items():
                    if test_name in comparison["baseline_results"]:
                        baseline = comparison["baseline_results"][test_name]
                        
                        time_improvement = (baseline["avg_time"] - current["avg_time"]) / baseline["avg_time"]
                        throughput_improvement = (current["throughput"] - baseline["throughput"]) / baseline["throughput"]
                        
                        comparison["improvements"][test_name] = {
                            "time_improvement_percent": time_improvement * 100,
                            "throughput_improvement_percent": throughput_improvement * 100,
                            "memory_change_mb": current["memory_usage_mb"] - baseline["memory_usage_mb"]
                        }
                        
            except Exception as e:
                logger.error(f"Failed to load baseline file: {e}")
        
        return comparison
    
    def export_results(self, filename: str = None) -> str:
        """导出基准测试结果"""
        if filename is None:
            filename = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "test_count": len(self.results),
            "results": {result.test_name: asdict(result) for result in self.results},
            "summary": self._generate_summary()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Benchmark results exported to {filename}")
        return filename
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        if not self.results:
            return {}
        
        avg_times = [r.avg_time for r in self.results]
        throughputs = [r.throughput for r in self.results]
        success_rates = [r.success_rate for r in self.results]
        memory_usages = [r.memory_usage_mb for r in self.results]
        
        return {
            "total_tests": len(self.results),
            "overall_avg_time": statistics.mean(avg_times),
            "overall_throughput": statistics.mean(throughputs),
            "overall_success_rate": statistics.mean(success_rates),
            "total_memory_usage": sum(memory_usages),
            "fastest_test": min(self.results, key=lambda r: r.avg_time).test_name,
            "slowest_test": max(self.results, key=lambda r: r.avg_time).test_name,
            "highest_throughput": max(self.results, key=lambda r: r.throughput).test_name
        }

# 创建全局基准测试套件
benchmark_suite = BenchmarkSuite()

# 注册核心功能测试
def register_core_tests():
    """注册核心功能测试"""
    
    # 文本处理测试
    def test_text_processing():
        """测试文本处理性能"""
        # 模拟文本处理
        text = "这是一个测试文本" * 100
        processed = text.upper().lower().strip()
        return len(processed)
    
    # 异步处理测试
    async def test_async_processing():
        """测试异步处理性能"""
        await asyncio.sleep(0.001)  # 模拟异步操作
        return "async_result"
    
    # 内存操作测试
    def test_memory_operations():
        """测试内存操作性能"""
        data = list(range(1000))
        result = [x * 2 for x in data if x % 2 == 0]
        return len(result)
    
    # JSON序列化测试
    def test_json_serialization():
        """测试JSON序列化性能"""
        data = {"test": list(range(100)), "nested": {"key": "value"}}
        serialized = json.dumps(data)
        deserialized = json.loads(serialized)
        return len(serialized)
    
    # 注册测试
    benchmark_suite.register_test("text_processing", test_text_processing)
    benchmark_suite.register_test("async_processing", test_async_processing)
    benchmark_suite.register_test("memory_operations", test_memory_operations)
    benchmark_suite.register_test("json_serialization", test_json_serialization)

# 自动注册核心测试
register_core_tests()

async def run_performance_benchmark(iterations: int = 100) -> Dict[str, Any]:
    """运行性能基准测试"""
    logger.info("Starting performance benchmark suite")
    
    # 启动性能监控
    performance_monitor.start_monitoring()
    
    try:
        # 运行所有基准测试
        results = await benchmark_suite.run_all_benchmarks(iterations)
        
        # 导出结果
        results_file = benchmark_suite.export_results()
        
        # 生成比较报告
        comparison = benchmark_suite.compare_results()
        
        return {
            "success": True,
            "results_count": len(results),
            "results_file": results_file,
            "summary": benchmark_suite._generate_summary(),
            "comparison": comparison
        }
        
    except Exception as e:
        logger.error(f"Benchmark suite failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        # 停止性能监控
        performance_monitor.stop_monitoring()

if __name__ == "__main__":
    async def main():
        result = await run_performance_benchmark()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(main())
