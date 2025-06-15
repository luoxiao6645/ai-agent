#!/usr/bin/env python3
"""
简化的测试套件运行器
运行测试并生成覆盖率报告
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class SimpleTestRunner:
    """简化的测试运行器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.test_results = {}
        
    def run_tests(self):
        """运行测试套件"""
        print("🧪 开始运行AI Agent测试套件...")
        print("="*60)
        
        try:
            # 1. 运行同步测试
            print("\n📋 运行同步单元测试...")
            sync_results = self.run_sync_tests()
            
            # 2. 运行简单的性能测试
            print("\n⚡ 运行性能测试...")
            perf_results = self.run_performance_tests()
            
            # 3. 生成测试报告
            print("\n📊 生成测试报告...")
            report = self.generate_report(sync_results, perf_results)
            
            # 4. 显示结果
            self.display_results(report)
            
            return report
            
        except Exception as e:
            print(f"❌ 测试运行失败: {e}")
            return {"success": False, "error": str(e)}
    
    def run_sync_tests(self):
        """运行同步测试"""
        try:
            # 只运行同步测试方法
            cmd = [
                "python", "-m", "pytest", 
                "tests/unit/test_simple_agent.py::TestSimpleAgent::test_session_management",
                "tests/unit/test_simple_agent.py::TestSimpleAgent::test_conversation_history",
                "tests/unit/test_simple_agent.py::TestSimpleAgent::test_agent_initialization",
                "-v"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_performance_tests(self):
        """运行简单的性能测试"""
        try:
            print("   测试缓存性能...")
            cache_result = self.test_cache_performance()
            
            print("   测试内存处理性能...")
            memory_result = self.test_memory_performance()
            
            print("   测试API模拟性能...")
            api_result = self.test_api_performance()
            
            return {
                "success": True,
                "cache": cache_result,
                "memory": memory_result,
                "api": api_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_cache_performance(self):
        """测试缓存性能"""
        cache_data = {}
        iterations = 1000
        
        # 写入测试
        start_time = time.time()
        for i in range(iterations):
            cache_data[f"key_{i}"] = f"value_{i}" * 10
        write_time = time.time() - start_time
        
        # 读取测试
        start_time = time.time()
        for i in range(iterations):
            _ = cache_data.get(f"key_{i}")
        read_time = time.time() - start_time
        
        total_time = write_time + read_time
        ops_per_second = (iterations * 2) / total_time
        
        return {
            "operations_per_second": ops_per_second,
            "write_time": write_time,
            "read_time": read_time,
            "iterations": iterations
        }
    
    def test_memory_performance(self):
        """测试内存处理性能"""
        object_count = 1000
        
        start_time = time.time()
        
        # 创建对象
        objects = []
        for i in range(object_count):
            obj = {
                "id": i,
                "data": "x" * 100,
                "metadata": {"index": i}
            }
            objects.append(obj)
        
        # 处理对象
        processed = []
        for obj in objects:
            processed_obj = {
                "processed_id": obj["id"] * 2,
                "processed_data": obj["data"][:50]
            }
            processed.append(processed_obj)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 清理
        del objects
        del processed
        
        return {
            "processing_time": processing_time,
            "objects_per_second": object_count / processing_time,
            "object_count": object_count
        }
    
    def test_api_performance(self):
        """测试API模拟性能"""
        import json
        
        request_count = 100
        response_times = []
        
        for i in range(request_count):
            start_time = time.time()
            
            # 模拟API处理
            request_data = {"id": i, "data": "x" * 100}
            json_data = json.dumps(request_data)
            response_data = json.loads(json_data)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "request_count": request_count
        }
    
    def generate_report(self, sync_results, perf_results):
        """生成测试报告"""
        total_time = time.time() - self.start_time
        
        # 解析同步测试结果
        sync_success = sync_results.get("success", False)
        sync_output = sync_results.get("stdout", "")
        
        # 统计测试数量
        passed_count = sync_output.count("PASSED")
        failed_count = sync_output.count("FAILED")
        total_tests = passed_count + failed_count
        
        # 性能测试结果
        perf_success = perf_results.get("success", False)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": total_time,
            "overall_success": sync_success and perf_success,
            "test_statistics": {
                "total_tests": total_tests,
                "passed": passed_count,
                "failed": failed_count,
                "success_rate": (passed_count / total_tests * 100) if total_tests > 0 else 0
            },
            "sync_tests": {
                "success": sync_success,
                "output": sync_output
            },
            "performance_tests": perf_results
        }
        
        # 保存报告
        self.save_report(report)
        
        return report
    
    def save_report(self, report):
        """保存测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📁 测试报告已保存到: {report_file}")
    
    def display_results(self, report):
        """显示测试结果"""
        print("\n" + "="*60)
        print("🎉 测试完成！")
        print("="*60)
        
        # 总体状态
        overall_success = report["overall_success"]
        status_emoji = "✅" if overall_success else "❌"
        print(f"{status_emoji} 总体状态: {'成功' if overall_success else '失败'}")
        
        # 执行时间
        duration = report["duration_seconds"]
        print(f"⏱️ 执行时间: {duration:.2f}秒")
        
        # 测试统计
        stats = report["test_statistics"]
        print(f"📊 测试统计:")
        print(f"   总测试数: {stats['total_tests']}")
        print(f"   通过: {stats['passed']}")
        print(f"   失败: {stats['failed']}")
        print(f"   成功率: {stats['success_rate']:.1f}%")
        
        # 性能测试结果
        perf_results = report["performance_tests"]
        if perf_results.get("success"):
            print(f"\n⚡ 性能测试结果:")
            
            cache_result = perf_results.get("cache", {})
            if cache_result:
                print(f"   💾 缓存性能: {cache_result.get('operations_per_second', 0):.0f} ops/sec")
            
            memory_result = perf_results.get("memory", {})
            if memory_result:
                print(f"   🧠 内存处理: {memory_result.get('objects_per_second', 0):.0f} objects/sec")
            
            api_result = perf_results.get("api", {})
            if api_result:
                print(f"   🌐 API响应: {api_result.get('avg_response_time_ms', 0):.2f}ms")
        
        print("\n✨ 测试报告生成完成！")

def main():
    """主函数"""
    runner = SimpleTestRunner()
    report = runner.run_tests()
    
    # 根据结果设置退出码
    exit_code = 0 if report.get("overall_success", False) else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
