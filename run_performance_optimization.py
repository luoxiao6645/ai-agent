#!/usr/bin/env python3
"""
性能优化测试脚本
运行完整的性能优化流程并生成报告
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

async def run_performance_test():
    """运行性能优化测试"""
    logger.info("🚀 开始性能优化测试...")
    
    try:
        # 导入性能优化组件
        from performance.optimization_manager import optimization_manager
        from performance.benchmark_suite import run_performance_benchmark
        from performance.performance_monitor import performance_monitor
        from performance.cache_manager import cache_manager
        from performance.database_optimizer import record_database_query
        from performance.api_optimizer import record_api_request
        
        # 1. 启动性能优化
        logger.info("📊 启动性能监控和优化...")
        await optimization_manager.start_optimization()
        
        # 等待一段时间让监控收集数据
        await asyncio.sleep(2)
        
        # 2. 运行基准测试
        logger.info("🔧 运行基准测试...")
        benchmark_results = await run_performance_benchmark(iterations=50)
        
        # 3. 模拟一些API请求
        logger.info("🌐 模拟API请求...")
        for i in range(20):
            # 模拟不同的API端点
            endpoints = ["/api/chat", "/api/tools", "/api/memory", "/api/status"]
            methods = ["GET", "POST"]
            
            for endpoint in endpoints:
                for method in methods:
                    # 模拟响应时间
                    response_time = 0.1 + (i % 5) * 0.05  # 0.1-0.35秒
                    status_code = 200 if i % 10 != 9 else 500  # 10%错误率
                    
                    record_api_request(
                        endpoint=endpoint,
                        method=method,
                        response_time=response_time,
                        status_code=status_code,
                        request_size=1024,
                        response_size=2048
                    )
            
            await asyncio.sleep(0.1)
        
        # 4. 模拟数据库查询
        logger.info("💾 模拟数据库查询...")
        queries = [
            "SELECT * FROM users WHERE id = ?",
            "SELECT * FROM conversations WHERE session_id = ?",
            "INSERT INTO messages (content, timestamp) VALUES (?, ?)",
            "UPDATE users SET last_active = ? WHERE id = ?",
            "SELECT COUNT(*) FROM messages WHERE created_at > ?"
        ]
        
        for i in range(30):
            query = queries[i % len(queries)]
            execution_time = 0.05 + (i % 3) * 0.02  # 0.05-0.11秒
            success = i % 15 != 14  # 约7%失败率
            
            record_database_query(
                query=query,
                execution_time=execution_time,
                rows_affected=1 if "SELECT" not in query else 0,
                success=success,
                error_message=None if success else "Connection timeout"
            )
            
            await asyncio.sleep(0.05)
        
        # 5. 测试缓存性能
        logger.info("💾 测试缓存性能...")
        for i in range(50):
            key = f"test_key_{i % 10}"  # 重复键以测试命中率
            value = f"test_value_{i}" * 100  # 较大的值
            
            # 设置缓存
            cache_manager.set(key, value, ttl=300)
            
            # 获取缓存
            cached_value = cache_manager.get(key)
            
            await asyncio.sleep(0.01)
        
        # 6. 等待优化周期运行
        logger.info("⏳ 等待优化周期运行...")
        await asyncio.sleep(5)
        
        # 7. 获取优化报告
        logger.info("📋 生成优化报告...")
        optimization_report = await optimization_manager.get_optimization_report()
        
        # 8. 导出报告
        report_file = optimization_manager.export_optimization_report()
        
        # 9. 生成测试摘要
        test_summary = {
            "test_timestamp": datetime.now().isoformat(),
            "test_duration_seconds": time.time() - start_time,
            "benchmark_results": benchmark_results,
            "optimization_report": optimization_report,
            "report_file": report_file,
            "test_statistics": {
                "api_requests_simulated": 160,  # 4 endpoints * 2 methods * 20 iterations
                "database_queries_simulated": 30,
                "cache_operations": 100,  # 50 sets + 50 gets
                "performance_score": optimization_report.get("performance_score", 0)
            }
        }
        
        # 保存测试摘要
        summary_file = f"performance_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(test_summary, f, indent=2, ensure_ascii=False)
        
        # 10. 停止优化
        await optimization_manager.stop_optimization()
        
        # 输出结果
        print("\n" + "="*60)
        print("🎉 性能优化测试完成！")
        print("="*60)
        print(f"📊 性能评分: {optimization_report.get('performance_score', 0):.1f}/100")
        print(f"📁 详细报告: {report_file}")
        print(f"📋 测试摘要: {summary_file}")
        
        # 显示关键指标
        current_metrics = optimization_report.get("current_metrics", {})
        
        if "api" in current_metrics:
            api_stats = current_metrics["api"].get("request_stats", {})
            print(f"🌐 API平均响应时间: {api_stats.get('avg_response_time', 0)*1000:.1f}ms")
            print(f"🌐 API错误率: {api_stats.get('error_rate_percent', 0):.1f}%")
        
        if "cache" in current_metrics:
            cache_stats = current_metrics["cache"]
            print(f"💾 缓存命中率: {cache_stats.get('hit_rate_percent', 0):.1f}%")
        
        if "memory" in current_metrics:
            memory_stats = current_metrics["memory"].get("memory_analysis", {}).get("current_memory", {})
            print(f"🧠 内存使用率: {memory_stats.get('memory_percent', 0):.1f}%")
        
        # 显示建议
        recommendations = optimization_report.get("recommendations", [])
        if recommendations:
            print(f"\n💡 优化建议:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"   {i}. {rec}")
        
        print("\n✅ 测试成功完成！")
        return test_summary
        
    except Exception as e:
        logger.error(f"❌ 性能测试失败: {e}")
        print(f"\n❌ 测试失败: {e}")
        return None

async def main():
    """主函数"""
    global start_time
    start_time = time.time()
    
    try:
        result = await run_performance_test()
        if result:
            return 0
        else:
            return 1
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n💥 测试出现异常: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
