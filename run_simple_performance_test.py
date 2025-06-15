#!/usr/bin/env python3
"""
简化版性能优化测试脚本
不依赖外部库，测试核心性能优化功能
"""

import asyncio
import time
import json
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimplePerformanceTest:
    """简化版性能测试"""
    
    def __init__(self):
        self.start_time = time.time()
        self.test_results = {}
        
    async def test_cache_performance(self):
        """测试缓存性能"""
        logger.info("💾 测试缓存性能...")
        
        from performance.cache_manager import cache_manager
        
        # 测试数据
        test_data = {
            f"key_{i}": f"value_{i}" * 100 for i in range(100)
        }
        
        # 写入测试
        start_time = time.time()
        for key, value in test_data.items():
            cache_manager.set(key, value, ttl=300)
        write_time = time.time() - start_time
        
        # 读取测试
        start_time = time.time()
        hits = 0
        for key in test_data.keys():
            if cache_manager.get(key) is not None:
                hits += 1
        read_time = time.time() - start_time
        
        # 命中率测试
        hit_rate = (hits / len(test_data)) * 100
        
        self.test_results["cache"] = {
            "write_time": write_time,
            "read_time": read_time,
            "hit_rate": hit_rate,
            "operations_per_second": len(test_data) / (write_time + read_time)
        }
        
        logger.info(f"   缓存写入时间: {write_time:.3f}s")
        logger.info(f"   缓存读取时间: {read_time:.3f}s")
        logger.info(f"   缓存命中率: {hit_rate:.1f}%")
    
    async def test_database_simulation(self):
        """测试数据库查询模拟"""
        logger.info("💾 测试数据库查询模拟...")
        
        from performance.database_optimizer import record_database_query, get_database_optimization_report
        
        # 模拟各种查询
        queries = [
            ("SELECT * FROM users WHERE id = ?", 0.05),
            ("SELECT * FROM conversations WHERE session_id = ?", 0.08),
            ("INSERT INTO messages (content, timestamp) VALUES (?, ?)", 0.03),
            ("UPDATE users SET last_active = ? WHERE id = ?", 0.04),
            ("SELECT COUNT(*) FROM messages WHERE created_at > ?", 0.12),
            ("SELECT * FROM large_table WHERE complex_condition = ?", 1.5),  # 慢查询
        ]
        
        start_time = time.time()
        
        for i in range(50):
            query, base_time = queries[i % len(queries)]
            execution_time = base_time + (i % 3) * 0.01
            success = i % 20 != 19  # 5%失败率
            
            record_database_query(
                query=query,
                execution_time=execution_time,
                rows_affected=1 if "SELECT" not in query else i % 10,
                success=success,
                error_message=None if success else "Simulated error"
            )
        
        total_time = time.time() - start_time
        
        # 获取优化报告
        db_report = get_database_optimization_report()
        
        self.test_results["database"] = {
            "total_queries": 50,
            "simulation_time": total_time,
            "optimization_report": db_report
        }
        
        logger.info(f"   数据库查询模拟时间: {total_time:.3f}s")
        logger.info(f"   慢查询数量: {len(db_report.get('top_slow_queries', []))}")
    
    async def test_api_simulation(self):
        """测试API性能模拟"""
        logger.info("🌐 测试API性能模拟...")
        
        from performance.api_optimizer import record_api_request, get_api_performance_summary
        
        # 模拟API端点
        endpoints = [
            ("/api/v1/chat", "POST", 0.2),
            ("/api/v1/tools", "GET", 0.1),
            ("/api/v1/memory", "GET", 0.15),
            ("/api/v1/status", "GET", 0.05),
            ("/api/v1/upload", "POST", 0.8),
        ]
        
        start_time = time.time()
        
        for i in range(100):
            endpoint, method, base_time = endpoints[i % len(endpoints)]
            response_time = base_time + (i % 5) * 0.02
            status_code = 200 if i % 15 != 14 else 500  # ~7%错误率
            
            record_api_request(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=status_code,
                request_size=1024 + (i % 10) * 100,
                response_size=2048 + (i % 20) * 200
            )
        
        total_time = time.time() - start_time
        
        # 获取性能摘要
        api_summary = get_api_performance_summary()
        
        self.test_results["api"] = {
            "total_requests": 100,
            "simulation_time": total_time,
            "performance_summary": api_summary
        }
        
        logger.info(f"   API请求模拟时间: {total_time:.3f}s")
        logger.info(f"   平均响应时间: {api_summary.get('request_stats', {}).get('avg_response_time', 0)*1000:.1f}ms")
    
    async def test_async_performance(self):
        """测试异步性能"""
        logger.info("⚡ 测试异步性能...")
        
        # 模拟异步任务
        async def mock_async_task(task_id: int, delay: float):
            await asyncio.sleep(delay)
            return f"Task {task_id} completed"
        
        # 并发执行测试
        start_time = time.time()
        
        tasks = []
        for i in range(20):
            delay = 0.1 + (i % 3) * 0.05
            task = mock_async_task(i, delay)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        concurrent_time = time.time() - start_time
        
        # 串行执行测试
        start_time = time.time()
        
        for i in range(20):
            delay = 0.1 + (i % 3) * 0.05
            await mock_async_task(i, delay)
        
        sequential_time = time.time() - start_time
        
        # 计算性能提升
        performance_improvement = (sequential_time - concurrent_time) / sequential_time * 100
        
        self.test_results["async"] = {
            "concurrent_time": concurrent_time,
            "sequential_time": sequential_time,
            "performance_improvement_percent": performance_improvement,
            "tasks_completed": len(results)
        }
        
        logger.info(f"   并发执行时间: {concurrent_time:.3f}s")
        logger.info(f"   串行执行时间: {sequential_time:.3f}s")
        logger.info(f"   性能提升: {performance_improvement:.1f}%")
    
    async def test_memory_simulation(self):
        """测试内存使用模拟"""
        logger.info("🧠 测试内存使用模拟...")
        
        # 模拟内存密集型操作
        start_time = time.time()
        
        # 创建大量对象
        large_data = []
        for i in range(1000):
            data = {
                "id": i,
                "content": "x" * 1000,  # 1KB字符串
                "metadata": {"timestamp": time.time(), "index": i}
            }
            large_data.append(data)
        
        creation_time = time.time() - start_time
        
        # 模拟数据处理
        start_time = time.time()
        
        processed_data = []
        for item in large_data:
            processed = {
                "processed_id": item["id"] * 2,
                "processed_content": item["content"][:100],  # 截取前100字符
                "processed_at": time.time()
            }
            processed_data.append(processed)
        
        processing_time = time.time() - start_time
        
        # 清理内存
        start_time = time.time()
        del large_data
        del processed_data
        cleanup_time = time.time() - start_time
        
        self.test_results["memory"] = {
            "objects_created": 1000,
            "creation_time": creation_time,
            "processing_time": processing_time,
            "cleanup_time": cleanup_time,
            "total_time": creation_time + processing_time + cleanup_time
        }
        
        logger.info(f"   对象创建时间: {creation_time:.3f}s")
        logger.info(f"   数据处理时间: {processing_time:.3f}s")
        logger.info(f"   内存清理时间: {cleanup_time:.3f}s")
    
    def calculate_performance_score(self) -> float:
        """计算综合性能分数"""
        score = 100.0
        
        # 缓存性能评分（25%）
        cache_results = self.test_results.get("cache", {})
        cache_ops_per_sec = cache_results.get("operations_per_second", 0)
        if cache_ops_per_sec < 1000:  # 期望每秒1000次操作
            score -= (1000 - cache_ops_per_sec) / 1000 * 25
        
        # API性能评分（30%）
        api_results = self.test_results.get("api", {})
        api_summary = api_results.get("performance_summary", {})
        avg_response_time = api_summary.get("request_stats", {}).get("avg_response_time", 0)
        if avg_response_time > 0.5:  # 期望500ms以下
            score -= min(30, (avg_response_time - 0.5) / 0.5 * 30)
        
        # 异步性能评分（25%）
        async_results = self.test_results.get("async", {})
        performance_improvement = async_results.get("performance_improvement_percent", 0)
        if performance_improvement < 80:  # 期望80%以上提升
            score -= (80 - performance_improvement) / 80 * 25
        
        # 内存性能评分（20%）
        memory_results = self.test_results.get("memory", {})
        total_memory_time = memory_results.get("total_time", 0)
        if total_memory_time > 1.0:  # 期望1秒以内
            score -= min(20, (total_memory_time - 1.0) * 20)
        
        return max(0, min(100, score))
    
    def generate_report(self) -> dict:
        """生成测试报告"""
        total_time = time.time() - self.start_time
        performance_score = self.calculate_performance_score()
        
        # 生成建议
        recommendations = []
        
        cache_results = self.test_results.get("cache", {})
        if cache_results.get("hit_rate", 0) < 90:
            recommendations.append("缓存命中率较低，考虑优化缓存策略")
        
        api_results = self.test_results.get("api", {})
        api_summary = api_results.get("performance_summary", {})
        if api_summary.get("request_stats", {}).get("avg_response_time", 0) > 0.3:
            recommendations.append("API响应时间较长，建议优化处理逻辑")
        
        async_results = self.test_results.get("async", {})
        if async_results.get("performance_improvement_percent", 0) < 70:
            recommendations.append("异步性能提升有限，检查并发控制策略")
        
        return {
            "test_timestamp": datetime.now().isoformat(),
            "total_test_time": total_time,
            "performance_score": performance_score,
            "test_results": self.test_results,
            "recommendations": recommendations,
            "summary": {
                "cache_ops_per_second": cache_results.get("operations_per_second", 0),
                "api_avg_response_time_ms": api_summary.get("request_stats", {}).get("avg_response_time", 0) * 1000,
                "async_improvement_percent": async_results.get("performance_improvement_percent", 0),
                "memory_processing_time": self.test_results.get("memory", {}).get("total_time", 0)
            }
        }

async def main():
    """主函数"""
    print("🚀 开始简化版性能优化测试...")
    print("="*60)
    
    try:
        # 创建测试实例
        test = SimplePerformanceTest()
        
        # 运行各项测试
        await test.test_cache_performance()
        await test.test_database_simulation()
        await test.test_api_simulation()
        await test.test_async_performance()
        await test.test_memory_simulation()
        
        # 生成报告
        report = test.generate_report()
        
        # 保存报告
        report_file = f"simple_performance_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 输出结果
        print("\n" + "="*60)
        print("🎉 性能测试完成！")
        print("="*60)
        print(f"📊 综合性能分数: {report['performance_score']:.1f}/100")
        print(f"⏱️ 总测试时间: {report['total_test_time']:.2f}秒")
        print(f"📁 详细报告: {report_file}")
        
        print(f"\n📈 关键指标:")
        summary = report['summary']
        print(f"   💾 缓存操作/秒: {summary['cache_ops_per_second']:.0f}")
        print(f"   🌐 API平均响应时间: {summary['api_avg_response_time_ms']:.1f}ms")
        print(f"   ⚡ 异步性能提升: {summary['async_improvement_percent']:.1f}%")
        print(f"   🧠 内存处理时间: {summary['memory_processing_time']:.3f}s")
        
        if report['recommendations']:
            print(f"\n💡 优化建议:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print("\n✅ 测试成功完成！")
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        logger.error(f"Performance test failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
