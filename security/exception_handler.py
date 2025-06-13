"""
异常处理机制
确保应用在遇到错误时能够优雅降级而不是崩溃
"""
import traceback
import functools
import sys
from typing import Any, Callable, Dict, Optional, Type, Union
from datetime import datetime
import streamlit as st
from enum import Enum

class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ErrorCategory(Enum):
    """错误类别"""
    API_ERROR = "API_ERROR"
    FILE_ERROR = "FILE_ERROR"
    MEMORY_ERROR = "MEMORY_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    USER_ERROR = "USER_ERROR"

class ExceptionHandler:
    """异常处理器"""
    
    def __init__(self):
        """初始化异常处理器"""
        self.error_counts = {}
        self.error_history = []
        self.recovery_strategies = {}
        self._setup_recovery_strategies()
    
    def _setup_recovery_strategies(self):
        """设置恢复策略"""
        self.recovery_strategies = {
            ErrorCategory.API_ERROR: self._handle_api_error,
            ErrorCategory.FILE_ERROR: self._handle_file_error,
            ErrorCategory.MEMORY_ERROR: self._handle_memory_error,
            ErrorCategory.NETWORK_ERROR: self._handle_network_error,
            ErrorCategory.VALIDATION_ERROR: self._handle_validation_error,
            ErrorCategory.SYSTEM_ERROR: self._handle_system_error,
            ErrorCategory.USER_ERROR: self._handle_user_error
        }
    
    def handle_exception(self, exception: Exception, context: Dict[str, Any] = None,
                        category: ErrorCategory = ErrorCategory.SYSTEM_ERROR,
                        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                        user_message: str = None) -> Dict[str, Any]:
        """
        处理异常
        
        Args:
            exception: 异常对象
            context: 上下文信息
            category: 错误类别
            severity: 错误严重程度
            user_message: 用户友好的错误消息
            
        Returns:
            处理结果字典
        """
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'category': category.value,
            'severity': severity.value,
            'context': context or {},
            'traceback': traceback.format_exc(),
            'session_id': self._get_session_id()
        }
        
        # 记录错误
        self._log_error(error_info)
        
        # 执行恢复策略
        recovery_result = self._execute_recovery_strategy(category, exception, context)
        
        # 显示用户友好的错误消息
        self._display_user_message(severity, user_message or recovery_result.get('user_message', '发生了未知错误'))
        
        return {
            'handled': True,
            'error_info': error_info,
            'recovery_result': recovery_result
        }
    
    def safe_execute(self, func: Callable, *args, fallback_value: Any = None,
                    category: ErrorCategory = ErrorCategory.SYSTEM_ERROR,
                    user_message: str = None, **kwargs) -> Any:
        """
        安全执行函数
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            fallback_value: 失败时的回退值
            category: 错误类别
            user_message: 用户错误消息
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果或回退值
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_exception(
                e, 
                context={'function': func.__name__, 'args': str(args)[:200]},
                category=category,
                user_message=user_message
            )
            return fallback_value
    
    def _log_error(self, error_info: Dict[str, Any]):
        """记录错误信息"""
        # 更新错误计数
        error_type = error_info['exception_type']
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # 添加到历史记录
        self.error_history.append(error_info)
        
        # 保持历史记录大小
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-50:]
        
        # 记录到session state（用于UI显示）
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
        
        st.session_state.error_log.append({
            'timestamp': error_info['timestamp'],
            'type': error_info['exception_type'],
            'message': error_info['exception_message'],
            'severity': error_info['severity']
        })
        
        # 保持session state日志大小
        if len(st.session_state.error_log) > 20:
            st.session_state.error_log = st.session_state.error_log[-10:]
    
    def _execute_recovery_strategy(self, category: ErrorCategory, 
                                 exception: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行恢复策略"""
        strategy = self.recovery_strategies.get(category, self._handle_system_error)
        return strategy(exception, context)
    
    def _handle_api_error(self, exception: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理API错误"""
        if "timeout" in str(exception).lower():
            return {
                'action': 'retry_with_longer_timeout',
                'user_message': 'API请求超时，请稍后重试',
                'recovery_suggestion': '检查网络连接或稍后重试'
            }
        else:
            return {
                'action': 'fallback_to_cache',
                'user_message': 'API服务暂时不可用，正在尝试使用缓存数据',
                'recovery_suggestion': '检查API配置或使用缓存数据'
            }
    
    def _handle_file_error(self, exception: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理文件错误"""
        return {
            'action': 'skip_file_processing',
            'user_message': '文件处理失败，已跳过该文件',
            'recovery_suggestion': '检查文件格式或尝试其他文件'
        }
    
    def _handle_memory_error(self, exception: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理内存错误"""
        return {
            'action': 'cleanup_memory',
            'user_message': '内存不足，正在清理缓存...',
            'recovery_suggestion': '减少数据量或重启应用'
        }
    
    def _handle_network_error(self, exception: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理网络错误"""
        return {
            'action': 'retry_with_backoff',
            'user_message': '网络连接失败，正在重试...',
            'recovery_suggestion': '检查网络连接'
        }
    
    def _handle_validation_error(self, exception: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理验证错误"""
        return {
            'action': 'prompt_correction',
            'user_message': f'输入验证失败：{str(exception)}',
            'recovery_suggestion': '请检查输入格式并重新提交'
        }
    
    def _handle_system_error(self, exception: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理系统错误"""
        return {
            'action': 'graceful_degradation',
            'user_message': '系统遇到错误，正在尝试恢复...',
            'recovery_suggestion': '如果问题持续，请刷新页面'
        }
    
    def _handle_user_error(self, exception: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户错误"""
        return {
            'action': 'provide_guidance',
            'user_message': '操作有误，请检查输入',
            'recovery_suggestion': '请按照提示正确操作'
        }
    
    def _display_user_message(self, severity: ErrorSeverity, message: str):
        """显示用户友好的错误消息"""
        if severity == ErrorSeverity.CRITICAL:
            st.error(f"🚨 严重错误：{message}")
        elif severity == ErrorSeverity.HIGH:
            st.error(f"❌ 错误：{message}")
        elif severity == ErrorSeverity.MEDIUM:
            st.warning(f"⚠️ 警告：{message}")
        else:
            st.info(f"ℹ️ 提示：{message}")
    
    def _get_session_id(self) -> str:
        """获取会话ID"""
        if 'session_id' not in st.session_state:
            import hashlib
            session_data = f"{datetime.now().isoformat()}_{id(st.session_state)}"
            st.session_state.session_id = hashlib.md5(session_data.encode()).hexdigest()[:16]
        return st.session_state.session_id
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        total_errors = sum(self.error_counts.values())
        
        return {
            'total_errors': total_errors,
            'error_counts': self.error_counts,
            'recent_errors': self.error_history[-10:] if self.error_history else [],
            'error_rate': len(self.error_history) / max(1, len(st.session_state.get('operation_count', [1])))
        }

def exception_handler(category: ErrorCategory = ErrorCategory.SYSTEM_ERROR,
                     severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                     user_message: str = None,
                     fallback_value: Any = None):
    """
    异常处理装饰器
    
    Args:
        category: 错误类别
        severity: 错误严重程度
        user_message: 用户错误消息
        fallback_value: 回退值
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = get_exception_handler()
                handler.handle_exception(
                    e,
                    context={'function': func.__name__},
                    category=category,
                    severity=severity,
                    user_message=user_message
                )
                return fallback_value
        return wrapper
    return decorator

# 全局实例
exception_handler_instance = ExceptionHandler()

def get_exception_handler() -> ExceptionHandler:
    """获取异常处理器实例"""
    return exception_handler_instance
