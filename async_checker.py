#!/usr/bin/env python3
"""
异步处理正确性检查工具
验证async/await的正确使用和并发安全性
"""

import ast
import re

from pathlib import Path

from typing import Dict, List, Any

from datetime import datetime


class AsyncChecker:
    """异步处理检查器"""


    def __init__(self):
        self.project_root = Path(".")
        self.python_files = []
        self.results = {}


    def scan_files(self):
        """扫描Python文件"""
        print("🔍 扫描Python文件...")

        exclude_patterns = ['__pycache__', '.git', 'venv', 'env']

        for file_path in self.project_root.rglob("*.py"):
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                self.python_files.append(file_path)

        print(f"📁 找到 {len(self.python_files)} 个Python文件")


    def analyze_async_usage(self):
        """分析异步使用情况"""
        print("\n⚡ 分析异步使用情况...")

        async_analysis = {
            "files_with_async": 0,
            "async_functions": 0,
            "await_statements": 0,
            "async_generators": 0,
            "async_context_managers": 0,
            "asyncio_imports": 0,
            "async_patterns": {
                "gather": 0,
                "create_task": 0,
                "run_in_executor": 0,
                "semaphore": 0,
                "lock": 0,
                "queue": 0
            },
            "files_analysis": {}
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                file_has_async = False
                file_async_count = 0
                file_await_count = 0

                try:
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        # 异步函数
                        if isinstance(node, ast.AsyncFunctionDef):
                            async_analysis["async_functions"] += 1
                            file_async_count += 1
                            file_has_async = True

                        # await语句
                        elif isinstance(node, ast.Await):
                            async_analysis["await_statements"] += 1
                            file_await_count += 1
                            file_has_async = True

                        # 异步生成器
                        elif isinstance(node, ast.AsyncFor):
                            async_analysis["async_generators"] += 1
                            file_has_async = True

                        # 异步上下文管理器
                        elif isinstance(node, ast.AsyncWith):
                            async_analysis["async_context_managers"] += 1
                            file_has_async = True

                    # 检查asyncio导入
                    if 'import asyncio' in content or 'from asyncio' in content:

                        async_analysis["asyncio_imports"] += 1

                    # 检查异步模式
                    for pattern, count_key in async_analysis["async_patterns"].items():
                        if pattern in content:
                            async_analysis["async_patterns"][count_key] += content.count(pattern)

                    if file_has_async:
                        async_analysis["files_with_async"] += 1

                    async_analysis["files_analysis"][str(file_path)] = {
                        "has_async": file_has_async,
                        "async_functions": file_async_count,
                        "await_statements": file_await_count
                    }

                except SyntaxError:
                    pass

            except Exception as e:
                print(f"⚠️ 分析失败 {file_path}: {e}")

        self.results["async_usage"] = async_analysis

        print(f"📊 异步使用分析:")
        print(f"  - 使用异步的文件: {async_analysis['files_with_async']}")
        print(f"  - 异步函数总数: {async_analysis['async_functions']}")
        print(f"  - await语句总数: {async_analysis['await_statements']}")
        print(f"  - asyncio导入: {async_analysis['asyncio_imports']}")


    def check_async_await_correctness(self):
        """检查async/await的正确使用"""
        print("\n✅ 检查async/await正确性...")

        correctness_analysis = {
            "correct_usage": [],
            "incorrect_usage": [],
            "missing_await": [],
            "unnecessary_async": [],
            "blocking_calls_in_async": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                try:
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.AsyncFunctionDef):
                            func_content = ast.get_source_segment(content, node)
                            if func_content:
                                # 检查是否有await语句
                                if 'await' not in func_content:
                                    correctness_analysis["unnecessary_async"].append({
                                        "file": str(file_path),
                                        "function": node.name,
                                        "line": node.lineno,
                                        "issue": "异步函数中没有await语句"
                                    })

                                # 检查阻塞调用
                                blocking_patterns = [
                                    'time.sleep', 'requests.get', 'requests.post',
                                    'urllib.request', 'socket.recv', 'input()'
                                ]

                                for pattern in blocking_patterns:
                                    if pattern in func_content and f'await {pattern}' not in func_content:
                                        correctness_analysis["blocking_calls_in_async"].append({
                                            "file": str(file_path),
                                            "function": node.name,
                                            "line": node.lineno,
                                            "issue": f"异步函数中使用了阻塞调用: {pattern}",
                                            "suggestion": "使用异步版本或run_in_executor"
                                        })

                        # 检查可能需要await的调用
                        elif isinstance(node, ast.Call):
                            if hasattr(node.func, 'attr'):
                                func_name = node.func.attr
                                # 常见的异步方法
                                async_methods = [
                                    'arun', 'aclose', 'aenter', 'aexit',
                                    'read', 'write', 'connect', 'send'
                                ]

                                if func_name in async_methods:
                                    # 检查是否在await中
                                    parent = getattr(node, 'parent', None)
                                    if not isinstance(parent, ast.Await):
                                        correctness_analysis["missing_await"].append({
                                            "file": str(file_path),
                                            "line": node.lineno,
                                            "issue": f"可能需要await的调用: {func_name}",
                                            "suggestion": "检查是否需要添加await"
                                        })

                except SyntaxError:
                    pass

            except Exception as e:
                print(f"⚠️ 正确性检查失败 {file_path}: {e}")

        self.results["correctness_analysis"] = correctness_analysis

        print(f"📊 正确性分析:")
        print(f"  - 不必要的async: {len(correctness_analysis['unnecessary_async'])}")
        print(f"  - 可能缺少await: {len(correctness_analysis['missing_await'])}")
        print(f"  - 异步中的阻塞调用: {len(correctness_analysis['blocking_calls_in_async'])}")


    def check_concurrency_safety(self):
        """检查并发安全性"""
        print("\n🔒 检查并发安全性...")

        safety_analysis = {
            "shared_state_access": [],
            "race_condition_risks": [],
            "proper_synchronization": [],
            "resource_management": [],
            "deadlock_risks": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                # 检查共享状态访问
                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    # 检查全局变量修改
                    if re.search(r'global\s+\w+', stripped_line):
                        safety_analysis["shared_state_access"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "issue": "修改全局变量可能导致竞态条件",
                            "code": stripped_line
                        })

                    # 检查同步原语使用
                    sync_patterns = ['asyncio.Lock', 'asyncio.Semaphore', 'asyncio.Event']
                    for pattern in sync_patterns:
                        if pattern in stripped_line:
                            safety_analysis["proper_synchronization"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "practice": f"使用了同步原语: {pattern}"
                            })

                    # 检查资源管理
                    if 'async with' in stripped_line:
                        safety_analysis["resource_management"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "practice": "使用了异步上下文管理器"
                        })

                    # 检查潜在的死锁风险
                    if 'acquire()' in stripped_line and 'await' not in stripped_line:
                        safety_analysis["deadlock_risks"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "issue": "同步acquire可能导致死锁",
                            "suggestion": "使用async with或await acquire()"
                        })

            except Exception as e:
                print(f"⚠️ 安全性检查失败 {file_path}: {e}")

        self.results["safety_analysis"] = safety_analysis

        print(f"📊 安全性分析:")
        print(f"  - 共享状态访问: {len(safety_analysis['shared_state_access'])}")
        print(f"  - 竞态条件风险: {len(safety_analysis['race_condition_risks'])}")
        print(f"  - 正确同步使用: {len(safety_analysis['proper_synchronization'])}")
        print(f"  - 死锁风险: {len(safety_analysis['deadlock_risks'])}")


    def check_performance_patterns(self):
        """检查性能模式"""
        print("\n🚀 检查性能模式...")

        performance_analysis = {
            "good_patterns": [],
            "anti_patterns": [],
            "optimization_opportunities": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    # 好的模式
                    if 'asyncio.gather' in stripped_line:
                        performance_analysis["good_patterns"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "pattern": "使用gather进行并发执行"
                        })

                    if 'asyncio.create_task' in stripped_line:
                        performance_analysis["good_patterns"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "pattern": "使用create_task创建任务"
                        })

                    # 反模式
                    if re.search(r'for.*in.*:\s*await', stripped_line):
                        performance_analysis["anti_patterns"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "issue": "串行await循环",
                            "suggestion": "考虑使用asyncio.gather或create_task"
                        })

                    # 优化机会
                    if 'run_in_executor' in stripped_line:
                        performance_analysis["optimization_opportunities"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "opportunity": "使用了executor，检查是否可以使用纯异步版本"
                        })

            except Exception as e:
                print(f"⚠️ 性能检查失败 {file_path}: {e}")

        self.results["performance_analysis"] = performance_analysis

        print(f"📊 性能分析:")
        print(f"  - 良好模式: {len(performance_analysis['good_patterns'])}")
        print(f"  - 反模式: {len(performance_analysis['anti_patterns'])}")
        print(f"  - 优化机会: {len(performance_analysis['optimization_opportunities'])}")


    def generate_report(self):
        """生成异步处理报告"""
        print("\n" + "="*60)
        print("⚡ 异步处理正确性分析报告")
        print("="*60)

        async_usage = self.results["async_usage"]
        total_files = len(self.python_files)

        # 计算异步覆盖率
        async_coverage = (async_usage["files_with_async"] / total_files) * 100

        print(f"📊 异步覆盖率: {async_coverage:.1f}%")
        print(f"📁 分析文件总数: {total_files}")
        print(f"⚡ 使用异步的文件: {async_usage['files_with_async']}")
        print(f"🔧 异步函数总数: {async_usage['async_functions']}")

        # 问题统计
        total_issues = (
            len(self.results["correctness_analysis"]["unnecessary_async"]) +
            len(self.results["correctness_analysis"]["missing_await"]) +
            len(self.results["correctness_analysis"]["blocking_calls_in_async"]) +
            len(self.results["safety_analysis"]["shared_state_access"]) +
            len(self.results["safety_analysis"]["deadlock_risks"]) +
            len(self.results["performance_analysis"]["anti_patterns"])
        )

        print(f"\n⚠️ 发现的问题:")
        print(f"  - 不必要的async: {len(self.results['correctness_analysis']['unnecessary_async'])}")
        print(f"  - 可能缺少await: {len(self.results['correctness_analysis']['missing_await'])}")
        print(f"  - 异步中的阻塞调用: {len(self.results['correctness_analysis']['blocking_calls_in_async'])}")
        print(f"  - 共享状态风险: {len(self.results['safety_analysis']['shared_state_access'])}")
        print(f"  - 死锁风险: {len(self.results['safety_analysis']['deadlock_risks'])}")
        print(f"  - 性能反模式: {len(self.results['performance_analysis']['anti_patterns'])}")
        print(f"  - 总问题数: {total_issues}")

        # 保存详细结果
        self.results["summary"] = {
            "timestamp": datetime.now().isoformat(),
            "total_files": total_files,
            "async_coverage": async_coverage,
            "total_issues": total_issues
        }

        import json

        with open("async_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 详细报告已保存到: async_analysis_report.json")

        return self.results


    def run_analysis(self):
        """运行完整的异步分析"""
        self.scan_files()
        self.analyze_async_usage()
        self.check_async_await_correctness()
        self.check_concurrency_safety()
        self.check_performance_patterns()
        return self.generate_report()


def main():
    checker = AsyncChecker()
    return checker.run_analysis()

if __name__ == "__main__":
    main()
