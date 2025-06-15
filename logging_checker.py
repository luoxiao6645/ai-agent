#!/usr/bin/env python3
"""
日志记录规范性检查工具
验证日志级别、格式和安全性
"""

import re
import ast

from pathlib import Path

from typing import Dict, List, Any

from datetime import datetime


class LoggingChecker:
    """日志记录检查器"""


    def __init__(self):
        self.project_root = Path(".")
        self.python_files = []
        self.results = {}

        # 日志级别
        self.log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

        # 敏感信息模式
        self.sensitive_patterns = [
            r'password\s*=\s*["\'].*["\']',
            r'token\s*=\s*["\'].*["\']',
            r'key\s*=\s*["\'].*["\']',
            r'secret\s*=\s*["\'].*["\']',
            r'api_key\s*=\s*["\'].*["\']',
            r'access_token\s*=\s*["\'].*["\']'
        ]


    def scan_files(self):
        """扫描Python文件"""
        print("🔍 扫描Python文件...")

        exclude_patterns = ['__pycache__', '.git', 'venv', 'env']

        for file_path in self.project_root.rglob("*.py"):
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                self.python_files.append(file_path)

        print(f"📁 找到 {len(self.python_files)} 个Python文件")


    def analyze_logging_usage(self):
        """分析日志使用情况"""
        print("\n📝 分析日志使用情况...")

        logging_analysis = {
            "files_with_logging": 0,
            "total_log_statements": 0,
            "log_level_distribution": {level: 0 for level in self.log_levels},
            "logging_imports": 0,
            "print_statements": 0,
            "files_using_print": 0,
            "logger_configurations": 0,
            "log_statements_by_file": {}
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                file_has_logging = False
                file_has_print = False
                file_log_count = 0
                file_print_count = 0

                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    # 检查logging导入
                    if re.search(r'import\s+logging|from\s+logging', stripped_line):
                        logging_analysis["logging_imports"] += 1

                    # 检查logger配置
                    if 'logging.basicConfig' in stripped_line or 'getLogger' in stripped_line:
                        logging_analysis["logger_configurations"] += 1

                    # 检查日志语句
                    for level in self.log_levels:
                        if f'logger.{level.lower()}' in stripped_line or f'logging.{level.lower()}' in stripped_line:
                            logging_analysis["total_log_statements"] += 1
                            logging_analysis["log_level_distribution"][level] += 1
                            file_has_logging = True
                            file_log_count += 1

                    # 检查print语句
                    if re.search(r'\bprint\s*\(', stripped_line) and not stripped_line.startswith('#'):
                        logging_analysis["print_statements"] += 1
                        file_has_print = True
                        file_print_count += 1

                if file_has_logging:
                    logging_analysis["files_with_logging"] += 1

                if file_has_print:
                    logging_analysis["files_using_print"] += 1

                logging_analysis["log_statements_by_file"][str(file_path)] = {
                    "log_statements": file_log_count,
                    "print_statements": file_print_count
                }

            except Exception as e:
                print(f"⚠️ 分析失败 {file_path}: {e}")

        self.results["logging_usage"] = logging_analysis

        print(f"📊 日志使用分析:")
        print(f"  - 使用日志的文件: {logging_analysis['files_with_logging']}")
        print(f"  - 日志语句总数: {logging_analysis['total_log_statements']}")
        print(f"  - 使用print的文件: {logging_analysis['files_using_print']}")
        print(f"  - print语句总数: {logging_analysis['print_statements']}")


    def check_log_level_appropriateness(self):
        """检查日志级别的合理性"""
        print("\n📊 检查日志级别合理性...")

        level_analysis = {
            "appropriate_usage": [],
            "questionable_usage": [],
            "missing_error_logs": [],
            "excessive_debug_logs": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                debug_count = 0

                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    # 检查DEBUG级别使用
                    if 'logger.debug' in stripped_line or 'logging.debug' in stripped_line:
                        debug_count += 1
                        if debug_count > 10:  # 过多的debug日志
                            level_analysis["excessive_debug_logs"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "issue": "文件中DEBUG日志过多"
                            })

                    # 检查异常处理中是否有错误日志
                    if stripped_line.startswith('except'):
                        # 查看接下来几行是否有错误日志
                        has_error_log = False
                        for j in range(i + 1, min(i + 5, len(lines))):
                            next_line = lines[j].strip()
                            if ('logger.error' in next_line or 'logger.exception' in next_line or
                                'logging.error' in next_line or 'logging.exception' in next_line):
                                has_error_log = True
                                level_analysis["appropriate_usage"].append({
                                    "file": str(file_path),
                                    "line": j + 1,
                                    "practice": "在异常处理中使用了错误日志"
                                })
                                break

                        if not has_error_log:
                            level_analysis["missing_error_logs"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "issue": "异常处理中缺少错误日志"
                            })

                    # 检查INFO级别的合理使用
                    if 'logger.info' in stripped_line or 'logging.info' in stripped_line:
                        # 检查是否在重要操作中使用
                        if any(keyword in stripped_line.lower() for keyword in
                              ['started', 'completed', 'initialized', 'success', '成功', '开始', '完成']):
                            level_analysis["appropriate_usage"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "practice": "在重要操作中使用了INFO日志"
                            })

            except Exception as e:
                print(f"⚠️ 日志级别检查失败 {file_path}: {e}")

        self.results["log_level_analysis"] = level_analysis

        print(f"📊 日志级别分析:")
        print(f"  - 合理使用: {len(level_analysis['appropriate_usage'])}")
        print(f"  - 可疑使用: {len(level_analysis['questionable_usage'])}")
        print(f"  - 缺少错误日志: {len(level_analysis['missing_error_logs'])}")
        print(f"  - DEBUG日志过多: {len(level_analysis['excessive_debug_logs'])}")


    def check_sensitive_information(self):
        """检查敏感信息泄露"""
        print("\n🔒 检查敏感信息泄露...")

        security_analysis = {
            "potential_leaks": [],
            "safe_logging": [],
            "files_with_risks": 0
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                file_has_risks = False

                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    # 检查日志语句中的敏感信息
                    if any(log_pattern in stripped_line for log_pattern in
                          ['logger.', 'logging.', 'print(']):

                        # 检查敏感信息模式
                        for pattern in self.sensitive_patterns:
                            if re.search(pattern, stripped_line, re.IGNORECASE):
                                security_analysis["potential_leaks"].append({
                                    "file": str(file_path),
                                    "line": i + 1,
                                    "code": stripped_line,
                                    "risk": "可能泄露敏感信息"
                                })
                                file_has_risks = True

                        # 检查是否有安全的日志记录实践
                        if any(safe_pattern in stripped_line.lower() for safe_pattern in
                              ['***', 'masked', 'hidden', '隐藏', '掩码']):
                            security_analysis["safe_logging"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "practice": "使用了安全的日志记录方式"
                            })

                if file_has_risks:
                    security_analysis["files_with_risks"] += 1

            except Exception as e:
                print(f"⚠️ 安全检查失败 {file_path}: {e}")

        self.results["security_analysis"] = security_analysis

        print(f"📊 安全分析:")
        print(f"  - 潜在泄露风险: {len(security_analysis['potential_leaks'])}")
        print(f"  - 安全日志实践: {len(security_analysis['safe_logging'])}")
        print(f"  - 有风险的文件: {security_analysis['files_with_risks']}")


    def check_log_format_consistency(self):
        """检查日志格式一致性"""
        print("\n📐 检查日志格式一致性...")

        format_analysis = {
            "consistent_formats": 0,
            "inconsistent_formats": 0,
            "format_issues": [],
            "good_practices": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                log_formats = []

                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    # 查找日志格式配置
                    if 'format=' in stripped_line and 'logging' in stripped_line:
                        log_formats.append({
                            "file": str(file_path),
                            "line": i + 1,
                            "format": stripped_line
                        })

                    # 检查日志消息格式
                    if any(log_pattern in stripped_line for log_pattern in
                          ['logger.', 'logging.']):

                        # 检查是否包含上下文信息
                        if any(context in stripped_line for context in
                              ['%s', '{', 'f"', "f'"]):
                            format_analysis["good_practices"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "practice": "日志消息包含上下文信息"
                            })

                        # 检查硬编码的日志消息
                        if re.search(r'logger\.\w+\s*\(\s*["\'][^"\']*["\']\s*\)', stripped_line):
                            format_analysis["format_issues"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "issue": "使用了硬编码的日志消息",
                                "suggestion": "考虑添加上下文信息"
                            })

            except Exception as e:
                print(f"⚠️ 格式检查失败 {file_path}: {e}")

        self.results["format_analysis"] = format_analysis

        print(f"📊 格式分析:")
        print(f"  - 良好实践: {len(format_analysis['good_practices'])}")
        print(f"  - 格式问题: {len(format_analysis['format_issues'])}")


    def generate_report(self):
        """生成日志记录报告"""
        print("\n" + "="*60)
        print("📝 日志记录规范性分析报告")
        print("="*60)

        logging_usage = self.results["logging_usage"]
        total_files = len(self.python_files)

        # 计算日志覆盖率
        logging_coverage = (logging_usage["files_with_logging"] / total_files) * 100

        print(f"📊 日志覆盖率: {logging_coverage:.1f}%")
        print(f"📁 分析文件总数: {total_files}")
        print(f"📝 使用日志的文件: {logging_usage['files_with_logging']}")
        print(f"🖨️ 使用print的文件: {logging_usage['files_using_print']}")

        # 日志级别分布
        print(f"\n📊 日志级别分布:")
        for level, count in logging_usage["log_level_distribution"].items():
            print(f"  - {level}: {count}")

        # 问题统计
        total_issues = (
            len(self.results["log_level_analysis"]["missing_error_logs"]) +
            len(self.results["log_level_analysis"]["excessive_debug_logs"]) +
            len(self.results["security_analysis"]["potential_leaks"]) +
            len(self.results["format_analysis"]["format_issues"])
        )

        print(f"\n⚠️ 发现的问题:")
        print(f"  - 缺少错误日志: {len(self.results['log_level_analysis']['missing_error_logs'])}")
        print(f"  - DEBUG日志过多: {len(self.results['log_level_analysis']['excessive_debug_logs'])}")
        print(f"  - 潜在信息泄露: {len(self.results['security_analysis']['potential_leaks'])}")
        print(f"  - 格式问题: {len(self.results['format_analysis']['format_issues'])}")
        print(f"  - 总问题数: {total_issues}")

        # 保存详细结果
        self.results["summary"] = {
            "timestamp": datetime.now().isoformat(),
            "total_files": total_files,
            "logging_coverage": logging_coverage,
            "total_issues": total_issues
        }

        import json

        with open("logging_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 详细报告已保存到: logging_analysis_report.json")

        return self.results


    def run_analysis(self):
        """运行完整的日志分析"""
        self.scan_files()
        self.analyze_logging_usage()
        self.check_log_level_appropriateness()
        self.check_sensitive_information()
        self.check_log_format_consistency()
        return self.generate_report()


def main():
    checker = LoggingChecker()
    return checker.run_analysis()

if __name__ == "__main__":
    main()
