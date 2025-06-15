#!/usr/bin/env python3
"""
代码质量分析工具
用于识别冗余代码、未使用的导入、死代码等问题
"""

import os
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re

class CodeQualityAnalyzer:
    """代码质量分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.python_files = []
        self.issues = defaultdict(list)
        self.duplicate_files = []
        self.unused_imports = defaultdict(list)
        
    def scan_project(self):
        """扫描项目文件"""
        print("🔍 扫描项目文件...")
        
        # 查找所有Python文件
        for file_path in self.project_root.rglob("*.py"):
            if not any(part.startswith('.') for part in file_path.parts):
                self.python_files.append(file_path)
        
        print(f"📁 找到 {len(self.python_files)} 个Python文件")
        
    def analyze_duplicate_files(self):
        """分析重复文件"""
        print("\n🔍 分析重复文件...")
        
        # 识别可能重复的应用启动文件
        app_files = [
            "app.py", "simple_app.py", "enhanced_app.py", "advanced_app.py",
            "enterprise_app.py", "streamlit_app.py", "simple_streamlit_app.py",
            "enhanced_streamlit_app.py", "secure_streamlit_app.py",
            "integrated_streamlit_app.py", "streamlit_cloud_app.py",
            "quick_start.py", "run_local.py"
        ]
        
        existing_app_files = []
        for app_file in app_files:
            if (self.project_root / app_file).exists():
                existing_app_files.append(app_file)
        
        if len(existing_app_files) > 3:  # 超过3个应用文件认为冗余
            self.duplicate_files = existing_app_files
            self.issues["duplicate_files"].append({
                "type": "多个应用启动文件",
                "files": existing_app_files,
                "suggestion": "保留主要的2-3个文件，删除其他冗余文件"
            })
    
    def analyze_unused_imports(self):
        """分析未使用的导入"""
        print("\n🔍 分析未使用的导入...")
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # 收集导入的模块
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
                        for alias in node.names:
                            imports.add(alias.name)
                
                # 检查是否使用了导入的模块
                unused = []
                for imp in imports:
                    if imp not in content.replace(f"import {imp}", "").replace(f"from {imp}", ""):
                        # 简单检查，可能有误报
                        pattern = rf'\b{re.escape(imp)}\b'
                        if not re.search(pattern, content.replace(f"import {imp}", "").replace(f"from {imp}", "")):
                            unused.append(imp)
                
                if unused:
                    self.unused_imports[str(file_path)] = unused
                    
            except Exception as e:
                print(f"⚠️ 分析文件 {file_path} 时出错: {e}")
    
    def analyze_code_complexity(self):
        """分析代码复杂度"""
        print("\n🔍 分析代码复杂度...")
        
        complex_files = []
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 检查文件长度
                if len(lines) > 500:
                    complex_files.append({
                        "file": str(file_path),
                        "lines": len(lines),
                        "issue": "文件过长",
                        "suggestion": "考虑拆分为多个模块"
                    })
                
                # 检查函数长度
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_lines = node.end_lineno - node.lineno + 1
                        if func_lines > 50:
                            complex_files.append({
                                "file": str(file_path),
                                "function": node.name,
                                "lines": func_lines,
                                "issue": "函数过长",
                                "suggestion": "考虑拆分函数"
                            })
                            
            except Exception as e:
                print(f"⚠️ 分析文件 {file_path} 时出错: {e}")
        
        if complex_files:
            self.issues["complexity"] = complex_files
    
    def analyze_pep8_violations(self):
        """分析PEP8规范违反"""
        print("\n🔍 分析PEP8规范...")
        
        pep8_issues = []
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # 检查行长度
                    if len(line.rstrip()) > 88:  # 稍微宽松的限制
                        pep8_issues.append({
                            "file": str(file_path),
                            "line": i,
                            "issue": "行长度超过88字符",
                            "content": line.strip()[:50] + "..."
                        })
                    
                    # 检查尾随空格
                    if line.rstrip() != line.rstrip('\n'):
                        pep8_issues.append({
                            "file": str(file_path),
                            "line": i,
                            "issue": "行尾有多余空格"
                        })
                        
            except Exception as e:
                print(f"⚠️ 分析文件 {file_path} 时出错: {e}")
        
        if pep8_issues:
            self.issues["pep8"] = pep8_issues[:20]  # 只显示前20个问题
    
    def generate_report(self):
        """生成分析报告"""
        print("\n" + "="*60)
        print("📊 代码质量分析报告")
        print("="*60)
        
        # 重复文件报告
        if self.duplicate_files:
            print("\n🔄 重复/冗余文件:")
            for file in self.duplicate_files:
                print(f"  - {file}")
            print("  💡 建议: 保留主要的2-3个应用文件，删除其他冗余文件")
        
        # 未使用导入报告
        if self.unused_imports:
            print("\n📦 可能未使用的导入:")
            for file, imports in list(self.unused_imports.items())[:5]:  # 只显示前5个文件
                print(f"  📁 {file}:")
                for imp in imports[:3]:  # 每个文件只显示前3个
                    print(f"    - {imp}")
        
        # 复杂度报告
        if "complexity" in self.issues:
            print("\n🔧 代码复杂度问题:")
            for issue in self.issues["complexity"][:5]:  # 只显示前5个
                if "function" in issue:
                    print(f"  📁 {issue['file']} - 函数 {issue['function']} ({issue['lines']} 行)")
                else:
                    print(f"  📁 {issue['file']} - {issue['issue']} ({issue['lines']} 行)")
        
        # PEP8报告
        if "pep8" in self.issues:
            print(f"\n📏 PEP8规范问题 (显示前10个):")
            for issue in self.issues["pep8"][:10]:
                print(f"  📁 {issue['file']}:{issue['line']} - {issue['issue']}")
        
        # 总结
        print("\n" + "="*60)
        print("📋 总结:")
        print(f"  📁 扫描文件: {len(self.python_files)}")
        print(f"  🔄 重复文件: {len(self.duplicate_files)}")
        print(f"  📦 有未使用导入的文件: {len(self.unused_imports)}")
        print(f"  🔧 复杂度问题: {len(self.issues.get('complexity', []))}")
        print(f"  📏 PEP8问题: {len(self.issues.get('pep8', []))}")
        print("="*60)
    
    def get_cleanup_recommendations(self):
        """获取清理建议"""
        recommendations = []
        
        # 重复文件清理建议
        if self.duplicate_files:
            keep_files = ["app.py", "enhanced_app.py", "quick_start.py"]
            remove_files = [f for f in self.duplicate_files if f not in keep_files]
            
            recommendations.append({
                "type": "删除冗余文件",
                "action": "remove_files",
                "files": remove_files,
                "description": "删除冗余的应用启动文件，保留主要的3个文件"
            })
        
        # 代码重构建议
        if "complexity" in self.issues:
            recommendations.append({
                "type": "代码重构",
                "action": "refactor_code",
                "files": [issue["file"] for issue in self.issues["complexity"]],
                "description": "重构复杂的函数和文件，提高代码可维护性"
            })
        
        return recommendations

def main():
    """主函数"""
    print("🔍 代码质量分析工具")
    print("="*40)
    
    analyzer = CodeQualityAnalyzer()
    
    # 执行分析
    analyzer.scan_project()
    analyzer.analyze_duplicate_files()
    analyzer.analyze_unused_imports()
    analyzer.analyze_code_complexity()
    analyzer.analyze_pep8_violations()
    
    # 生成报告
    analyzer.generate_report()
    
    # 获取清理建议
    recommendations = analyzer.get_cleanup_recommendations()
    
    if recommendations:
        print("\n💡 清理建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['type']}: {rec['description']}")
    
    return analyzer

if __name__ == "__main__":
    analyzer = main()
