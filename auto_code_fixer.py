#!/usr/bin/env python3
"""
自动代码修复工具
修复常见的代码质量问题
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Set

class AutoCodeFixer:
    """自动代码修复器"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.python_files = []
        self.fixes_applied = 0
        
    def scan_files(self):
        """扫描Python文件"""
        print("🔍 扫描Python文件...")
        
        # 排除一些不需要修复的文件
        exclude_patterns = [
            'venv', '__pycache__', '.git', 'node_modules',
            'code_quality_analyzer.py', 'code_quality_check.py',
            'auto_code_fixer.py'  # 排除自己
        ]
        
        for file_path in self.project_root.rglob("*.py"):
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                self.python_files.append(file_path)
        
        print(f"📁 找到 {len(self.python_files)} 个Python文件")
    
    def fix_trailing_whitespace(self):
        """修复尾随空格"""
        print("\n🧹 修复尾随空格...")
        
        fixed_files = 0
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 修复尾随空格
                fixed_lines = []
                has_changes = False
                
                for line in lines:
                    original_line = line
                    # 保留换行符，但去除其他尾随空格
                    if line.endswith('\n'):
                        fixed_line = line.rstrip() + '\n'
                    else:
                        fixed_line = line.rstrip()
                    
                    fixed_lines.append(fixed_line)
                    
                    if fixed_line != original_line:
                        has_changes = True
                
                # 如果有修改，写回文件
                if has_changes:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(fixed_lines)
                    fixed_files += 1
                    self.fixes_applied += 1
                
            except Exception as e:
                print(f"⚠️ 修复文件 {file_path} 时出错: {e}")
        
        print(f"✅ 修复了 {fixed_files} 个文件的尾随空格")
    
    def fix_long_lines(self):
        """修复过长的行（简单情况）"""
        print("\n📏 修复过长的行...")
        
        fixed_files = 0
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                fixed_lines = []
                has_changes = False
                
                for line in lines:
                    if len(line.rstrip()) > 88:
                        # 简单的修复：如果是导入语句，尝试换行
                        if line.strip().startswith('from ') and ' import ' in line:
                            # 分割长导入语句
                            parts = line.split(' import ')
                            if len(parts) == 2:
                                from_part = parts[0]
                                import_part = parts[1].strip()
                                
                                # 如果导入多个项目，尝试换行
                                if ',' in import_part:
                                    imports = [imp.strip() for imp in import_part.split(',')]
                                    if len(imports) > 2:
                                        fixed_line = from_part + ' import (\n'
                                        for imp in imports:
                                            fixed_line += f'    {imp},\n'
                                        fixed_line += ')\n'
                                        fixed_lines.append(fixed_line)
                                        has_changes = True
                                        continue
                        
                        # 如果是字符串，尝试使用三引号
                        if ('"""' in line or "'''" in line) and line.strip().startswith(('"""', "'''")):
                            fixed_lines.append(line)  # 保持不变
                            continue
                    
                    fixed_lines.append(line)
                
                # 如果有修改，写回文件
                if has_changes:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(fixed_lines)
                    fixed_files += 1
                    self.fixes_applied += 1
                
            except Exception as e:
                print(f"⚠️ 修复文件 {file_path} 时出错: {e}")
        
        print(f"✅ 修复了 {fixed_files} 个文件的长行问题")
    
    def remove_unused_imports(self):
        """移除明显未使用的导入"""
        print("\n📦 移除未使用的导入...")
        
        fixed_files = 0
        
        # 常见的未使用导入模式
        common_unused = [
            'import sys',
            'import os', 
            'import time',
            'import datetime',
            'import json',
            'import re'
        ]
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                fixed_lines = []
                has_changes = False
                
                for line in lines:
                    # 检查是否是明显未使用的导入
                    should_remove = False
                    
                    for unused_import in common_unused:
                        if line.strip() == unused_import:
                            # 检查模块是否在代码中使用
                            module_name = unused_import.split()[-1]
                            
                            # 简单检查：如果模块名在其他地方没有出现，可能未使用
                            rest_content = content.replace(line, '')
                            if module_name not in rest_content:
                                should_remove = True
                                break
                    
                    if not should_remove:
                        fixed_lines.append(line)
                    else:
                        has_changes = True
                        print(f"  移除: {file_path} - {line.strip()}")
                
                # 如果有修改，写回文件
                if has_changes:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(fixed_lines))
                    fixed_files += 1
                    self.fixes_applied += 1
                
            except Exception as e:
                print(f"⚠️ 修复文件 {file_path} 时出错: {e}")
        
        print(f"✅ 修复了 {fixed_files} 个文件的导入问题")
    
    def add_missing_docstrings(self):
        """为主要函数添加基本文档字符串"""
        print("\n📝 添加缺失的文档字符串...")
        
        fixed_files = 0
        
        for file_path in self.python_files:
            # 只处理主要文件
            if file_path.name not in ['app.py', 'main.py', 'enhanced_app.py']:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                lines = content.split('\n')
                
                # 找到需要添加文档字符串的函数
                functions_to_fix = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # 检查是否已有文档字符串
                        has_docstring = (
                            node.body and
                            isinstance(node.body[0], ast.Expr) and
                            isinstance(node.body[0].value, ast.Constant) and
                            isinstance(node.body[0].value.value, str)
                        )
                        
                        if not has_docstring and not node.name.startswith('_'):
                            functions_to_fix.append({
                                'name': node.name,
                                'line': node.lineno - 1,  # 转换为0索引
                                'indent': len(lines[node.lineno - 1]) - len(lines[node.lineno - 1].lstrip())
                            })
                
                # 添加文档字符串
                if functions_to_fix:
                    # 从后往前处理，避免行号变化
                    functions_to_fix.sort(key=lambda x: x['line'], reverse=True)
                    
                    for func_info in functions_to_fix:
                        func_line = func_info['line']
                        indent = func_info['indent']
                        func_name = func_info['name']
                        
                        # 生成简单的文档字符串
                        docstring = f'{" " * (indent + 4)}"""{func_name}函数"""'
                        
                        # 在函数定义后插入文档字符串
                        lines.insert(func_line + 1, docstring)
                    
                    # 写回文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    
                    fixed_files += 1
                    self.fixes_applied += len(functions_to_fix)
                    print(f"  添加文档字符串: {file_path} - {len(functions_to_fix)}个函数")
                
            except Exception as e:
                print(f"⚠️ 修复文件 {file_path} 时出错: {e}")
        
        print(f"✅ 为 {fixed_files} 个文件添加了文档字符串")
    
    def fix_common_issues(self):
        """修复常见问题"""
        print("\n🔧 修复常见问题...")
        
        fixed_files = 0
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # 修复常见的格式问题
                # 1. 修复多余的空行
                content = re.sub(r'\n\n\n+', '\n\n', content)
                
                # 2. 修复函数定义前的空行
                content = re.sub(r'\n(\s*)def ', r'\n\n\1def ', content)
                content = re.sub(r'\n(\s*)class ', r'\n\n\1class ', content)
                
                # 3. 修复导入语句后的空行
                content = re.sub(r'(import .+)\n([^import\n])', r'\1\n\n\2', content)
                
                # 如果有修改，写回文件
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_files += 1
                    self.fixes_applied += 1
                
            except Exception as e:
                print(f"⚠️ 修复文件 {file_path} 时出错: {e}")
        
        print(f"✅ 修复了 {fixed_files} 个文件的常见问题")
    
    def run_all_fixes(self):
        """运行所有修复"""
        print("🔧 自动代码修复工具")
        print("="*40)
        
        self.scan_files()
        
        # 按优先级执行修复
        self.fix_trailing_whitespace()
        self.remove_unused_imports()
        self.fix_long_lines()
        self.add_missing_docstrings()
        self.fix_common_issues()
        
        print(f"\n✅ 修复完成！总共应用了 {self.fixes_applied} 个修复")
        
        return self.fixes_applied

def main():
    """主函数"""
    fixer = AutoCodeFixer()
    fixes_applied = fixer.run_all_fixes()
    
    if fixes_applied > 0:
        print(f"\n🎉 成功修复了 {fixes_applied} 个问题")
        print("💡 建议运行代码质量检查工具验证修复效果")
    else:
        print("\n✅ 没有发现需要自动修复的问题")
    
    return 0

if __name__ == "__main__":
    main()
