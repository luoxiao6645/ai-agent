"""
输入验证和清理系统
防止注入攻击和恶意输入，确保所有用户输入的安全性
"""
import re
import html
import json
import hashlib
import mimetypes
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import streamlit as st
from datetime import datetime

class InputValidator:
    """输入验证器"""
    
    # 危险字符和模式
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # JavaScript
        r'javascript:',               # JavaScript协议
        r'on\w+\s*=',                # 事件处理器
        r'<iframe[^>]*>.*?</iframe>', # iframe标签
        r'<object[^>]*>.*?</object>', # object标签
        r'<embed[^>]*>.*?</embed>',   # embed标签
        r'eval\s*\(',                # eval函数
        r'exec\s*\(',                # exec函数
        r'import\s+os',               # 系统导入
        r'__import__',                # 动态导入
        r'subprocess',                # 子进程
        r'system\s*\(',               # 系统调用
    ]
    
    # 允许的文件类型
    ALLOWED_FILE_TYPES = {
        'text': ['.txt', '.md', '.csv', '.json', '.xml', '.yaml', '.yml'],
        'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
        'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
        'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
    }
    
    # 最大文件大小 (MB)
    MAX_FILE_SIZES = {
        'text': 10,
        'document': 50,
        'image': 20,
        'audio': 100,
        'video': 500
    }
    
    def __init__(self):
        """初始化验证器"""
        self.validation_stats = {
            'total_validations': 0,
            'blocked_inputs': 0,
            'file_validations': 0,
            'blocked_files': 0
        }
    
    def validate_text_input(self, text: str, max_length: int = 10000, 
                           allow_html: bool = False) -> Tuple[bool, str, str]:
        """
        验证文本输入
        
        Args:
            text: 输入文本
            max_length: 最大长度
            allow_html: 是否允许HTML
            
        Returns:
            (是否有效, 清理后的文本, 错误信息)
        """
        self.validation_stats['total_validations'] += 1
        
        if not isinstance(text, str):
            return False, "", "输入必须是字符串类型"
        
        # 长度检查
        if len(text) > max_length:
            return False, "", f"输入长度超过限制 ({max_length} 字符)"
        
        # 检查危险模式
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                self.validation_stats['blocked_inputs'] += 1
                return False, "", f"输入包含不安全内容"
        
        # 清理文本
        cleaned_text = self._clean_text(text, allow_html)
        
        return True, cleaned_text, ""
    
    def validate_file_upload(self, uploaded_file, allowed_categories: List[str] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        验证文件上传
        
        Args:
            uploaded_file: Streamlit上传的文件对象
            allowed_categories: 允许的文件类别
            
        Returns:
            (是否有效, 文件信息, 错误信息)
        """
        self.validation_stats['file_validations'] += 1
        
        if uploaded_file is None:
            return False, {}, "未选择文件"
        
        # 获取文件信息
        file_info = {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'type': uploaded_file.type,
            'extension': Path(uploaded_file.name).suffix.lower()
        }
        
        # 文件名验证
        if not self._validate_filename(file_info['name']):
            self.validation_stats['blocked_files'] += 1
            return False, file_info, "文件名包含不安全字符"
        
        # 文件类型验证
        category = self._get_file_category(file_info['extension'])
        if not category:
            self.validation_stats['blocked_files'] += 1
            return False, file_info, f"不支持的文件类型: {file_info['extension']}"
        
        if allowed_categories and category not in allowed_categories:
            self.validation_stats['blocked_files'] += 1
            return False, file_info, f"不允许的文件类别: {category}"
        
        # 文件大小验证
        max_size_mb = self.MAX_FILE_SIZES.get(category, 10)
        file_size_mb = file_info['size'] / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            self.validation_stats['blocked_files'] += 1
            return False, file_info, f"文件大小超过限制 ({max_size_mb}MB)"
        
        file_info['category'] = category
        file_info['size_mb'] = round(file_size_mb, 2)
        
        return True, file_info, ""
    
    def _clean_text(self, text: str, allow_html: bool = False) -> str:
        """清理文本内容"""
        if not allow_html:
            # HTML转义
            text = html.escape(text)
        
        # 移除控制字符（保留换行和制表符）
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # 标准化空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除首尾空白
        text = text.strip()
        
        return text
    
    def _validate_filename(self, filename: str) -> bool:
        """验证文件名安全性"""
        # 检查危险字符
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            if char in filename:
                return False
        
        return True
    
    def _get_file_category(self, extension: str) -> Optional[str]:
        """获取文件类别"""
        for category, extensions in self.ALLOWED_FILE_TYPES.items():
            if extension in extensions:
                return category
        return None
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """获取验证统计信息"""
        stats = self.validation_stats.copy()
        if stats['total_validations'] > 0:
            stats['block_rate'] = round((stats['blocked_inputs'] / stats['total_validations']) * 100, 2)
        else:
            stats['block_rate'] = 0
        
        if stats['file_validations'] > 0:
            stats['file_block_rate'] = round((stats['blocked_files'] / stats['file_validations']) * 100, 2)
        else:
            stats['file_block_rate'] = 0
        
        return stats

class SecurityAuditor:
    """安全审计器"""
    
    def __init__(self):
        """初始化审计器"""
        self.audit_log = []
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], 
                          severity: str = "INFO") -> None:
        """记录安全事件"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'severity': severity,
            'details': details,
            'session_id': self._get_session_id()
        }
        
        self.audit_log.append(event)
        
        # 保持日志大小
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-500:]
    
    def _get_session_id(self) -> str:
        """获取会话ID"""
        if 'session_id' not in st.session_state:
            # 生成唯一会话ID
            session_data = f"{datetime.now().isoformat()}_{id(st.session_state)}"
            st.session_state.session_id = hashlib.md5(session_data.encode()).hexdigest()[:16]
        
        return st.session_state.session_id
    
    def get_security_summary(self) -> Dict[str, Any]:
        """获取安全摘要"""
        if not self.audit_log:
            return {'total_events': 0, 'severity_counts': {}}
        
        severity_counts = {}
        for event in self.audit_log:
            severity = event['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_events': len(self.audit_log),
            'severity_counts': severity_counts,
            'recent_events': self.audit_log[-10:] if self.audit_log else []
        }

# 全局实例
input_validator = InputValidator()
security_auditor = SecurityAuditor()

def get_input_validator() -> InputValidator:
    """获取输入验证器实例"""
    return input_validator

def get_security_auditor() -> SecurityAuditor:
    """获取安全审计器实例"""
    return security_auditor
