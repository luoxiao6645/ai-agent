#!/usr/bin/env python3
"""
安全性措施检查工具
验证输入验证、认证授权、数据加密等安全措施
"""

import re
import ast
import json

from pathlib import Path

from typing import Dict, List, Any

from datetime import datetime


class SecurityChecker:
    """安全性检查器"""


    def __init__(self):
        self.project_root = Path(".")
        self.python_files = []
        self.results = {}

        # 安全风险模式
        self.security_patterns = {
            "high_risk": [
                (r'eval\s*\(', 'eval()函数使用'),
                (r'exec\s*\(', 'exec()函数使用'),
                (r'os\.system\s*\(', 'os.system()使用'),
                (r'subprocess.*shell\s*=\s*True', 'shell=True使用'),
                (r'pickle\.loads?\s*\(', 'pickle反序列化'),
                (r'yaml\.load\s*\((?!.*Loader)', 'yaml.load()不安全使用'),
            ],
            "medium_risk": [
                (r'open\s*\([^)]*["\']w["\']', '文件写入操作'),
                (r'requests\.\w+\([^)]*verify\s*=\s*False', 'SSL验证禁用'),
                (r'urllib\.request\.urlopen', 'urllib不安全请求'),
                (r'random\.random\(\)', '弱随机数生成'),
                (r'hashlib\.md5\(\)', 'MD5哈希使用'),
                (r'hashlib\.sha1\(\)', 'SHA1哈希使用'),
            ],
            "low_risk": [
                (r'input\s*\(', '用户输入未验证'),
                (r'print\s*\([^)]*password', '密码信息打印'),
                (r'print\s*\([^)]*token', '令牌信息打印'),
                (r'logging\.\w+\([^)]*password', '密码信息记录'),
            ]
        }

        # 敏感信息模式
        self.sensitive_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', '硬编码密码'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', '硬编码API密钥'),
            (r'secret\s*=\s*["\'][^"\']+["\']', '硬编码密钥'),
            (r'token\s*=\s*["\'][^"\']+["\']', '硬编码令牌'),
            (r'["\'][A-Za-z0-9]{32,}["\']', '可能的硬编码密钥'),
        ]


    def scan_files(self):
        """扫描Python文件"""
        print("🔍 扫描Python文件...")

        exclude_patterns = ['__pycache__', '.git', 'venv', 'env']

        for file_path in self.project_root.rglob("*.py"):
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                self.python_files.append(file_path)

        print(f"📁 找到 {len(self.python_files)} 个Python文件")


    def check_input_validation(self):
        """检查输入验证"""
        print("\n🛡️ 检查输入验证...")

        validation_analysis = {
            "user_inputs": [],
            "validated_inputs": [],
            "unvalidated_inputs": [],
            "validation_patterns": [],
            "sanitization_found": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    # 检查用户输入
                    if re.search(r'\binput\s*\(', stripped_line):
                        validation_analysis["user_inputs"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "code": stripped_line
                        })

                        # 检查后续行是否有验证
                        has_validation = False
                        for j in range(i + 1, min(i + 5, len(lines))):
                            next_line = lines[j].strip()
                            if any(pattern in next_line for pattern in
                                  ['validate', 'check', 'verify', 'isinstance', 'len(']):
                                has_validation = True
                                validation_analysis["validated_inputs"].append({
                                    "file": str(file_path),
                                    "line": i + 1,
                                    "validation_line": j + 1
                                })
                                break

                        if not has_validation:
                            validation_analysis["unvalidated_inputs"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "issue": "用户输入未验证"
                            })

                    # 检查验证模式
                    validation_keywords = ['validate', 'sanitize', 'escape', 'filter']
                    for keyword in validation_keywords:
                        if keyword in stripped_line.lower():
                            validation_analysis["validation_patterns"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "pattern": keyword,
                                "code": stripped_line
                            })

                    # 检查数据清理
                    if any(pattern in stripped_line for pattern in
                          ['html.escape', 're.sub', 'strip()', 'replace(']):
                        validation_analysis["sanitization_found"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "practice": "数据清理操作"
                        })

            except Exception as e:
                print(f"⚠️ 输入验证检查失败 {file_path}: {e}")

        self.results["input_validation"] = validation_analysis

        print(f"📊 输入验证分析:")
        print(f"  - 用户输入点: {len(validation_analysis['user_inputs'])}")
        print(f"  - 已验证输入: {len(validation_analysis['validated_inputs'])}")
        print(f"  - 未验证输入: {len(validation_analysis['unvalidated_inputs'])}")
        print(f"  - 验证模式: {len(validation_analysis['validation_patterns'])}")


    def check_authentication_authorization(self):
        """检查认证和授权"""
        print("\n🔐 检查认证和授权...")

        auth_analysis = {
            "auth_mechanisms": [],
            "jwt_usage": [],
            "session_management": [],
            "permission_checks": [],
            "auth_vulnerabilities": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    # 检查JWT使用
                    if 'jwt' in stripped_line.lower():
                        auth_analysis["jwt_usage"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "code": stripped_line
                        })

                    # 检查会话管理
                    if any(pattern in stripped_line.lower() for pattern in
                          ['session', 'cookie', 'login', 'logout']):
                        auth_analysis["session_management"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "type": "会话管理相关"
                        })

                    # 检查权限检查
                    if any(pattern in stripped_line.lower() for pattern in
                          ['permission', 'authorize', 'access', 'role']):
                        auth_analysis["permission_checks"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "type": "权限检查"
                        })

                    # 检查认证机制
                    if any(pattern in stripped_line for pattern in
                          ['authenticate', 'verify_token', 'check_auth']):
                        auth_analysis["auth_mechanisms"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "mechanism": "认证机制"
                        })

                    # 检查认证漏洞
                    if re.search(r'password\s*==\s*["\']', stripped_line):
                        auth_analysis["auth_vulnerabilities"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "vulnerability": "明文密码比较",
                            "suggestion": "使用哈希比较"
                        })

            except Exception as e:
                print(f"⚠️ 认证检查失败 {file_path}: {e}")

        self.results["auth_analysis"] = auth_analysis

        print(f"📊 认证授权分析:")
        print(f"  - 认证机制: {len(auth_analysis['auth_mechanisms'])}")
        print(f"  - JWT使用: {len(auth_analysis['jwt_usage'])}")
        print(f"  - 会话管理: {len(auth_analysis['session_management'])}")
        print(f"  - 权限检查: {len(auth_analysis['permission_checks'])}")
        print(f"  - 认证漏洞: {len(auth_analysis['auth_vulnerabilities'])}")


    def check_data_encryption(self):
        """检查数据加密"""
        print("\n🔒 检查数据加密...")

        encryption_analysis = {
            "encryption_usage": [],
            "weak_encryption": [],
            "strong_encryption": [],
            "key_management": [],
            "ssl_tls_usage": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    # 检查加密库使用
                    encryption_libs = ['cryptography', 'pycrypto', 'hashlib', 'ssl']
                    for lib in encryption_libs:
                        if lib in stripped_line:
                            encryption_analysis["encryption_usage"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "library": lib
                            })

                    # 检查弱加密
                    weak_patterns = ['md5', 'sha1', 'des', 'rc4']
                    for pattern in weak_patterns:
                        if pattern in stripped_line.lower():
                            encryption_analysis["weak_encryption"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "algorithm": pattern,
                                "suggestion": "使用更强的加密算法"
                            })

                    # 检查强加密
                    strong_patterns = ['aes', 'sha256', 'sha512', 'rsa', 'ecdsa']
                    for pattern in strong_patterns:
                        if pattern in stripped_line.lower():
                            encryption_analysis["strong_encryption"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "algorithm": pattern
                            })

                    # 检查密钥管理
                    if any(pattern in stripped_line.lower() for pattern in
                          ['key', 'secret', 'password']):
                        if any(secure_pattern in stripped_line for secure_pattern in
                              ['os.environ', 'getenv', 'config']):
                            encryption_analysis["key_management"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "practice": "安全的密钥管理"
                            })

                    # 检查SSL/TLS
                    if any(pattern in stripped_line for pattern in
                          ['https://', 'ssl', 'tls', 'verify=True']):
                        encryption_analysis["ssl_tls_usage"].append({
                            "file": str(file_path),
                            "line": i + 1,
                            "usage": "SSL/TLS使用"
                        })

            except Exception as e:
                print(f"⚠️ 加密检查失败 {file_path}: {e}")

        self.results["encryption_analysis"] = encryption_analysis

        print(f"📊 数据加密分析:")
        print(f"  - 加密库使用: {len(encryption_analysis['encryption_usage'])}")
        print(f"  - 弱加密算法: {len(encryption_analysis['weak_encryption'])}")
        print(f"  - 强加密算法: {len(encryption_analysis['strong_encryption'])}")
        print(f"  - 安全密钥管理: {len(encryption_analysis['key_management'])}")
        print(f"  - SSL/TLS使用: {len(encryption_analysis['ssl_tls_usage'])}")


    def check_security_vulnerabilities(self):
        """检查安全漏洞"""
        print("\n🚨 检查安全漏洞...")

        vulnerability_analysis = {
            "high_risk_issues": [],
            "medium_risk_issues": [],
            "low_risk_issues": [],
            "sensitive_data_exposure": [],
            "injection_risks": []
        }

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines):
                    stripped_line = line.strip()

                    # 检查高风险问题
                    for pattern, description in self.security_patterns["high_risk"]:
                        if re.search(pattern, stripped_line):
                            vulnerability_analysis["high_risk_issues"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "issue": description,
                                "code": stripped_line,
                                "severity": "high"
                            })

                    # 检查中风险问题
                    for pattern, description in self.security_patterns["medium_risk"]:
                        if re.search(pattern, stripped_line):
                            vulnerability_analysis["medium_risk_issues"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "issue": description,
                                "code": stripped_line,
                                "severity": "medium"
                            })

                    # 检查低风险问题
                    for pattern, description in self.security_patterns["low_risk"]:
                        if re.search(pattern, stripped_line):
                            vulnerability_analysis["low_risk_issues"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "issue": description,
                                "code": stripped_line,
                                "severity": "low"
                            })

                    # 检查敏感数据暴露
                    for pattern, description in self.sensitive_patterns:
                        if re.search(pattern, stripped_line):
                            vulnerability_analysis["sensitive_data_exposure"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "issue": description,
                                "code": stripped_line[:50] + "..."
                            })

                    # 检查注入风险
                    injection_patterns = [
                        (r'\.format\s*\([^)]*input', 'SQL注入风险'),
                        (r'%\s*[^)]*input', '字符串格式化注入'),
                        (r'f["\'][^"\']*{[^}]*input', 'f-string注入风险')
                    ]

                    for pattern, description in injection_patterns:
                        if re.search(pattern, stripped_line):
                            vulnerability_analysis["injection_risks"].append({
                                "file": str(file_path),
                                "line": i + 1,
                                "issue": description,
                                "code": stripped_line
                            })

            except Exception as e:
                print(f"⚠️ 漏洞检查失败 {file_path}: {e}")

        self.results["vulnerability_analysis"] = vulnerability_analysis

        print(f"📊 安全漏洞分析:")
        print(f"  - 高风险问题: {len(vulnerability_analysis['high_risk_issues'])}")
        print(f"  - 中风险问题: {len(vulnerability_analysis['medium_risk_issues'])}")
        print(f"  - 低风险问题: {len(vulnerability_analysis['low_risk_issues'])}")
        print(f"  - 敏感数据暴露: {len(vulnerability_analysis['sensitive_data_exposure'])}")
        print(f"  - 注入风险: {len(vulnerability_analysis['injection_risks'])}")


    def generate_report(self):
        """生成安全性报告"""
        print("\n" + "="*60)
        print("🛡️ 安全性措施分析报告")
        print("="*60)

        total_files = len(self.python_files)

        # 计算安全分数
        total_vulnerabilities = (
            len(self.results["vulnerability_analysis"]["high_risk_issues"]) +
            len(self.results["vulnerability_analysis"]["medium_risk_issues"]) +
            len(self.results["vulnerability_analysis"]["low_risk_issues"])
        )

        security_score = max(0, 100 - (
            len(self.results["vulnerability_analysis"]["high_risk_issues"]) * 20 +
            len(self.results["vulnerability_analysis"]["medium_risk_issues"]) * 10 +
            len(self.results["vulnerability_analysis"]["low_risk_issues"]) * 5 +
            len(self.results["input_validation"]["unvalidated_inputs"]) * 3
        ))

        print(f"📊 安全评分: {security_score:.1f}/100")
        print(f"📁 分析文件总数: {total_files}")
        print(f"🚨 总漏洞数: {total_vulnerabilities}")

        print(f"\n🛡️ 安全措施统计:")
        print(f"  - 输入验证: {len(self.results['input_validation']['validated_inputs'])}")
        print(f"  - 认证机制: {len(self.results['auth_analysis']['auth_mechanisms'])}")
        print(f"  - 加密使用: {len(self.results['encryption_analysis']['encryption_usage'])}")

        print(f"\n⚠️ 安全风险:")
        print(f"  - 高风险: {len(self.results['vulnerability_analysis']['high_risk_issues'])}")
        print(f"  - 中风险: {len(self.results['vulnerability_analysis']['medium_risk_issues'])}")
        print(f"  - 低风险: {len(self.results['vulnerability_analysis']['low_risk_issues'])}")
        print(f"  - 敏感数据暴露: {len(self.results['vulnerability_analysis']['sensitive_data_exposure'])}")

        # 保存详细结果
        self.results["summary"] = {
            "timestamp": datetime.now().isoformat(),
            "total_files": total_files,
            "security_score": security_score,
            "total_vulnerabilities": total_vulnerabilities
        }

        with open("security_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 详细报告已保存到: security_analysis_report.json")

        return self.results


    def run_analysis(self):
        """运行完整的安全性分析"""
        self.scan_files()
        self.check_input_validation()
        self.check_authentication_authorization()
        self.check_data_encryption()
        self.check_security_vulnerabilities()
        return self.generate_report()


def main():
    checker = SecurityChecker()
    return checker.run_analysis()

if __name__ == "__main__":
    main()
