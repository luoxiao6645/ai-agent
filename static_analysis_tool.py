#!/usr/bin/env python3
"""
静态代码分析工具 - 简化版
对Python代码进行质量评估
"""

import os
import ast
import re
import json

from pathlib import Path

from typing import Dict, List, Any

from datetime import datetime


class CodeQualityAnalyzer:
    """代码质量分析器"""


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


    def analyze_complexity(self):
        """分析代码复杂度"""
        print("\n🔧 分析代码复杂度...")

        complexity_results = {}
        total_lines = 0
        total_functions = 0
        complex_functions = []

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                lines = len(content.split('\n'))
                total_lines += lines

                try:
                    tree = ast.parse(content)

                    file_functions = 0
                    file_complex = []

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            file_functions += 1
                            total_functions += 1

                            func_length = node.end_lineno - node.lineno + 1
                            if func_length > 50:
                                complex_func = {
                                    "file": str(file_path),
                                    "function": node.name,
                                    "length": func_length,
                                    "line": node.lineno
                                }
                                file_complex.append(complex_func)
                                complex_functions.append(complex_func)

                    complexity_results[str(file_path)] = {
                        "lines": lines,
                        "functions": file_functions,
                        "complex_functions": file_complex
                    }

                except SyntaxError as e:
                    print(f"⚠️ 语法错误 {file_path}: {e}")

            except Exception as e:
                print(f"⚠️ 分析失败 {file_path}: {e}")

        self.results["complexity"] = {
            "total_lines": total_lines,
            "total_functions": total_functions,
            "complex_functions": complex_functions,
            "by_file": complexity_results
        }

        print(f"📊 总代码行数: {total_lines}")
        print(f"📊 总函数数: {total_functions}")
        print(f"📊 复杂函数数: {len(complex_functions)}")


    def check_security_issues(self):
        """检查安全问题"""
        print("\n🛡️ 检查安全问题...")

        security_patterns = [
            (r'eval\s*\(', 'eval()函数使用', 'high'),
            (r'exec\s*\(', 'exec()函数使用', 'high'),
            (r'os\.system\s*\(', 'os.system()使用', 'high'),
            (r'subprocess.*shell\s*=\s*True', 'shell=True使用', 'medium'),
            (r'pickle\.loads?\s*\(', 'pickle反序列化', 'medium'),
            (r'yaml\.load\s*\(', 'yaml.load()使用', 'medium'),
        ]

        security_issues = []

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for i, line in enumerate(lines, 1):
                    for pattern, description, severity in security_patterns:
                        if re.search(pattern, line) and not line.strip().startswith('#'):
                            security_issues.append({
                                "file": str(file_path),
                                "line": i,
                                "code": line.strip(),
                                "issue": description,
                                "severity": severity
                            })

            except Exception as e:
                print(f"⚠️ 安全检查失败 {file_path}: {e}")

        # 按严重程度分组
        by_severity = {"high": [], "medium": [], "low": []}
        for issue in security_issues:
            by_severity[issue["severity"]].append(issue)

        self.results["security"] = {
            "issues": security_issues,
            "by_severity": by_severity,
            "summary": {
                "total": len(security_issues),
                "high": len(by_severity["high"]),
                "medium": len(by_severity["medium"]),
                "low": len(by_severity["low"])
            }
        }

        print(f"🚨 发现安全问题: {len(security_issues)}")
        print(f"   - 高危: {len(by_severity['high'])}")
        print(f"   - 中危: {len(by_severity['medium'])}")
        print(f"   - 低危: {len(by_severity['low'])}")


    def check_code_style(self):
        """检查代码风格"""
        print("\n📏 检查代码风格...")

        style_issues = []

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for i, line in enumerate(lines, 1):
                    # 检查行长度
                    if len(line.rstrip()) > 88:
                        style_issues.append({
                            "file": str(file_path),
                            "line": i,
                            "issue": "行长度超过88字符",
                            "type": "line_length"
                        })

                    # 检查尾随空格
                    if line.rstrip() != line.rstrip('\n'):
                        style_issues.append({
                            "file": str(file_path),
                            "line": i,
                            "issue": "行尾有多余空格",
                            "type": "trailing_whitespace"
                        })

            except Exception as e:
                print(f"⚠️ 风格检查失败 {file_path}: {e}")

        self.results["style"] = {
            "issues": style_issues,
            "total": len(style_issues)
        }

        print(f"📐 代码风格问题: {len(style_issues)}")


    def check_imports(self):
        """检查导入问题"""
        print("\n📦 检查导入问题...")

        import_issues = []

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                try:
                    tree = ast.parse(content)

                    imports = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.append(node.module)

                    # 简单检查未使用的导入
                    for imp in imports:
                        module_name = imp.split('.')[0]
                        if module_name not in content.replace(f"import {imp}", ""):

                            # 更精确的检查
                            if not re.search(rf'\b{re.escape(module_name)}\b',
                                           content.replace(f"import {imp}", "")):

                                import_issues.append({
                                    "file": str(file_path),
                                    "import": imp,
                                    "issue": "可能未使用的导入"
                                })

                except SyntaxError:
                    pass

            except Exception as e:
                print(f"⚠️ 导入检查失败 {file_path}: {e}")

        self.results["imports"] = {
            "issues": import_issues,
            "total": len(import_issues)
        }

        print(f"📦 导入问题: {len(import_issues)}")


    def calculate_quality_score(self):
        """计算质量分数"""
        score = 100.0

        # 复杂度扣分
        complex_functions = len(self.results["complexity"]["complex_functions"])
        score -= min(complex_functions * 3, 30)

        # 安全问题扣分
        security = self.results["security"]["summary"]
        score -= security["high"] * 15
        score -= security["medium"] * 8
        score -= security["low"] * 3

        # 风格问题扣分
        style_issues = self.results["style"]["total"]
        score -= min(style_issues * 0.1, 20)

        # 导入问题扣分
        import_issues = self.results["imports"]["total"]
        score -= min(import_issues * 1, 10)

        return max(0, score)


    def generate_report(self):
        """生成报告"""
        quality_score = self.calculate_quality_score()

        print("\n" + "="*60)
        print("📊 代码质量分析报告")
        print("="*60)
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"分析文件: {len(self.python_files)} 个")
        print(f"整体质量分数: {quality_score:.1f}/100")

        # 详细结果
        complexity = self.results["complexity"]
        print(f"\n🔧 复杂度分析:")
        print(f"  - 总代码行数: {complexity['total_lines']}")
        print(f"  - 总函数数: {complexity['total_functions']}")
        print(f"  - 复杂函数数: {len(complexity['complex_functions'])}")

        security = self.results["security"]["summary"]
        print(f"\n🛡️ 安全分析:")
        print(f"  - 高危问题: {security['high']}")
        print(f"  - 中危问题: {security['medium']}")
        print(f"  - 低危问题: {security['low']}")

        print(f"\n📏 代码风格: {self.results['style']['total']} 个问题")
        print(f"📦 导入问题: {self.results['imports']['total']} 个问题")

        # 保存详细结果
        self.results["summary"] = {
            "timestamp": datetime.now().isoformat(),
            "quality_score": quality_score,
            "total_files": len(self.python_files)
        }

        with open("code_quality_report.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 详细报告已保存到: code_quality_report.json")

        return self.results


    def run_analysis(self):
        """运行完整分析"""
        self.scan_files()
        self.analyze_complexity()
        self.check_security_issues()
        self.check_code_style()
        self.check_imports()
        return self.generate_report()


def main():
    analyzer = CodeQualityAnalyzer()
    return analyzer.run_analysis()

if __name__ == "__main__":
    main()
