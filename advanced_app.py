#!/usr/bin/env python3
"""
高级版应用启动器

集成第五阶段的所有新功能：监控、API、日志聚合等
"""

import os
import sys
import threading
import time
import signal
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入配置
from config import Config

# 导入基础模块
try:
    from enhanced_app import EnhancedAppManager
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

# 导入监控模块
try:
    from monitoring.prometheus_exporter import start_prometheus_monitoring, get_prometheus_exporter
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# 导入API模块
try:
    from api.graphql_server import start_graphql_server
    GRAPHQL_AVAILABLE = True
except ImportError:
    GRAPHQL_AVAILABLE = False

try:
    from api.mobile_api import start_mobile_api_server
    MOBILE_API_AVAILABLE = True
except ImportError:
    MOBILE_API_AVAILABLE = False

# 导入日志模块
try:
    from logging.structured_logger import get_app_logger, log_aggregator
    STRUCTURED_LOGGING_AVAILABLE = True
except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False

class AdvancedAppManager:
    """高级版应用管理器"""
    
    def __init__(self):
        """初始化高级版应用管理器"""
        self.config = Config()
        self.running = False
        self.threads = []
        self.services = {}
        
        # 初始化日志
        if STRUCTURED_LOGGING_AVAILABLE:
            self.logger = get_app_logger()
        else:
            self.logger = None
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def initialize_services(self):
        """初始化所有服务"""
        print("🚀 正在初始化高级版应用服务...")
        
        if self.logger:
            self.logger.info("Starting advanced application services")
        
        # 创建必要的目录
        self._create_directories()
        
        # 初始化基础应用
        if ENHANCED_AVAILABLE:
            self._initialize_enhanced_app()
        
        # 初始化监控服务
        if PROMETHEUS_AVAILABLE:
            self._initialize_prometheus_monitoring()
        
        # 初始化API服务
        if GRAPHQL_AVAILABLE:
            self._initialize_graphql_api()
        
        if MOBILE_API_AVAILABLE:
            self._initialize_mobile_api()
        
        print("✅ 所有高级服务初始化完成")
        
        if self.logger:
            self.logger.info("All advanced services initialized successfully")
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = ['logs', 'cache', 'data', 'chroma_data', 'monitoring', 'api']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        print("📁 目录结构已创建")
    
    def _initialize_enhanced_app(self):
        """初始化增强版应用"""
        try:
            self.enhanced_manager = EnhancedAppManager()
            self.enhanced_manager.initialize_components()
            self.services['enhanced_app'] = True
            print("🎯 增强版应用已初始化")
        except Exception as e:
            print(f"❌ 增强版应用初始化失败: {e}")
            self.services['enhanced_app'] = False
    
    def _initialize_prometheus_monitoring(self):
        """初始化Prometheus监控"""
        try:
            prometheus_port = int(os.getenv('PROMETHEUS_PORT', '8090'))
            success = start_prometheus_monitoring(port=prometheus_port)
            
            if success:
                self.services['prometheus'] = True
                print(f"📊 Prometheus监控已启动 (端口: {prometheus_port})")
                
                if self.logger:
                    self.logger.info(f"Prometheus monitoring started on port {prometheus_port}")
            else:
                self.services['prometheus'] = False
                print("⚠️ Prometheus监控启动失败")
                
        except Exception as e:
            print(f"❌ Prometheus监控初始化失败: {e}")
            self.services['prometheus'] = False
    
    def _initialize_graphql_api(self):
        """初始化GraphQL API"""
        try:
            graphql_port = int(os.getenv('GRAPHQL_PORT', '8000'))
            
            # 在后台线程启动GraphQL服务器
            graphql_thread = threading.Thread(
                target=start_graphql_server,
                args=("0.0.0.0", graphql_port),
                name="GraphQLServer",
                daemon=True
            )
            graphql_thread.start()
            self.threads.append(graphql_thread)
            
            self.services['graphql_api'] = True
            print(f"🔗 GraphQL API已启动 (端口: {graphql_port})")
            
            if self.logger:
                self.logger.info(f"GraphQL API started on port {graphql_port}")
                
        except Exception as e:
            print(f"❌ GraphQL API初始化失败: {e}")
            self.services['graphql_api'] = False
    
    def _initialize_mobile_api(self):
        """初始化移动端API"""
        try:
            mobile_api_port = int(os.getenv('MOBILE_API_PORT', '8001'))
            
            # 在后台线程启动移动端API服务器
            mobile_api_thread = threading.Thread(
                target=start_mobile_api_server,
                args=("0.0.0.0", mobile_api_port),
                name="MobileAPIServer",
                daemon=True
            )
            mobile_api_thread.start()
            self.threads.append(mobile_api_thread)
            
            self.services['mobile_api'] = True
            print(f"📱 移动端API已启动 (端口: {mobile_api_port})")
            
            if self.logger:
                self.logger.info(f"Mobile API started on port {mobile_api_port}")
                
        except Exception as e:
            print(f"❌ 移动端API初始化失败: {e}")
            self.services['mobile_api'] = False
    
    def start_streamlit_app(self):
        """启动Streamlit应用"""
        try:
            import streamlit.web.cli as stcli
            
            # 设置Streamlit参数
            streamlit_port = int(os.getenv('STREAMLIT_PORT', '8501'))
            streamlit_host = os.getenv('STREAMLIT_HOST', '0.0.0.0')
            
            # 选择应用文件
            app_file = 'enhanced_streamlit_app.py'
            if not Path(app_file).exists():
                app_file = 'secure_streamlit_app.py'
                if not Path(app_file).exists():
                    app_file = 'integrated_streamlit_app.py'
            
            print(f"🌐 启动Streamlit应用: {app_file}")
            print(f"📍 访问地址: http://{streamlit_host}:{streamlit_port}")
            
            if self.logger:
                self.logger.info(f"Starting Streamlit app: {app_file} on {streamlit_host}:{streamlit_port}")
            
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
            if self.logger:
                self.logger.error(f"Streamlit app startup failed: {e}")
            self.shutdown()
    
    def shutdown(self):
        """优雅关闭应用"""
        if not self.running:
            return
        
        print("\n🛑 正在关闭高级版应用...")
        if self.logger:
            self.logger.info("Shutting down advanced application")
        
        self.running = False
        
        # 关闭增强版应用
        if hasattr(self, 'enhanced_manager'):
            try:
                self.enhanced_manager.shutdown()
                print("🎯 增强版应用已关闭")
            except Exception as e:
                print(f"⚠️ 增强版应用关闭时出错: {e}")
        
        # 关闭Prometheus监控
        if PROMETHEUS_AVAILABLE and self.services.get('prometheus'):
            try:
                exporter = get_prometheus_exporter()
                if exporter:
                    exporter.stop_collector()
                print("📊 Prometheus监控已停止")
            except Exception as e:
                print(f"⚠️ Prometheus监控关闭时出错: {e}")
        
        # 等待线程结束
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        print("✅ 高级版应用已安全关闭")
        if self.logger:
            self.logger.info("Advanced application shutdown completed")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n📡 收到信号 {signum}，正在关闭应用...")
        self.shutdown()
        sys.exit(0)
    
    def print_startup_info(self):
        """打印启动信息"""
        print("\n" + "="*70)
        print("🚀 智能多模态AI Agent - 高级版 (第五阶段)")
        print("="*70)
        print(f"📦 项目根目录: {project_root}")
        print(f"🐍 Python版本: {sys.version}")
        print(f"🔧 配置文件: {self.config}")
        
        print("\n📋 服务模块状态:")
        print(f"  🎯 增强版应用: {'✅ 已启用' if ENHANCED_AVAILABLE else '❌ 未启用'}")
        print(f"  📊 Prometheus监控: {'✅ 已启用' if PROMETHEUS_AVAILABLE else '❌ 未启用'}")
        print(f"  🔗 GraphQL API: {'✅ 已启用' if GRAPHQL_AVAILABLE else '❌ 未启用'}")
        print(f"  📱 移动端API: {'✅ 已启用' if MOBILE_API_AVAILABLE else '❌ 未启用'}")
        print(f"  📝 结构化日志: {'✅ 已启用' if STRUCTURED_LOGGING_AVAILABLE else '❌ 未启用'}")
        
        print("\n🌐 访问端点:")
        streamlit_port = os.getenv('STREAMLIT_PORT', '8501')
        health_port = os.getenv('HEALTH_CHECK_PORT', '8080')
        prometheus_port = os.getenv('PROMETHEUS_PORT', '8090')
        graphql_port = os.getenv('GRAPHQL_PORT', '8000')
        mobile_api_port = os.getenv('MOBILE_API_PORT', '8001')
        
        print(f"  📱 主应用: http://localhost:{streamlit_port}")
        print(f"  🏥 健康检查: http://localhost:{health_port}/health")
        print(f"  📊 系统指标: http://localhost:{health_port}/metrics")
        
        if PROMETHEUS_AVAILABLE:
            print(f"  📈 Prometheus: http://localhost:{prometheus_port}/metrics")
        
        if GRAPHQL_AVAILABLE:
            print(f"  🔗 GraphQL API: http://localhost:{graphql_port}/graphql")
        
        if MOBILE_API_AVAILABLE:
            print(f"  📱 移动端API: http://localhost:{mobile_api_port}/docs")
        
        print("\n🎯 新功能特性:")
        print("  📊 Prometheus + Grafana监控栈")
        print("  🔗 GraphQL API接口")
        print("  📱 移动端优化API")
        print("  📝 结构化JSON日志")
        print("  🔍 ELK Stack日志分析支持")
        
        print("="*70)

def main():
    """主函数"""
    # 创建高级版应用管理器
    app_manager = AdvancedAppManager()
    
    try:
        # 打印启动信息
        app_manager.print_startup_info()
        
        # 初始化服务
        app_manager.initialize_services()
        
        # 启动应用
        print("\n🚀 启动高级版应用中...")
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
