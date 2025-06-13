"""
增强版Streamlit应用

集成性能优化、监控、缓存等功能的完整多模态AI Agent应用
"""

import streamlit as st
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# 导入核心模块
from config import Config
from multimodal_agent.core.agent import MultimodalAgent

# 导入安全模块
try:
    from security import (
        get_input_validator, get_security_logger, get_exception_handler,
        get_session_manager, get_secrets_manager, get_security_auditor
    )
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# 导入性能优化模块
try:
    from performance import (
        get_cache_manager, get_connection_pool, get_async_processor,
        get_performance_monitor, OptimizationConfig
    )
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

# 页面配置
st.set_page_config(
    page_title="智能多模态AI Agent - 增强版",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .performance-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .status-healthy { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-critical { color: #dc3545; }
    
    .cache-hit { background-color: #d4edda; padding: 0.5rem; border-radius: 4px; }
    .cache-miss { background-color: #f8d7da; padding: 0.5rem; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

def initialize_components():
    """初始化组件"""
    if 'initialized' not in st.session_state:
        # 初始化配置
        config = Config()
        st.session_state.config = config
        
        # 初始化Agent
        st.session_state.agent = MultimodalAgent(config)
        
        # 初始化性能组件
        if PERFORMANCE_AVAILABLE:
            st.session_state.cache_manager = get_cache_manager()
            st.session_state.connection_pool = get_connection_pool()
            st.session_state.async_processor = get_async_processor()
            st.session_state.performance_monitor = get_performance_monitor()
            st.session_state.optimization_config = OptimizationConfig.from_env()
        
        # 初始化安全组件
        if SECURITY_AVAILABLE:
            st.session_state.input_validator = get_input_validator()
            st.session_state.security_logger = get_security_logger()
            st.session_state.session_manager = get_session_manager()
            st.session_state.secrets_manager = get_secrets_manager()
            st.session_state.security_auditor = get_security_auditor()
        
        st.session_state.initialized = True

def render_header():
    """渲染页面头部"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 智能多模态AI Agent - 增强版</h1>
        <p>集成性能优化、安全防护、实时监控的完整AI助手</p>
    </div>
    """, unsafe_allow_html=True)

def render_performance_dashboard():
    """渲染性能仪表板"""
    if not PERFORMANCE_AVAILABLE:
        st.warning("性能监控模块未启用")
        return
    
    st.subheader("📊 性能监控仪表板")
    
    # 获取性能数据
    performance_monitor = st.session_state.performance_monitor
    cache_manager = st.session_state.cache_manager
    connection_pool = st.session_state.connection_pool
    async_processor = st.session_state.async_processor
    
    # 系统状态
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        system_status = performance_monitor.get_current_system_status()
        if system_status:
            status_class = f"status-{system_status.get('status', 'healthy')}"
            st.markdown(f"""
            <div class="metric-card">
                <h4 class="{status_class}">系统状态</h4>
                <p>CPU: {system_status.get('cpu_percent', 0):.1f}%</p>
                <p>内存: {system_status.get('memory_percent', 0):.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        cache_stats = cache_manager.get_stats()
        hit_rate = cache_stats.get('hit_rate_percent', 0)
        hit_class = 'cache-hit' if hit_rate > 70 else 'cache-miss'
        st.markdown(f"""
        <div class="metric-card {hit_class}">
            <h4>缓存性能</h4>
            <p>命中率: {hit_rate:.1f}%</p>
            <p>大小: {cache_stats.get('cache_size', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pool_stats = connection_pool.get_all_stats()
        default_pool = pool_stats.get('http_pool_default', {})
        success_rate = default_pool.get('success_rate', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h4>连接池</h4>
            <p>成功率: {success_rate:.1f}%</p>
            <p>活跃: {default_pool.get('active_connections', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        async_stats = async_processor.get_stats()
        success_rate = async_stats.get('success_rate', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h4>异步处理</h4>
            <p>成功率: {success_rate:.1f}%</p>
            <p>队列: {async_stats.get('queue_size', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 详细性能图表
    with st.expander("📈 详细性能数据", expanded=False):
        tab1, tab2, tab3 = st.tabs(["系统指标", "缓存统计", "连接池状态"])
        
        with tab1:
            system_metrics = performance_monitor.get_system_metrics(last_n=20)
            if system_metrics:
                import pandas as pd
                df = pd.DataFrame([
                    {
                        'timestamp': datetime.fromtimestamp(m.timestamp),
                        'CPU %': m.cpu_percent,
                        '内存 %': m.memory_percent,
                        '磁盘 %': m.disk_usage_percent
                    }
                    for m in system_metrics
                ])
                st.line_chart(df.set_index('timestamp'))
        
        with tab2:
            st.json(cache_stats)
        
        with tab3:
            st.json(pool_stats)

def render_chat_interface():
    """渲染对话界面"""
    st.subheader("💬 智能对话")
    
    # 对话历史
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 安全验证
        if SECURITY_AVAILABLE:
            input_validator = st.session_state.input_validator
            is_valid, cleaned_prompt, error_msg = input_validator.validate_text_input(prompt)
            if not is_valid:
                st.error(f"输入验证失败: {error_msg}")
                return
            prompt = cleaned_prompt
        
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 检查缓存
        cached_response = None
        if PERFORMANCE_AVAILABLE:
            cache_manager = st.session_state.cache_manager
            cached_response = cache_manager.get_cached_response(
                prompt, "gpt-3.5-turbo", 0.7, 500
            )
        
        # 生成回复
        with st.chat_message("assistant"):
            if cached_response:
                st.markdown("🎯 *从缓存获取回复*")
                st.markdown(cached_response)
                response = cached_response
            else:
                with st.spinner("AI正在思考..."):
                    start_time = time.time()
                    
                    try:
                        # 使用Agent处理
                        agent = st.session_state.agent
                        response = agent.process_text(prompt)
                        
                        processing_time = time.time() - start_time
                        
                        # 缓存响应
                        if PERFORMANCE_AVAILABLE:
                            cache_manager.cache_response(
                                prompt, "gpt-3.5-turbo", 0.7, 500, response
                            )
                        
                        # 记录性能指标
                        if PERFORMANCE_AVAILABLE:
                            performance_monitor = st.session_state.performance_monitor
                            performance_monitor.add_metric(
                                "response_time_ms", processing_time * 1000, "ms"
                            )
                        
                        st.markdown(response)
                        
                    except Exception as e:
                        if SECURITY_AVAILABLE:
                            exception_handler = st.session_state.exception_handler
                            exception_handler.handle_exception(e, {"prompt": prompt})
                        
                        response = f"抱歉，处理您的请求时出现错误: {str(e)}"
                        st.error(response)
        
        # 添加助手消息
        st.session_state.messages.append({"role": "assistant", "content": response})

def render_file_processing():
    """渲染文件处理界面"""
    st.subheader("📁 文件处理")
    
    uploaded_file = st.file_uploader(
        "选择文件", 
        type=['txt', 'pdf', 'docx', 'jpg', 'jpeg', 'png', 'mp3', 'wav']
    )
    
    if uploaded_file is not None:
        # 安全验证
        if SECURITY_AVAILABLE:
            input_validator = st.session_state.input_validator
            is_valid, error_msg = input_validator.validate_file_upload(uploaded_file)
            if not is_valid:
                st.error(f"文件验证失败: {error_msg}")
                return
        
        # 显示文件信息
        st.info(f"文件名: {uploaded_file.name}")
        st.info(f"文件大小: {uploaded_file.size} bytes")
        
        if st.button("处理文件"):
            with st.spinner("正在处理文件..."):
                try:
                    # 使用Agent处理文件
                    agent = st.session_state.agent
                    result = agent.process_file(uploaded_file)
                    
                    st.success("文件处理完成!")
                    st.markdown(result)
                    
                except Exception as e:
                    if SECURITY_AVAILABLE:
                        exception_handler = st.session_state.exception_handler
                        exception_handler.handle_exception(e, {"file": uploaded_file.name})
                    
                    st.error(f"文件处理失败: {str(e)}")

def render_system_settings():
    """渲染系统设置"""
    st.subheader("⚙️ 系统设置")
    
    if PERFORMANCE_AVAILABLE:
        st.markdown("### 性能优化设置")
        
        optimization_config = st.session_state.optimization_config
        
        # 优化级别
        optimization_level = st.selectbox(
            "优化级别",
            ["minimal", "balanced", "aggressive"],
            index=["minimal", "balanced", "aggressive"].index(optimization_config.optimization_level)
        )
        
        if optimization_level != optimization_config.optimization_level:
            optimization_config.optimization_level = optimization_level
            optimization_config._adjust_config_by_level()
            st.success("优化级别已更新")
        
        # 缓存设置
        with st.expander("缓存设置"):
            cache_enabled = st.checkbox("启用缓存", value=optimization_config.enable_caching)
            cache_size = st.slider("缓存大小", 100, 10000, optimization_config.cache.max_size)
            cache_ttl = st.slider("缓存TTL(秒)", 300, 7200, optimization_config.cache.default_ttl)
            
            if st.button("应用缓存设置"):
                optimization_config.enable_caching = cache_enabled
                optimization_config.cache.max_size = cache_size
                optimization_config.cache.default_ttl = cache_ttl
                st.success("缓存设置已更新")
        
        # 连接池设置
        with st.expander("连接池设置"):
            pool_enabled = st.checkbox("启用连接池", value=optimization_config.enable_connection_pooling)
            pool_size = st.slider("连接池大小", 5, 50, optimization_config.connection_pool.http_pool_size)
            
            if st.button("应用连接池设置"):
                optimization_config.enable_connection_pooling = pool_enabled
                optimization_config.connection_pool.http_pool_size = pool_size
                st.success("连接池设置已更新")
    
    if SECURITY_AVAILABLE:
        st.markdown("### 安全设置")
        
        with st.expander("安全统计"):
            input_validator = st.session_state.input_validator
            security_auditor = st.session_state.security_auditor
            
            validation_stats = input_validator.get_validation_stats()
            security_summary = security_auditor.get_security_summary()
            
            col1, col2 = st.columns(2)
            with col1:
                st.json(validation_stats)
            with col2:
                st.json(security_summary)

def main():
    """主函数"""
    # 初始化组件
    initialize_components()
    
    # 渲染页面头部
    render_header()
    
    # 侧边栏导航
    with st.sidebar:
        st.title("🎛️ 控制面板")
        
        page = st.selectbox(
            "选择功能",
            ["💬 智能对话", "📊 性能监控", "📁 文件处理", "⚙️ 系统设置"]
        )
        
        # 显示系统状态
        st.markdown("---")
        st.markdown("### 📈 系统状态")
        
        if PERFORMANCE_AVAILABLE:
            performance_monitor = st.session_state.performance_monitor
            system_status = performance_monitor.get_current_system_status()
            if system_status:
                status = system_status.get('status', 'unknown')
                status_emoji = {'healthy': '🟢', 'warning': '🟡', 'critical': '🔴'}.get(status, '⚪')
                st.markdown(f"{status_emoji} 系统状态: {status}")
                st.progress(system_status.get('cpu_percent', 0) / 100)
        
        if SECURITY_AVAILABLE:
            session_manager = st.session_state.session_manager
            session_info = session_manager.get_session_info()
            st.markdown(f"🔐 会话: {session_info.get('session_id', 'N/A')[:8]}...")
    
    # 主内容区域
    if page == "💬 智能对话":
        render_chat_interface()
    elif page == "📊 性能监控":
        render_performance_dashboard()
    elif page == "📁 文件处理":
        render_file_processing()
    elif page == "⚙️ 系统设置":
        render_system_settings()

if __name__ == "__main__":
    main()
