#!/usr/bin/env python3
"""
隐私保护工具

自动检测和隐藏项目中的敏感信息
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

class PrivacyProtector:
    """隐私保护器"""
    
    def __init__(self):
        """初始化隐私保护器"""
        # 敏感信息模式
        self.sensitive_patterns = {
            'api_keys': [
                r'(ARK_API_KEY\s*=\s*)["\']?([a-zA-Z0-9\-_]{20,})["\']?',
                r'(OPENAI_API_KEY\s*=\s*)["\']?(sk-[a-zA-Z0-9\-_]{20,})["\']?',
                r'(API_KEY\s*=\s*)["\']?([a-zA-Z0-9\-_]{20,})["\']?',
                r'(api_key\s*[:=]\s*)["\']?([a-zA-Z0-9\-_]{20,})["\']?',
            ],
            'secrets': [
                r'(SECRET_KEY\s*=\s*)["\']?([a-zA-Z0-9\-_]{20,})["\']?',
                r'(CLIENT_SECRET\s*=\s*)["\']?([a-zA-Z0-9\-_]{20,})["\']?',
                r'(ACCESS_TOKEN\s*=\s*)["\']?([a-zA-Z0-9\-_]{20,})["\']?',
            ],
            'passwords': [
                r'(PASSWORD\s*=\s*)["\']?([^\s"\']{8,})["\']?',
                r'(PASSWD\s*=\s*)["\']?([^\s"\']{8,})["\']?',
                r'(password\s*[:=]\s*)["\']?([^\s"\']{8,})["\']?',
            ],
            'urls_with_auth': [
                r'(https?://[^:]+):([^@]+)@([^\s"\']+)',
                r'(mongodb://[^:]+):([^@]+)@([^\s"\']+)',
            ],
            'email_addresses': [
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            ],
            'ip_addresses': [
                r'(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)',
            ]
        }
        
        # 替换模板
        self.replacement_templates = {
            'api_keys': '***API_KEY_HIDDEN***',
            'secrets': '***SECRET_HIDDEN***',
            'passwords': '***PASSWORD_HIDDEN***',
            'urls_with_auth': r'\1:***AUTH_HIDDEN***@\3',
            'email_addresses': '***EMAIL_HIDDEN***',
            'ip_addresses': '***IP_HIDDEN***'
        }
        
        # 需要检查的文件类型
        self.file_extensions = [
            '.py', '.md', '.txt', '.yml', '.yaml', '.json', 
            '.toml', '.env', '.example', '.conf', '.config'
        ]
        
        # 排除的目录
        self.exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', 'env', '.env', 'logs', 'cache'
        }
        
        # 排除的文件
        self.exclude_files = {
            '.gitignore', '.DS_Store', 'privacy_protection.py'
        }
    
    def scan_project(self, project_path: str = '.') -> Dict[str, List[Dict]]:
        """扫描项目中的敏感信息"""
        project_path = Path(project_path)
        findings = {
            'files_scanned': 0,
            'sensitive_files': [],
            'issues_found': []
        }
        
        for file_path in self._get_files_to_scan(project_path):
            findings['files_scanned'] += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_issues = self._scan_content(str(file_path), content)
                if file_issues:
                    findings['sensitive_files'].append(str(file_path))
                    findings['issues_found'].extend(file_issues)
                    
            except Exception as e:
                print(f"⚠️ 无法读取文件 {file_path}: {e}")
        
        return findings
    
    def _get_files_to_scan(self, project_path: Path) -> List[Path]:
        """获取需要扫描的文件列表"""
        files_to_scan = []
        
        for root, dirs, files in os.walk(project_path):
            # 排除指定目录
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file in self.exclude_files:
                    continue
                
                file_path = Path(root) / file
                
                # 检查文件扩展名
                if any(file.endswith(ext) for ext in self.file_extensions):
                    files_to_scan.append(file_path)
        
        return files_to_scan
    
    def _scan_content(self, file_path: str, content: str) -> List[Dict]:
        """扫描内容中的敏感信息"""
        issues = []
        
        for category, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    # 跳过明显的示例值
                    if self._is_example_value(match.group()):
                        continue
                    
                    line_num = content[:match.start()].count('\n') + 1
                    
                    issues.append({
                        'file': file_path,
                        'line': line_num,
                        'category': category,
                        'pattern': pattern,
                        'match': match.group(),
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return issues
    
    def _is_example_value(self, value: str) -> bool:
        """检查是否为示例值"""
        example_indicators = [
            'your_', 'example', 'test', 'demo', 'sample',
            'placeholder', 'xxx', '***', 'hidden',
            'replace_me', 'change_me', 'api_key_here'
        ]
        
        value_lower = value.lower()
        return any(indicator in value_lower for indicator in example_indicators)
    
    def mask_sensitive_content(self, content: str) -> Tuple[str, int]:
        """掩码内容中的敏感信息"""
        masked_content = content
        replacements_made = 0
        
        for category, patterns in self.sensitive_patterns.items():
            template = self.replacement_templates[category]
            
            for pattern in patterns:
                def replace_func(match):
                    nonlocal replacements_made
                    if self._is_example_value(match.group()):
                        return match.group()  # 保持示例值不变
                    
                    replacements_made += 1
                    
                    if category == 'urls_with_auth':
                        return template
                    else:
                        # 保留前缀，只替换敏感部分
                        if len(match.groups()) >= 2:
                            return match.group(1) + template
                        else:
                            return template
                
                masked_content = re.sub(pattern, replace_func, masked_content, flags=re.IGNORECASE | re.MULTILINE)
        
        return masked_content, replacements_made
    
    def create_safe_files(self, project_path: str = '.') -> Dict[str, int]:
        """创建安全版本的文件"""
        project_path = Path(project_path)
        safe_dir = project_path / 'safe_versions'
        safe_dir.mkdir(exist_ok=True)
        
        results = {
            'files_processed': 0,
            'files_modified': 0,
            'total_replacements': 0
        }
        
        for file_path in self._get_files_to_scan(project_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                masked_content, replacements = self.mask_sensitive_content(content)
                
                if replacements > 0:
                    # 创建安全版本
                    relative_path = file_path.relative_to(project_path)
                    safe_file_path = safe_dir / relative_path
                    safe_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(safe_file_path, 'w', encoding='utf-8') as f:
                        f.write(masked_content)
                    
                    results['files_modified'] += 1
                    results['total_replacements'] += replacements
                    
                    print(f"✅ 已创建安全版本: {safe_file_path} ({replacements} 处替换)")
                
                results['files_processed'] += 1
                
            except Exception as e:
                print(f"❌ 处理文件失败 {file_path}: {e}")
        
        return results
    
    def generate_gitignore_rules(self) -> List[str]:
        """生成.gitignore规则"""
        rules = [
            "# 敏感信息文件",
            ".env",
            "*.env",
            "secrets.toml",
            "config/secrets.json",
            "",
            "# API密钥和配置",
            "**/api_keys.txt",
            "**/secrets.txt",
            "**/config/production.json",
            "",
            "# 日志文件（可能包含敏感信息）",
            "logs/",
            "*.log",
            "",
            "# 缓存和临时文件",
            "cache/",
            "tmp/",
            "temp/",
            "",
            "# 数据库文件",
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            "",
            "# 备份文件",
            "*.bak",
            "*.backup",
            "",
            "# 系统文件",
            ".DS_Store",
            "Thumbs.db",
        ]
        return rules
    
    def update_gitignore(self, project_path: str = '.') -> bool:
        """更新.gitignore文件"""
        gitignore_path = Path(project_path) / '.gitignore'
        
        try:
            # 读取现有内容
            existing_content = ""
            if gitignore_path.exists():
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # 生成新规则
            new_rules = self.generate_gitignore_rules()
            
            # 检查哪些规则需要添加
            rules_to_add = []
            for rule in new_rules:
                if rule and not rule.startswith('#') and rule not in existing_content:
                    rules_to_add.append(rule)
            
            if rules_to_add:
                # 添加新规则
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    if existing_content and not existing_content.endswith('\n'):
                        f.write('\n')
                    f.write('\n'.join(new_rules))
                    f.write('\n')
                
                print(f"✅ 已更新 .gitignore，添加了 {len(rules_to_add)} 条新规则")
                return True
            else:
                print("ℹ️ .gitignore 已包含所有必要规则")
                return False
                
        except Exception as e:
            print(f"❌ 更新 .gitignore 失败: {e}")
            return False

def main():
    """主函数"""
    print("🔒 隐私保护工具")
    print("=" * 50)
    
    protector = PrivacyProtector()
    
    # 扫描项目
    print("🔍 扫描项目中的敏感信息...")
    findings = protector.scan_project()
    
    print(f"\n📊 扫描结果:")
    print(f"  - 扫描文件数: {findings['files_scanned']}")
    print(f"  - 包含敏感信息的文件: {len(findings['sensitive_files'])}")
    print(f"  - 发现的问题数: {len(findings['issues_found'])}")
    
    if findings['issues_found']:
        print(f"\n⚠️ 发现的敏感信息:")
        for issue in findings['issues_found'][:10]:  # 只显示前10个
            print(f"  - {issue['file']}:{issue['line']} - {issue['category']}")
        
        if len(findings['issues_found']) > 10:
            print(f"  ... 还有 {len(findings['issues_found']) - 10} 个问题")
        
        # 创建安全版本
        print(f"\n🛡️ 创建安全版本...")
        results = protector.create_safe_files()
        print(f"  - 处理文件数: {results['files_processed']}")
        print(f"  - 修改文件数: {results['files_modified']}")
        print(f"  - 总替换数: {results['total_replacements']}")
    
    # 更新.gitignore
    print(f"\n📝 更新 .gitignore...")
    protector.update_gitignore()
    
    print(f"\n✅ 隐私保护完成!")
    print(f"\n💡 建议:")
    print(f"  1. 检查 safe_versions/ 目录中的安全版本")
    print(f"  2. 确保 .env 文件不被提交到版本控制")
    print(f"  3. 定期运行此工具检查新的敏感信息")
    print(f"  4. 在生产环境中使用环境变量或密钥管理服务")

if __name__ == "__main__":
    main()
