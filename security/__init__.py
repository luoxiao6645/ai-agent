"""
安全模块
第三阶段：安全性和稳定性加固

包含以下安全组件：
- 输入验证和清理系统
- 异常处理机制
- 日志记录系统
- 会话状态管理
- API密钥安全处理
"""

from .input_validator import (

    InputValidator,
    SecurityAuditor,
    get_input_validator,
    get_security_auditor,
)
from .exception_handler import (

    ExceptionHandler, ErrorSeverity, ErrorCategory,
    exception_handler, get_exception_handler
)
from .logging_system import (

    SecurityLogger, LogLevel, LogCategory,
    log_performance, get_security_logger
)
from .session_manager import SessionManager, get_session_manager

from .secrets_manager import SecretsManager, get_secrets_manager

__all__ = [
    # 输入验证
    'InputValidator',
    'SecurityAuditor',
    'get_input_validator',
    'get_security_auditor',

    # 异常处理
    'ExceptionHandler',
    'ErrorSeverity',
    'ErrorCategory',
    'exception_handler',
    'get_exception_handler',

    # 日志记录
    'SecurityLogger',
    'LogLevel',
    'LogCategory',
    'log_performance',
    'get_security_logger',

    # 会话管理
    'SessionManager',
    'get_session_manager',

    # 敏感信息管理
    'SecretsManager',
    'get_secrets_manager'
]

# 版本信息
__version__ = "1.0.0"
__author__ = "AI Agent Security Team"
__description__ = "Security and stability hardening module for multimodal AI agent"
