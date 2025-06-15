"""
日志配置
"""
import logging
import os

from datetime import datetime


def setup_logging(log_level="INFO", log_file=None):
    """
    设置日志配置

    Args:
        log_level: 日志级别
        log_file: 日志文件路径
    """
    # 创建日志目录
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 设置第三方库日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)

    logging.info(f"日志系统初始化完成 - 级别: {log_level}")

if __name__ == "__main__":
    # 测试日志配置
    setup_logging("INFO", "logs/test.log")

    logger = logging.getLogger(__name__)
    logger.info("这是一条测试日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
