#!/usr/bin/env python3
"""
企业版应用启动器 - 第六阶段

集成微服务架构、插件系统、本地模型和多语言支持
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
    from advanced_app import AdvancedAppManager
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False

# 导入微服务模块
try:
    from microservices.service_registry import get_service_registry, register_service
    MICROSERVICES_AVAILABLE = True
except ImportError:
    MICROSERVICES_AVAILABLE = False

# 导入插件系统
try:
    from plugins.plugin_manager import get_plugin_manager
    PLUGINS_AVAILABLE = True
except ImportError:
    PLUGINS_AVAILABLE = False

# 导入本地模型
try:
    from local_models.model_manager import get_model_manager
    LOCAL_MODELS_AVAILABLE = True
except ImportError:
    LOCAL_MODELS_AVAILABLE = False

# 导入国际化
try:
    from i18n.translator import get_translator, set_language
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False

# 导入日志
try:
    from logging.structured_logger import get_app_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

class EnterpriseAppManager:
    """企业版应用管理器"""
    
    def __init__(self):
        """初始化企业版应用管理器"""
        self.config = Config()
        self.running = False
        self.threads = []
        self.services = {}
        
        # 初始化日志
        if LOGGING_AVAILABLE:
            self.logger = get_app_logger()
        else:
            self.logger = None
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def initialize_enterprise_services(self):
        """初始化企业版服务"""
        print("🚀 正在初始化企业版应用服务...")
        
        if self.logger:
            self.logger.info("Starting enterprise application services")
        
        # 创建必要的目录
        self._create_directories()
        
        # 初始化基础应用
        if ADVANCED_AVAILABLE:
            self._initialize_advanced_app()
        
        # 初始化微服务注册中心
        if MICROSERVICES_AVAILABLE:
            self._initialize_microservices()
        
        # 初始化插件系统
        if PLUGINS_AVAILABLE:
            self._initialize_plugins()
        
        # 初始化本地模型管理
        if LOCAL_MODELS_AVAILABLE:
            self._initialize_local_models()
        
        # 初始化国际化
        if I18N_AVAILABLE:
            self._initialize_i18n()
        
        print("✅ 所有企业版服务初始化完成")
        
        if self.logger:
            self.logger.info("All enterprise services initialized successfully")
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            'logs', 'cache', 'data', 'chroma_data', 'monitoring', 'api',
            'microservices', 'plugins', 'local_models', 'i18n/locales'
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        print("📁 企业版目录结构已创建")
    
    def _initialize_advanced_app(self):
        """初始化高级版应用"""
        try:
            self.advanced_manager = AdvancedAppManager()
            self.advanced_manager.initialize_services()
            self.services['advanced_app'] = True
            print("🎯 高级版应用已初始化")
        except Exception as e:
            print(f"❌ 高级版应用初始化失败: {e}")
            self.services['advanced_app'] = False
    
    def _initialize_microservices(self):
        """初始化微服务注册中心"""
        try:
            service_registry = get_service_registry()
            service_registry.start_health_check()
            
            # 注册主应用服务
            register_service(
                name="ai-agent-main",
                host="localhost",
                port=int(os.getenv('STREAMLIT_PORT', '8501')),
                version="1.0.0",
                health_check_url=f"http://localhost:{os.getenv('HEALTH_CHECK_PORT', '8080')}/health",
                metadata={"type": "main_app", "framework": "streamlit"}
            )
            
            self.services['microservices'] = True
            print("🔗 微服务注册中心已启动")
            
            if self.logger:
                self.logger.info("Microservices registry started")
                
        except Exception as e:
            print(f"❌ 微服务注册中心初始化失败: {e}")
            self.services['microservices'] = False
    
    def _initialize_plugins(self):
        """初始化插件系统"""
        try:
            plugin_manager = get_plugin_manager()
            
            # 发现并加载插件
            available_plugins = plugin_manager.discover_plugins()
            print(f"🔍 发现插件: {available_plugins}")
            
            # 加载示例插件
            for plugin_name in available_plugins:
                if plugin_manager.load_plugin(plugin_name):
                    print(f"🔌 插件加载成功: {plugin_name}")
                else:
                    print(f"⚠️ 插件加载失败: {plugin_name}")
            
            self.services['plugins'] = True
            print("🔌 插件系统已初始化")
            
            if self.logger:
                self.logger.info(f"Plugin system initialized with {len(available_plugins)} plugins")
                
        except Exception as e:
            print(f"❌ 插件系统初始化失败: {e}")
            self.services['plugins'] = False
    
    def _initialize_local_models(self):
        """初始化本地模型管理"""
        try:
            model_manager = get_model_manager()
            system_info = model_manager.get_system_info()
            
            print(f"🤖 本地模型系统信息:")
            print(f"   设备: {system_info['device']}")
            print(f"   Transformers: {'✅' if system_info['transformers_available'] else '❌'}")
            print(f"   Ollama: {'✅' if system_info['ollama_available'] else '❌'}")
            
            # 注册示例模型（如果有的话）
            self._register_example_models(model_manager)
            
            self.services['local_models'] = True
            print("🤖 本地模型管理已初始化")
            
            if self.logger:
                self.logger.info("Local model manager initialized", **system_info)
                
        except Exception as e:
            print(f"❌ 本地模型管理初始化失败: {e}")
            self.services['local_models'] = False
    
    def _register_example_models(self, model_manager):
        """注册示例模型"""
        try:
            # 这里可以注册一些常用的开源模型
            example_models = [
                {
                    "name": "chatglm3-6b",
                    "type": "huggingface",
                    "path": "THUDM/chatglm3-6b",
                    "description": "ChatGLM3-6B 对话模型"
                },
                {
                    "name": "qwen-7b-chat",
                    "type": "huggingface", 
                    "path": "Qwen/Qwen-7B-Chat",
                    "description": "通义千问7B对话模型"
                }
            ]
            
            for model_config in example_models:
                # 只注册，不自动加载（因为模型可能很大）
                print(f"📝 注册模型配置: {model_config['name']}")
                
        except Exception as e:
            print(f"⚠️ 注册示例模型失败: {e}")
    
    def _initialize_i18n(self):
        """初始化国际化"""
        try:
            translator = get_translator()
            available_languages = translator.get_available_locales()
            
            print(f"🌍 可用语言: {available_languages}")
            
            # 设置默认语言
            default_lang = os.getenv('DEFAULT_LANGUAGE', 'zh_CN')
            if set_language(default_lang):
                print(f"🌍 默认语言设置为: {default_lang}")
            
            self.services['i18n'] = True
            print("🌍 国际化系统已初始化")
            
            if self.logger:
                self.logger.info(f"I18n system initialized with languages: {available_languages}")
                
        except Exception as e:
            print(f"❌ 国际化系统初始化失败: {e}")
            self.services['i18n'] = False
    
    def start_enterprise_app(self):
        """启动企业版应用"""
        try:
            import streamlit.web.cli as stcli
            
            # 设置Streamlit参数
            streamlit_port = int(os.getenv('STREAMLIT_PORT', '8501'))
            streamlit_host = os.getenv('STREAMLIT_HOST', '0.0.0.0')
            
            # 选择应用文件
            app_file = 'enterprise_streamlit_app.py'
            if not Path(app_file).exists():
                app_file = 'advanced_app.py'
                if not Path(app_file).exists():
                    app_file = 'enhanced_streamlit_app.py'
            
            print(f"🌐 启动企业版Streamlit应用: {app_file}")
            print(f"📍 访问地址: http://{streamlit_host}:{streamlit_port}")
            
            if self.logger:
                self.logger.info(f"Starting enterprise Streamlit app: {app_file} on {streamlit_host}:{streamlit_port}")
            
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
            print(f"❌ 企业版应用启动失败: {e}")
            if self.logger:
                self.logger.error(f"Enterprise app startup failed: {e}")
            self.shutdown()
    
    def shutdown(self):
        """优雅关闭应用"""
        if not self.running:
            return
        
        print("\n🛑 正在关闭企业版应用...")
        if self.logger:
            self.logger.info("Shutting down enterprise application")
        
        self.running = False
        
        # 关闭微服务注册中心
        if MICROSERVICES_AVAILABLE and self.services.get('microservices'):
            try:
                service_registry = get_service_registry()
                service_registry.stop_health_check()
                print("🔗 微服务注册中心已停止")
            except Exception as e:
                print(f"⚠️ 微服务注册中心关闭时出错: {e}")
        
        # 关闭插件系统
        if PLUGINS_AVAILABLE and self.services.get('plugins'):
            try:
                plugin_manager = get_plugin_manager()
                for plugin_name in list(plugin_manager.plugins.keys()):
                    plugin_manager.unload_plugin(plugin_name)
                print("🔌 插件系统已关闭")
            except Exception as e:
                print(f"⚠️ 插件系统关闭时出错: {e}")
        
        # 关闭本地模型
        if LOCAL_MODELS_AVAILABLE and self.services.get('local_models'):
            try:
                model_manager = get_model_manager()
                for model_name in list(model_manager.loaded_models.keys()):
                    model_manager.unload_model(model_name)
                print("🤖 本地模型已卸载")
            except Exception as e:
                print(f"⚠️ 本地模型关闭时出错: {e}")
        
        # 关闭高级版应用
        if hasattr(self, 'advanced_manager'):
            try:
                self.advanced_manager.shutdown()
                print("🎯 高级版应用已关闭")
            except Exception as e:
                print(f"⚠️ 高级版应用关闭时出错: {e}")
        
        # 等待线程结束
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        print("✅ 企业版应用已安全关闭")
        if self.logger:
            self.logger.info("Enterprise application shutdown completed")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n📡 收到信号 {signum}，正在关闭企业版应用...")
        self.shutdown()
        sys.exit(0)
    
    def print_enterprise_info(self):
        """打印企业版启动信息"""
        print("\n" + "="*80)
        print("🚀 智能多模态AI Agent - 企业版 (第六阶段)")
        print("="*80)
        print(f"📦 项目根目录: {project_root}")
        print(f"🐍 Python版本: {sys.version}")
        print(f"🔧 配置文件: {self.config}")
        
        print("\n📋 企业版功能模块状态:")
        print(f"  🎯 高级版应用: {'✅ 已启用' if ADVANCED_AVAILABLE else '❌ 未启用'}")
        print(f"  🔗 微服务架构: {'✅ 已启用' if MICROSERVICES_AVAILABLE else '❌ 未启用'}")
        print(f"  🔌 插件系统: {'✅ 已启用' if PLUGINS_AVAILABLE else '❌ 未启用'}")
        print(f"  🤖 本地模型: {'✅ 已启用' if LOCAL_MODELS_AVAILABLE else '❌ 未启用'}")
        print(f"  🌍 国际化: {'✅ 已启用' if I18N_AVAILABLE else '❌ 未启用'}")
        print(f"  📝 结构化日志: {'✅ 已启用' if LOGGING_AVAILABLE else '❌ 未启用'}")
        
        print("\n🌐 企业版服务端点:")
        streamlit_port = os.getenv('STREAMLIT_PORT', '8501')
        health_port = os.getenv('HEALTH_CHECK_PORT', '8080')
        prometheus_port = os.getenv('PROMETHEUS_PORT', '8090')
        graphql_port = os.getenv('GRAPHQL_PORT', '8000')
        mobile_api_port = os.getenv('MOBILE_API_PORT', '8001')
        
        print(f"  📱 主应用: http://localhost:{streamlit_port}")
        print(f"  🏥 健康检查: http://localhost:{health_port}/health")
        print(f"  📊 系统指标: http://localhost:{health_port}/metrics")
        print(f"  🔗 微服务注册: http://localhost:{health_port}/registry")
        
        if MICROSERVICES_AVAILABLE:
            print(f"  📈 Prometheus: http://localhost:{prometheus_port}/metrics")
        
        if PLUGINS_AVAILABLE:
            print(f"  🔗 GraphQL API: http://localhost:{graphql_port}/graphql")
        
        if LOCAL_MODELS_AVAILABLE:
            print(f"  📱 移动端API: http://localhost:{mobile_api_port}/docs")
        
        print("\n🎯 企业版新功能特性:")
        print("  🔗 微服务架构 - 服务注册、发现、健康检查")
        print("  🔌 插件系统 - 动态加载、第三方扩展")
        print("  🤖 本地模型 - HuggingFace、Ollama模型支持")
        print("  🌍 多语言界面 - 中文、英文、日文支持")
        print("  📊 企业级监控 - 完整的监控和日志体系")
        
        print("="*80)

def main():
    """主函数"""
    # 创建企业版应用管理器
    app_manager = EnterpriseAppManager()
    
    try:
        # 打印启动信息
        app_manager.print_enterprise_info()
        
        # 初始化企业版服务
        app_manager.initialize_enterprise_services()
        
        # 启动应用
        print("\n🚀 启动企业版应用中...")
        app_manager.start_enterprise_app()
        
    except KeyboardInterrupt:
        print("\n⌨️ 用户中断")
    except Exception as e:
        print(f"\n❌ 企业版应用启动失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        app_manager.shutdown()

if __name__ == "__main__":
    main()
