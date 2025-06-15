#!/usr/bin/env python3
"""
错误处理机制检查工具
验证异常处理的完整性和正确性
"""

import ast
import re

from pathlib import Path

from typing import Dict, List, Any

from datetime import datetime


class ErrorHandlingChecker:
    """错误处理检查器"""


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


    def analyze_exception_handling(self):
        """分析异常处理"""
        print("\n🛡️ 分析异常处理...")

        exception_analysis = {
            "files_with_try_except": 0,
            "total_try_blocks": 0,
            "bare_except_blocks": 0,
            "specific_exceptions": 0,
            "finally_blocks": 0,
            "missing_error_handling": [],
            "good_practices": [],
            "bad_practices": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                try:
                    tree = ast.parse(content)
                    file_has_try = False

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Try):
                            file_has_try = True
                            exception_analysis["total_try_blocks"] += 1

                            # 检查except处理
                            for handler in node.handlers:
                                if handler.type is None:
                                    # 裸except
                                    exception_analysis["bare_except_blocks"] += 1
                                    exception_analysis["bad_practices"].append({
                                        "file": str(file_path),
                                        "line": handler.lineno,
                                        "issue": "使用了裸except语句",
                                        "suggestion": "指定具体的异常类型"
                                    })
                                else:
                                    exception_analysis["specific_exceptions"] += 1

                            # 检查finally块
                            if node.finalbody:
                                exception_analysis["finally_blocks"] += 1

                        # 检查可能需要异常处理的函数
                        elif isinstance(node, ast.FunctionDef):
                            # 检查是否有文件操作、网络请求等需要异常处理的代码
                            func_content = ast.get_source_segment(content, node)
                            if func_content:
                                risky_operations = [
                                    'open(', 'requests.', 'urllib.', 'socket.',
                                    'json.loads', 'json.dumps', 'pickle.',
                                    'subprocess.', 'os.system'
                                ]

                                has_risky_ops = any(op in func_content for op in risky_operations)
                                has_try_except = 'try:' in func_content

                                if has_risky_ops and not has_try_except:
                                    exception_analysis["missing_error_handling"].append({
                                        "file": str(file_path),
                                        "function": node.name,
                                        "line": node.lineno,
                                        "issue": "函数包含风险操作但缺少异常处理"
                                    })

                    if file_has_try:
                        exception_analysis["files_with_try_except"] += 1

                except SyntaxError:
                    pass

            except Exception as e:
                print(f"⚠️ 分析失败 {file_path}: {e}")

        self.results["exception_handling"] = exception_analysis

        print(f"📊 异常处理分析结果:")
        print(f"  - 有异常处理的文件: {exception_analysis['files_with_try_except']}")
        print(f"  - try块总数: {exception_analysis['total_try_blocks']}")
        print(f"  - 裸except块: {exception_analysis['bare_except_blocks']}")
        print(f"  - 缺少异常处理的函数: {len(exception_analysis['missing_error_handling'])}")


    def check_logging_in_exceptions(self):
        """检查异常中的日志记录"""
        print("\n📝 检查异常日志记录...")

        logging_analysis = {
            "exceptions_with_logging": 0,
            "exceptions_without_logging": 0,
            "good_logging_practices": [],
            "missing_logging": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                # 查找except块
                in_except_block = False
                except_start_line = 0

                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    if stripped_line.startswith('except'):
                        in_except_block = True
                        except_start_line = i + 1

                    elif in_except_block and (stripped_line.startswith('def ') or
                                            stripped_line.startswith('class ') or
                                            (stripped_line and not line.startswith(' ') and not line.startswith('\t'))):
                        in_except_block = False

                    elif in_except_block:
                        # 检查是否有日志记录
                        if any(log_pattern in stripped_line for log_pattern in
                              ['logger.', 'logging.', 'print(']):
                            logging_analysis["exceptions_with_logging"] += 1

                            if 'logger.error' in stripped_line or 'logger.exception' in stripped_line:
                                logging_analysis["good_logging_practices"].append({
                                    "file": str(file_path),
                                    "line": i + 1,
                                    "practice": "使用了适当的错误日志级别"
                                })
                        elif stripped_line and not stripped_line.startswith('#'):
                            # 有代码但没有日志记录
                            logging_analysis["missing_logging"].append({
                                "file": str(file_path),
                                "line": except_start_line,
                                "issue": "except块中缺少日志记录"
                            })
                            logging_analysis["exceptions_without_logging"] += 1
                            in_except_block = False

            except Exception as e:
                print(f"⚠️ 日志检查失败 {file_path}: {e}")

        self.results["logging_in_exceptions"] = logging_analysis

        print(f"📊 异常日志记录分析:")
        print(f"  - 有日志记录的异常: {logging_analysis['exceptions_with_logging']}")
        print(f"  - 缺少日志记录的异常: {logging_analysis['exceptions_without_logging']}")


    def check_error_propagation(self):
        """检查错误传播机制"""
        print("\n🔄 检查错误传播...")

        propagation_analysis = {
            "functions_that_raise": 0,
            "functions_that_catch_and_reraise": 0,
            "functions_that_swallow_errors": 0,
            "custom_exceptions": 0,
            "error_propagation_issues": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                try:
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            func_content = ast.get_source_segment(content, node)
                            if func_content:
                                # 检查是否有raise语句
                                if 'raise' in func_content:
                                    propagation_analysis["functions_that_raise"] += 1

                                # 检查是否有catch and reraise模式
                                if 'except' in func_content and 'raise' in func_content:
                                    propagation_analysis["functions_that_catch_and_reraise"] += 1

                                # 检查是否有吞没错误的情况（except pass）
                                if re.search(r'except.*:\s*pass', func_content):
                                    propagation_analysis["functions_that_swallow_errors"] += 1
                                    propagation_analysis["error_propagation_issues"].append({
                                        "file": str(file_path),
                                        "function": node.name,
                                        "line": node.lineno,
                                        "issue": "函数吞没了异常（except pass）"
                                    })

                        elif isinstance(node, ast.ClassDef):
                            # 检查自定义异常类
                            if any(isinstance(base, ast.Name) and 'Exception' in base.id
                                  for base in node.bases if isinstance(base, ast.Name)):
                                propagation_analysis["custom_exceptions"] += 1

                except SyntaxError:
                    pass

            except Exception as e:
                print(f"⚠️ 错误传播检查失败 {file_path}: {e}")

        self.results["error_propagation"] = propagation_analysis

        print(f"📊 错误传播分析:")
        print(f"  - 抛出异常的函数: {propagation_analysis['functions_that_raise']}")
        print(f"  - 捕获并重抛的函数: {propagation_analysis['functions_that_catch_and_reraise']}")
        print(f"  - 吞没错误的函数: {propagation_analysis['functions_that_swallow_errors']}")
        print(f"  - 自定义异常类: {propagation_analysis['custom_exceptions']}")


    def check_user_friendly_errors(self):
        """检查用户友好的错误信息"""
        print("\n👥 检查用户友好错误信息...")

        user_error_analysis = {
            "user_facing_errors": 0,
            "technical_errors": 0,
            "good_error_messages": [],
            "poor_error_messages": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines):
                    # 查找错误消息
                    if 'raise' in line and ('Exception' in line or 'Error' in line):
                        error_msg = line.strip()

                        # 检查是否是用户友好的错误信息
                        if any(indicator in error_msg.lower() for indicator in
                              ['用户', '请', '无法', '失败', '错误', '不支持']):
                            user_error_analysis["user_facing_errors"] += 1
                            user_error_analysis["good_error_messages"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "message": error_msg
                            })
                        else:
                            user_error_analysis["technical_errors"] += 1
                            if len(error_msg) < 50:  # 过短的错误信息
                                user_error_analysis["poor_error_messages"].append({
                                    "file": str(file_path),
                                    "line": i + 1,
                                    "message": error_msg,
                                    "issue": "错误信息过于简短或技术性"
                                })

            except Exception as e:
                print(f"⚠️ 用户错误检查失败 {file_path}: {e}")

        self.results["user_friendly_errors"] = user_error_analysis

        print(f"📊 用户友好错误分析:")
        print(f"  - 用户友好错误: {user_error_analysis['user_facing_errors']}")
        print(f"  - 技术性错误: {user_error_analysis['technical_errors']}")
        print(f"  - 需要改进的错误信息: {len(user_error_analysis['poor_error_messages'])}")


    def generate_report(self):
        """生成错误处理报告"""
        print("\n" + "="*60)
        print("🛡️ 错误处理机制分析报告")
        print("="*60)

        # 计算错误处理覆盖率
        exception_handling = self.results["exception_handling"]
        total_files = len(self.python_files)
        coverage_rate = (exception_handling["files_with_try_except"] / total_files) * 100

        print(f"📊 错误处理覆盖率: {coverage_rate:.1f}%")
        print(f"📁 分析文件总数: {total_files}")
        print(f"🛡️ 有异常处理的文件: {exception_handling['files_with_try_except']}")

        # 问题统计
        total_issues = (
            exception_handling["bare_except_blocks"] +
            len(exception_handling["missing_error_handling"]) +
            self.results["error_propagation"]["functions_that_swallow_errors"] +
            len(self.results["user_friendly_errors"]["poor_error_messages"])
        )

        print(f"\n⚠️ 发现的问题:")
        print(f"  - 裸except块: {exception_handling['bare_except_blocks']}")
        print(f"  - 缺少异常处理的函数: {len(exception_handling['missing_error_handling'])}")
        print(f"  - 吞没错误的函数: {self.results['error_propagation']['functions_that_swallow_errors']}")
        print(f"  - 需要改进的错误信息: {len(self.results['user_friendly_errors']['poor_error_messages'])}")
        print(f"  - 总问题数: {total_issues}")

        # 保存详细结果
        self.results["summary"] = {
            "timestamp": datetime.now().isoformat(),
            "total_files": total_files,
            "coverage_rate": coverage_rate,
            "total_issues": total_issues
        }

        import json

        with open("error_handling_report.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 详细报告已保存到: error_handling_report.json")

        return self.results


    def run_analysis(self):
        """运行完整的错误处理分析"""
        self.scan_files()
        self.analyze_exception_handling()
        self.check_logging_in_exceptions()
        self.check_error_propagation()
        self.check_user_friendly_errors()
        return self.generate_report()


def main():
    checker = ErrorHandlingChecker()
    return checker.run_analysis()

if __name__ == "__main__":
    main()
