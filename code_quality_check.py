#!/usr/bin/env python3
"""
代码质量检查脚本
验证重构后的代码质量
"""

import os
import sys
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class CodeQualityChecker:
    """代码质量检查器"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.python_files = []
        self.results = {}
        
    def scan_files(self):
        """扫描Python文件"""
        print("🔍 扫描Python文件...")
        
        for file_path in self.project_root.rglob("*.py"):
            if not any(part.startswith('.') for part in file_path.parts):
                self.python_files.append(file_path)
        
        print(f"📁 找到 {len(self.python_files)} 个Python文件")
    
    def check_imports(self):
        """检查导入语句"""
        print("\n📦 检查导入语句...")
        
        import_issues = []
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # 检查导入语句
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            # 检查是否有未使用的导入
                            module_name = alias.name.split('.')[0]
                            if module_name not in content.replace(f"import {alias.name}", ""):
                                import_issues.append({
                                    "file": str(file_path),
                                    "line": node.lineno,
                                    "issue": f"可能未使用的导入: {alias.name}"
                                })
                
            except Exception as e:
                print(f"⚠️ 检查文件 {file_path} 时出错: {e}")
        
        self.results['imports'] = import_issues
        print(f"📦 发现 {len(import_issues)} 个导入问题")
    
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
                            "length": len(line.rstrip())
                        })
                    
                    # 检查尾随空格
                    if line.rstrip() != line.rstrip('\n'):
                        style_issues.append({
                            "file": str(file_path),
                            "line": i,
                            "issue": "行尾有多余空格"
                        })
                
            except Exception as e:
                print(f"⚠️ 检查文件 {file_path} 时出错: {e}")
        
        self.results['style'] = style_issues
        print(f"📏 发现 {len(style_issues)} 个风格问题")
    
    def check_function_complexity(self):
        """检查函数复杂度"""
        print("\n🔧 检查函数复杂度...")
        
        complexity_issues = []
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # 计算函数行数
                        func_lines = node.end_lineno - node.lineno + 1
                        
                        if func_lines > 50:
                            complexity_issues.append({
                                "file": str(file_path),
                                "function": node.name,
                                "lines": func_lines,
                                "issue": "函数过长"
                            })
                        
                        # 计算函数参数数量
                        param_count = len(node.args.args)
                        if param_count > 7:
                            complexity_issues.append({
                                "file": str(file_path),
                                "function": node.name,
                                "params": param_count,
                                "issue": "参数过多"
                            })
                
            except Exception as e:
                print(f"⚠️ 检查文件 {file_path} 时出错: {e}")
        
        self.results['complexity'] = complexity_issues
        print(f"🔧 发现 {len(complexity_issues)} 个复杂度问题")
    
    def check_docstrings(self):
        """检查文档字符串"""
        print("\n📝 检查文档字符串...")
        
        docstring_issues = []
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        # 检查是否有文档字符串
                        has_docstring = (
                            node.body and
                            isinstance(node.body[0], ast.Expr) and
                            isinstance(node.body[0].value, ast.Constant) and
                            isinstance(node.body[0].value.value, str)
                        )
                        
                        if not has_docstring and not node.name.startswith('_'):
                            docstring_issues.append({
                                "file": str(file_path),
                                "name": node.name,
                                "type": "函数" if isinstance(node, ast.FunctionDef) else "类",
                                "line": node.lineno,
                                "issue": "缺少文档字符串"
                            })
                
            except Exception as e:
                print(f"⚠️ 检查文件 {file_path} 时出错: {e}")
        
        self.results['docstrings'] = docstring_issues
        print(f"📝 发现 {len(docstring_issues)} 个文档问题")
    
    def check_security_issues(self):
        """检查安全问题"""
        print("\n🛡️ 检查安全问题...")
        
        security_issues = []
        
        # 危险的函数和模式
        dangerous_patterns = [
            ('eval(', '使用eval()函数'),
            ('exec(', '使用exec()函数'),
            ('os.system(', '使用os.system()'),
            ('subprocess.call(', '使用subprocess.call()'),
            ('shell=True', 'subprocess中使用shell=True'),
            ('pickle.loads(', '使用pickle.loads()'),
            ('yaml.load(', '使用yaml.load()而非yaml.safe_load()'),
        ]
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern, description in dangerous_patterns:
                        if pattern in line and not line.strip().startswith('#'):
                            security_issues.append({
                                "file": str(file_path),
                                "line": i,
                                "issue": description,
                                "code": line.strip()
                            })
                
            except Exception as e:
                print(f"⚠️ 检查文件 {file_path} 时出错: {e}")
        
        self.results['security'] = security_issues
        print(f"🛡️ 发现 {len(security_issues)} 个安全问题")
    
    def run_pylint(self):
        """运行pylint检查"""
        print("\n🔍 运行pylint检查...")
        
        try:
            # 检查是否安装了pylint
            result = subprocess.run(['pylint', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ pylint未安装，跳过检查")
                return
            
            # 运行pylint检查主要文件
            main_files = ['app.py', 'enhanced_app.py', 'main.py', 'utils/common.py']
            existing_files = [f for f in main_files if Path(f).exists()]
            
            if not existing_files:
                print("⚠️ 没有找到主要文件进行pylint检查")
                return
            
            result = subprocess.run(['pylint'] + existing_files, 
                                  capture_output=True, text=True)
            
            # 解析pylint输出
            lines = result.stdout.split('\n')
            score_line = [line for line in lines if 'Your code has been rated at' in line]
            
            if score_line:
                print(f"📊 Pylint评分: {score_line[0]}")
            else:
                print("📊 Pylint检查完成")
            
        except Exception as e:
            print(f"⚠️ pylint检查失败: {e}")
    
    def generate_report(self):
        """生成检查报告"""
        print("\n" + "="*60)
        print("📊 代码质量检查报告")
        print("="*60)
        
        # 总体统计
        total_issues = sum(len(issues) for issues in self.results.values())
        print(f"\n📋 总体统计:")
        print(f"  📁 检查文件: {len(self.python_files)}")
        print(f"  ⚠️ 发现问题: {total_issues}")
        
        # 分类统计
        for category, issues in self.results.items():
            if issues:
                print(f"\n📂 {category.upper()} 问题 ({len(issues)}个):")
                for issue in issues[:5]:  # 只显示前5个
                    if 'file' in issue:
                        print(f"  📄 {issue['file']}:{issue.get('line', '?')} - {issue['issue']}")
                
                if len(issues) > 5:
                    print(f"  ... 还有 {len(issues) - 5} 个问题")
        
        # 改进建议
        print(f"\n💡 改进建议:")
        if self.results.get('imports'):
            print("  📦 清理未使用的导入语句")
        if self.results.get('style'):
            print("  📏 修复代码风格问题")
        if self.results.get('complexity'):
            print("  🔧 重构复杂的函数")
        if self.results.get('docstrings'):
            print("  📝 添加缺失的文档字符串")
        if self.results.get('security'):
            print("  🛡️ 修复安全问题")
        
        print("="*60)
        
        return total_issues
    
    def run_all_checks(self):
        """运行所有检查"""
        self.scan_files()
        self.check_imports()
        self.check_code_style()
        self.check_function_complexity()
        self.check_docstrings()
        self.check_security_issues()
        self.run_pylint()
        
        return self.generate_report()

def main():
    """主函数"""
    print("🔍 代码质量检查工具")
    print("="*40)
    
    checker = CodeQualityChecker()
    total_issues = checker.run_all_checks()
    
    # 返回状态码
    if total_issues == 0:
        print("\n✅ 代码质量检查通过！")
        return 0
    else:
        print(f"\n⚠️ 发现 {total_issues} 个问题需要修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
