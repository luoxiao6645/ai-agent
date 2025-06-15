"""
增强版应用启动器

集成所有功能模块的统一启动入口
"""

import os
import sys
import threading
import time
import signal

from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入配置
from config import Config

# 导入性能优化模块
try:
    from performance import (

        get_cache_manager, get_connection_pool, get_async_processor,
        get_performance_monitor, OptimizationConfig
    )
    PERFORMANCE_AVAILABLE = True
    print("✅ 性能优化模块已加载")
except ImportError as e:
    PERFORMANCE_AVAILABLE = False
    print(f"⚠️ 性能优化模块未可用: {e}")

# 导入安全模块
try:
    from security import (

        get_input_validator, get_security_logger, get_exception_handler,
        get_session_manager, get_secrets_manager, get_security_auditor
    )
    SECURITY_AVAILABLE = True
    print("✅ 安全模块已加载")
except ImportError as e:
    SECURITY_AVAILABLE = False
    print(f"⚠️ 安全模块未可用: {e}")

# 导入健康检查
try:
    from health_check import start_health_server_thread

    HEALTH_CHECK_AVAILABLE = True
    print("✅ 健康检查模块已加载")
except ImportError as e:
    HEALTH_CHECK_AVAILABLE = False
    print(f"⚠️ 健康检查模块未可用: {e}")


class EnhancedAppManager:
    """增强版应用管理器"""


    def __init__(self):
        self.config = Config()
        self.running = False
        self.threads = []
        self.components = {}

        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)


    def initialize_components(self):
        """初始化所有组件"""
        print("🚀 正在初始化应用组件...")

        # 创建必要的目录
        self._create_directories()

        # 初始化性能组件
        if PERFORMANCE_AVAILABLE:
            self._initialize_performance_components()

        # 初始化安全组件
        if SECURITY_AVAILABLE:
            self._initialize_security_components()

        # 启动健康检查服务
        if HEALTH_CHECK_AVAILABLE:
            self._start_health_check_server()

        print("✅ 所有组件初始化完成")


    def _create_directories(self):
        """创建必要的目录"""
        directories = ['logs', 'cache', 'data', 'chroma_data']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        print("📁 目录结构已创建")


    def _initialize_performance_components(self):
        """初始化性能组件"""
        try:
            # 获取优化配置
            optimization_config = OptimizationConfig.from_env()
            self.components['optimization_config'] = optimization_config

            # 初始化缓存管理器
            if optimization_config.enable_caching:
                cache_manager = get_cache_manager()
                self.components['cache_manager'] = cache_manager
                print("📦 缓存管理器已初始化")

            # 初始化连接池
            if optimization_config.enable_connection_pooling:
                connection_pool = get_connection_pool()
                self.components['connection_pool'] = connection_pool
                print("🔗 连接池已初始化")

            # 初始化异步处理器
            if optimization_config.enable_async_processing:
                async_processor = get_async_processor()
                self.components['async_processor'] = async_processor
                print("⚡ 异步处理器已初始化")

            # 初始化性能监控
            if optimization_config.enable_performance_monitoring:
                performance_monitor = get_performance_monitor()
                self.components['performance_monitor'] = performance_monitor
                print("📊 性能监控已启动")

        except Exception as e:
            print(f"❌ 性能组件初始化失败: {e}")


    def _initialize_security_components(self):
        """初始化安全组件"""
        try:
            # 初始化输入验证器
            input_validator = get_input_validator()
            self.components['input_validator'] = input_validator

            # 初始化安全日志
            security_logger = get_security_logger()
            self.components['security_logger'] = security_logger

            # 初始化异常处理器
            exception_handler = get_exception_handler()
            self.components['exception_handler'] = exception_handler

            # 初始化会话管理器
            session_manager = get_session_manager()
            self.components['session_manager'] = session_manager

            # 初始化敏感信息管理器
            secrets_manager = get_secrets_manager()
            self.components['secrets_manager'] = secrets_manager

            # 初始化安全审计器
            security_auditor = get_security_auditor()
            self.components['security_auditor'] = security_auditor

            print("🛡️ 安全组件已初始化")

        except Exception as e:
            print(f"❌ 安全组件初始化失败: {e}")


    def _start_health_check_server(self):
        """启动健康检查服务器"""
        try:
            health_port = int(os.getenv('HEALTH_CHECK_PORT', '8080'))
            health_thread = start_health_server_thread(port=health_port)
            self.threads.append(health_thread)
            print(f"🏥 健康检查服务已启动 (端口: {health_port})")
        except Exception as e:
            print(f"❌ 健康检查服务启动失败: {e}")


    def start_streamlit_app(self):
        """启动Streamlit应用"""
        try:
            import streamlit.web.cli as stcli

            # 设置Streamlit参数
            streamlit_port = int(os.getenv('STREAMLIT_PORT', '8501'))
            streamlit_host = os.getenv('STREAMLIT_HOST', '0.0.0.0')

            # 选择应用文件 - 使用重构后的文件
            app_file = 'app.py'  # 使用重构后的统一应用文件
            if not Path(app_file).exists():
                app_file = 'quick_start.py'  # 备选文件

            print(f"🌐 启动Streamlit应用: {app_file}")
            print(f"📍 访问地址: http://{streamlit_host}:{streamlit_port}")

            # 设置Streamlit命令行参数
            sys.argv = [
                'streamlit', 'run', app_file,
                '--server.port', str(streamlit_port),
                '--server.address', streamlit_host,
                '--server.headless', 'true',
                '--browser.gatherUsageStats', 'false'
            ]

            self.running = True
            stcli.main()

        except Exception as e:
            print(f"❌ Streamlit应用启动失败: {e}")
            self.shutdown()


    def shutdown(self):
        """优雅关闭应用"""
        if not self.running:
            return

        print("\n🛑 正在关闭应用...")
        self.running = False

        # 关闭性能组件
        if PERFORMANCE_AVAILABLE:
            try:
                if 'async_processor' in self.components:
                    self.components['async_processor'].stop()
                    print("⚡ 异步处理器已关闭")

                if 'performance_monitor' in self.components:
                    self.components['performance_monitor'].stop_monitoring()
                    print("📊 性能监控已停止")

                if 'connection_pool' in self.components:
                    self.components['connection_pool'].close_all()
                    print("🔗 连接池已关闭")

            except Exception as e:
                print(f"⚠️ 性能组件关闭时出错: {e}")

        # 等待线程结束
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)

        print("✅ 应用已安全关闭")


    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n📡 收到信号 {signum}，正在关闭应用...")
        self.shutdown()
        sys.exit(0)


    def print_startup_info(self):
        """打印启动信息"""
        print("\n" + "="*60)
        print("🤖 智能多模态AI Agent - 增强版")
        print("="*60)
        print(f"📦 项目根目录: {project_root}")
        print(f"🐍 Python版本: {sys.version}")
        print(f"🔧 配置文件: {self.config}")

        print("\n📋 功能模块状态:")
        print(f"  🚀 性能优化: {'✅ 已启用' if PERFORMANCE_AVAILABLE else '❌ 未启用'}")
        print(f"  🛡️ 安全防护: {'✅ 已启用' if SECURITY_AVAILABLE else '❌ 未启用'}")
        print(f"  🏥 健康检查: {'✅ 已启用' if HEALTH_CHECK_AVAILABLE else '❌ 未启用'}")

        if PERFORMANCE_AVAILABLE and 'optimization_config' in self.components:
            config = self.components['optimization_config']
            print(f"\n⚡ 性能优化配置:")
            print(f"  📊 优化级别: {config.optimization_level}")
            print(f"  📦 缓存: {'✅' if config.enable_caching else '❌'}")
            print(f"  🔗 连接池: {'✅' if config.enable_connection_pooling else '❌'}")
            print(f"  ⚡ 异步处理: {'✅' if config.enable_async_processing else '❌'}")
            print(f"  📊 性能监控: {'✅' if config.enable_performance_monitoring else '❌'}")

        print("\n🌐 访问端点:")
        streamlit_port = os.getenv('STREAMLIT_PORT', '8501')
        health_port = os.getenv('HEALTH_CHECK_PORT', '8080')
        print(f"  📱 主应用: http://localhost:{streamlit_port}")
        if HEALTH_CHECK_AVAILABLE:
            print(f"  🏥 健康检查: http://localhost:{health_port}/health")
            print(f"  📊 系统指标: http://localhost:{health_port}/metrics")

        print("="*60)


def main():
    """主函数"""
    # 创建应用管理器
    app_manager = EnhancedAppManager()

    try:
        # 打印启动信息
        app_manager.print_startup_info()

        # 初始化组件
        app_manager.initialize_components()

        # 启动应用
        print("\n🚀 启动应用中...")
        app_manager.start_streamlit_app()

    except KeyboardInterrupt:
        print("\n⌨️ 用户中断")
    except Exception as e:
        print(f"\n❌ 应用启动失败: {e}")
        import traceback

        traceback.print_exc()
    finally:
        app_manager.shutdown()

if __name__ == "__main__":
    main()
