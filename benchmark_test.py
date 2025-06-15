"""
性能基准测试

测试系统各组件的性能表现
"""

import time
import asyncio
import threading
import statistics

from typing import List, Dict, Any

from datetime import datetime
import json

from pathlib import Path

# 导入测试模块
try:
    from performance import (

        get_cache_manager, get_connection_pool, get_async_processor,
        get_performance_monitor
    )
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

try:
    from security import get_input_validator, get_security_logger

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False


class BenchmarkRunner:
    """基准测试运行器"""


    def __init__(self):
        self.results = {}
        self.test_data = self._generate_test_data()


    def _generate_test_data(self) -> Dict[str, Any]:
        """生成测试数据"""
        return {
            'small_text': "Hello, world!",
            'medium_text': "This is a medium-sized text for testing purposes. " * 10,
            'large_text': "This is a large text for performance testing. " * 100,
            'test_prompts': [
                "What is artificial intelligence?",
                "Explain machine learning",
                "How does deep learning work?",
                "What are neural networks?",
                "Describe natural language processing"
            ],
            'test_data_sizes': [100, 1000, 10000, 100000]
        }


    def run_all_benchmarks(self) -> Dict[str, Any]:
        """运行所有基准测试"""
        print("🚀 开始性能基准测试...")

        if PERFORMANCE_AVAILABLE:
            self.results['cache_performance'] = self.benchmark_cache()
            self.results['connection_pool_performance'] = self.benchmark_connection_pool()
            self.results['async_processor_performance'] = self.benchmark_async_processor()
            self.results['performance_monitor_overhead'] = self.benchmark_performance_monitor()

        if SECURITY_AVAILABLE:
            self.results['security_validation_performance'] = self.benchmark_security_validation()

        self.results['system_performance'] = self.benchmark_system_performance()

        # 生成报告
        self._generate_report()

        return self.results


    def benchmark_cache(self) -> Dict[str, Any]:
        """缓存性能测试"""
        print("📦 测试缓存性能...")

        cache_manager = get_cache_manager()
        results = {}

        # 写入性能测试
        write_times = []
        for i in range(1000):
            start_time = time.time()
            cache_manager.set(f"test_key_{i}", f"test_value_{i}")
            write_times.append((time.time() - start_time) * 1000)

        results['write_performance'] = {
            'avg_ms': statistics.mean(write_times),
            'median_ms': statistics.median(write_times),
            'max_ms': max(write_times),
            'min_ms': min(write_times),
            'operations_per_second': 1000 / (sum(write_times) / 1000)
        }

        # 读取性能测试
        read_times = []
        for i in range(1000):
            start_time = time.time()
            cache_manager.get(f"test_key_{i}")
            read_times.append((time.time() - start_time) * 1000)

        results['read_performance'] = {
            'avg_ms': statistics.mean(read_times),
            'median_ms': statistics.median(read_times),
            'max_ms': max(read_times),
            'min_ms': min(read_times),
            'operations_per_second': 1000 / (sum(read_times) / 1000)
        }

        # 缓存命中率测试
        hit_count = 0
        for i in range(1000):
            if cache_manager.get(f"test_key_{i}") is not None:
                hit_count += 1

        results['hit_rate'] = hit_count / 1000 * 100

        return results


    def benchmark_connection_pool(self) -> Dict[str, Any]:
        """连接池性能测试"""
        print("🔗 测试连接池性能...")

        connection_pool = get_connection_pool()
        http_pool = connection_pool.get_http_pool()

        results = {}

        # 连接获取性能测试
        get_times = []
        sessions = []

        for i in range(100):
            start_time = time.time()
            session = http_pool.get_session()
            get_times.append((time.time() - start_time) * 1000)
            sessions.append(session)

        # 归还连接
        for session in sessions:
            http_pool.return_session(session)

        results['connection_acquisition'] = {
            'avg_ms': statistics.mean(get_times),
            'median_ms': statistics.median(get_times),
            'max_ms': max(get_times),
            'min_ms': min(get_times)
        }

        # 并发连接测试


        def concurrent_connection_test():
            start_time = time.time()
            session = http_pool.get_session()
            time.sleep(0.1)  # 模拟使用时间
            http_pool.return_session(session)
            return time.time() - start_time

        threads = []
        concurrent_times = []

        for i in range(20):
            thread = threading.Thread(target=lambda: concurrent_times.append(concurrent_connection_test()))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        results['concurrent_performance'] = {
            'avg_ms': statistics.mean([t * 1000 for t in concurrent_times]),
            'max_ms': max([t * 1000 for t in concurrent_times]),
            'min_ms': min([t * 1000 for t in concurrent_times])
        }

        return results


    def benchmark_async_processor(self) -> Dict[str, Any]:
        """异步处理器性能测试"""
        print("⚡ 测试异步处理器性能...")

        async_processor = get_async_processor()
        results = {}

        # 任务提交性能测试


        def dummy_task(x):
            time.sleep(0.01)  # 模拟工作
            return x * 2

        submit_times = []
        task_ids = []

        for i in range(100):
            start_time = time.time()
            task_id = async_processor.submit_task(dummy_task, i)
            submit_times.append((time.time() - start_time) * 1000)
            task_ids.append(task_id)

        results['task_submission'] = {
            'avg_ms': statistics.mean(submit_times),
            'median_ms': statistics.median(submit_times),
            'operations_per_second': 100 / (sum(submit_times) / 1000)
        }

        # 等待任务完成并测试处理时间
        completion_times = []
        for task_id in task_ids:
            start_time = time.time()
            try:
                async_processor.wait_for_task(task_id, timeout=5)
                completion_times.append((time.time() - start_time) * 1000)
            except:
                pass

        if completion_times:
            results['task_completion'] = {
                'avg_ms': statistics.mean(completion_times),
                'median_ms': statistics.median(completion_times),
                'max_ms': max(completion_times),
                'min_ms': min(completion_times)
            }

        return results


    def benchmark_performance_monitor(self) -> Dict[str, Any]:
        """性能监控开销测试"""
        print("📊 测试性能监控开销...")

        performance_monitor = get_performance_monitor()
        results = {}

        # 指标添加性能测试
        add_times = []
        for i in range(1000):
            start_time = time.time()
            performance_monitor.add_metric(f"test_metric_{i}", i, "count")
            add_times.append((time.time() - start_time) * 1000)

        results['metric_addition'] = {
            'avg_ms': statistics.mean(add_times),
            'median_ms': statistics.median(add_times),
            'operations_per_second': 1000 / (sum(add_times) / 1000)
        }

        # 系统指标收集开销
        collect_times = []
        for i in range(10):
            start_time = time.time()
            performance_monitor.get_current_system_status()
            collect_times.append((time.time() - start_time) * 1000)

        results['system_metrics_collection'] = {
            'avg_ms': statistics.mean(collect_times),
            'max_ms': max(collect_times),
            'min_ms': min(collect_times)
        }

        return results


    def benchmark_security_validation(self) -> Dict[str, Any]:
        """安全验证性能测试"""
        print("🛡️ 测试安全验证性能...")

        input_validator = get_input_validator()
        results = {}

        # 文本验证性能测试
        validation_times = []
        test_texts = [
            self.test_data['small_text'],
            self.test_data['medium_text'],
            self.test_data['large_text']
        ]

        for text in test_texts:
            for i in range(100):
                start_time = time.time()
                input_validator.validate_text_input(text)
                validation_times.append((time.time() - start_time) * 1000)

        results['text_validation'] = {
            'avg_ms': statistics.mean(validation_times),
            'median_ms': statistics.median(validation_times),
            'operations_per_second': len(validation_times) / (sum(validation_times) / 1000)
        }

        return results


    def benchmark_system_performance(self) -> Dict[str, Any]:
        """系统整体性能测试"""
        print("🖥️ 测试系统整体性能...")

        results = {}

        # CPU密集型任务测试


        def cpu_intensive_task():
            start_time = time.time()
            # 计算斐波那契数列


            def fibonacci(n):
                if n <= 1:
                    return n
                return fibonacci(n-1) + fibonacci(n-2)

            fibonacci(25)
            return time.time() - start_time

        cpu_times = []
        for i in range(10):
            cpu_times.append(cpu_intensive_task() * 1000)

        results['cpu_intensive'] = {
            'avg_ms': statistics.mean(cpu_times),
            'median_ms': statistics.median(cpu_times),
            'max_ms': max(cpu_times),
            'min_ms': min(cpu_times)
        }

        # 内存使用测试
        import psutil

        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # 创建大量数据
        large_data = []
        for i in range(10000):
            large_data.append(f"test_data_{i}" * 100)

        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before

        results['memory_usage'] = {
            'before_mb': memory_before,
            'after_mb': memory_after,
            'used_mb': memory_used
        }

        # 清理内存
        del large_data

        return results


    def _generate_report(self):
        """生成测试报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_results': self.results,
            'summary': self._generate_summary()
        }

        # 保存到文件
        report_file = Path('logs') / f'benchmark_report_{int(time.time())}.json'
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📊 测试报告已保存: {report_file}")

        # 打印摘要
        self._print_summary()


    def _generate_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        summary = {}

        if 'cache_performance' in self.results:
            cache_results = self.results['cache_performance']
            summary['cache'] = {
                'read_ops_per_sec': cache_results['read_performance']['operations_per_second'],
                'write_ops_per_sec': cache_results['write_performance']['operations_per_second'],
                'hit_rate': cache_results['hit_rate']
            }

        if 'async_processor_performance' in self.results:
            async_results = self.results['async_processor_performance']
            summary['async_processor'] = {
                'submission_ops_per_sec': async_results['task_submission']['operations_per_second']
            }

        return summary


    def _print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("📊 性能基准测试报告")
        print("="*60)

        if 'cache_performance' in self.results:
            cache = self.results['cache_performance']
            print(f"\n📦 缓存性能:")
            print(f"  读取: {cache['read_performance']['operations_per_second']:.0f} ops/sec")
            print(f"  写入: {cache['write_performance']['operations_per_second']:.0f} ops/sec")
            print(f"  命中率: {cache['hit_rate']:.1f}%")

        if 'connection_pool_performance' in self.results:
            pool = self.results['connection_pool_performance']
            print(f"\n🔗 连接池性能:")
            print(f"  连接获取: {pool['connection_acquisition']['avg_ms']:.2f}ms (平均)")
            print(f"  并发处理: {pool['concurrent_performance']['avg_ms']:.2f}ms (平均)")

        if 'async_processor_performance' in self.results:
            async_proc = self.results['async_processor_performance']
            print(f"\n⚡ 异步处理器性能:")
            print(f"  任务提交: {async_proc['task_submission']['operations_per_second']:.0f} ops/sec")
            if 'task_completion' in async_proc:
                print(f"  任务完成: {async_proc['task_completion']['avg_ms']:.2f}ms (平均)")

        if 'security_validation_performance' in self.results:
            security = self.results['security_validation_performance']
            print(f"\n🛡️ 安全验证性能:")
            print(f"  文本验证: {security['text_validation']['operations_per_second']:.0f} ops/sec")

        if 'system_performance' in self.results:
            system = self.results['system_performance']
            print(f"\n🖥️ 系统性能:")
            print(f"  CPU密集型任务: {system['cpu_intensive']['avg_ms']:.2f}ms (平均)")
            print(f"  内存使用: {system['memory_usage']['used_mb']:.2f}MB")

        print("="*60)


def main():
    """主函数"""
    benchmark = BenchmarkRunner()
    benchmark.run_all_benchmarks()

if __name__ == "__main__":
    main()
