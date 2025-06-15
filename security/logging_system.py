"""
日志记录系统
实现详细的日志记录，包括用户操作、系统错误、性能监控
"""
import logging
import json

from typing import Any, Dict, Optional

from datetime import datetime, timedelta

from pathlib import Path
import streamlit as st

from logging.handlers import RotatingFileHandler

from enum import Enum


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """日志类别"""
    USER_ACTION = "USER_ACTION"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    API_CALL = "API_CALL"
    FILE_OPERATION = "FILE_OPERATION"
    CACHE_OPERATION = "CACHE_OPERATION"
    MEMORY_USAGE = "MEMORY_USAGE"


class SecurityLogger:
    """安全日志记录器"""


    def __init__(self, log_dir: str = "logs", max_file_size: int = 10*1024*1024,
                 backup_count: int = 5):
        """
        初始化日志记录器

        Args:
            log_dir: 日志目录
            max_file_size: 最大文件大小（字节）
            backup_count: 备份文件数量
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.max_file_size = max_file_size
        self.backup_count = backup_count

        # 初始化不同类别的日志记录器
        self.loggers = {}
        self._setup_loggers()

        # 内存中的日志缓存（用于实时显示）
        self.log_cache = {category.value: [] for category in LogCategory}
        self.cache_max_size = 100


    def _setup_loggers(self):
        """设置日志记录器"""
        for category in LogCategory:
            logger = logging.getLogger(f"security_{category.value.lower()}")
            logger.setLevel(logging.DEBUG)

            # 清除现有处理器
            logger.handlers.clear()

            # 文件处理器
            log_file = self.log_dir / f"{category.value.lower()}.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )

            # 日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            self.loggers[category] = logger


    def log(self, category: LogCategory, level: LogLevel, message: str,
            data: Dict[str, Any] = None, user_id: str = None):
        """
        记录日志

        Args:
            category: 日志类别
            level: 日志级别
            message: 日志消息
            data: 附加数据
            user_id: 用户ID
        """
        logger = self.loggers.get(category)
        if not logger:
            return

        # 构建日志数据
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'category': category.value,
            'level': level.value,
            'message': message,
            'session_id': self._get_session_id(),
            'user_id': user_id or 'anonymous',
            'data': data or {}
        }

        # 记录到文件
        log_message = json.dumps(log_data, ensure_ascii=False)
        getattr(logger, level.value.lower())(log_message)

        # 添加到内存缓存
        self._add_to_cache(category, log_data)


    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """记录用户操作"""
        self.log(
            LogCategory.USER_ACTION,
            LogLevel.INFO,
            f"User action: {action}",
            details
        )


    def log_system_error(self, error: str, details: Dict[str, Any] = None):
        """记录系统错误"""
        self.log(
            LogCategory.SYSTEM_ERROR,
            LogLevel.ERROR,
            f"System error: {error}",
            details
        )


    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """记录性能信息"""
        perf_data = {'operation': operation, 'duration_seconds': duration}
        if details:
            perf_data.update(details)

        self.log(
            LogCategory.PERFORMANCE,
            LogLevel.INFO,
            f"Performance: {operation} took {duration:.3f}s",
            perf_data
        )


    def log_security_event(self, event: str, severity: LogLevel = LogLevel.WARNING,
                          details: Dict[str, Any] = None):
        """记录安全事件"""
        self.log(
            LogCategory.SECURITY,
            severity,
            f"Security event: {event}",
            details
        )


    def log_api_call(self, endpoint: str, method: str, status_code: int = None,
                    duration: float = None, details: Dict[str, Any] = None):
        """记录API调用"""
        api_data = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'duration_seconds': duration
        }
        if details:
            api_data.update(details)

        level = LogLevel.INFO if status_code and status_code < 400 else LogLevel.WARNING

        self.log(
            LogCategory.API_CALL,
            level,
            f"API call: {method} {endpoint}",
            api_data
        )


    def _add_to_cache(self, category: LogCategory, log_data: Dict[str, Any]):
        """添加到内存缓存"""
        cache = self.log_cache[category.value]
        cache.append(log_data)

        # 保持缓存大小
        if len(cache) > self.cache_max_size:
            cache.pop(0)


    def _get_session_id(self) -> str:
        """获取会话ID"""
        if 'session_id' not in st.session_state:
            import hashlib

            session_data = f"{datetime.now().isoformat()}_{id(st.session_state)}"
            st.session_state.session_id = hashlib.md5(session_data.encode()).hexdigest()[:16]
        return st.session_state.session_id


    def get_recent_logs(self, category: LogCategory = None, limit: int = 50) -> list:
        """获取最近的日志"""
        if category:
            return self.log_cache[category.value][-limit:]
        else:
            # 合并所有类别的日志
            all_logs = []
            for logs in self.log_cache.values():
                all_logs.extend(logs)

            # 按时间排序
            all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
            return all_logs[:limit]


    def get_log_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """获取日志统计信息"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff_time.isoformat()

        stats = {
            'total_logs': 0,
            'by_category': {},
            'by_level': {},
            'error_count': 0,
            'warning_count': 0
        }

        for category_name, logs in self.log_cache.items():
            category_count = 0
            for log in logs:
                if log['timestamp'] >= cutoff_str:
                    category_count += 1
                    stats['total_logs'] += 1

                    level = log['level']
                    stats['by_level'][level] = stats['by_level'].get(level, 0) + 1

                    if level == 'ERROR':
                        stats['error_count'] += 1
                    elif level == 'WARNING':
                        stats['warning_count'] += 1

            if category_count > 0:
                stats['by_category'][category_name] = category_count

        return stats

# 性能监控装饰器


def log_performance(operation_name: str):
    """性能监控装饰器"""


    def decorator(func):


        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                security_logger.log_performance(operation_name, duration)
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                security_logger.log_performance(operation_name, duration, {'error': str(e)})
                raise
        return wrapper
    return decorator

# 全局实例
security_logger = SecurityLogger()


def get_security_logger() -> SecurityLogger:
    """获取安全日志记录器实例"""
    return security_logger
