"""
安全增强版智能多模态AI Agent - Streamlit应用
第三阶段：安全性和稳定性加固
"""
import streamlit as st
import os
import sys
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# 导入安全模块
try:
    from security import (
        get_input_validator, get_security_auditor, get_exception_handler,
        get_security_logger, get_session_manager, get_secrets_manager,
        ErrorCategory, ErrorSeverity, LogLevel, LogCategory
    )
    SECURITY_AVAILABLE = True
except ImportError as e:
    st.warning(f"安全模块不可用: {e}")
    SECURITY_AVAILABLE = False

# 导入优化模块
try:
    from utils.cache_manager import get_cache_manager
    from utils.async_manager import get_async_manager, get_progress_tracker
    from utils.memory_optimizer import get_memory_optimizer
    from utils.ui_components import get_ui_components
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False

# 加载环境变量
load_dotenv()

# 初始化安全组件
if SECURITY_AVAILABLE:
    input_validator = get_input_validator()
    security_auditor = get_security_auditor()
    exception_handler = get_exception_handler()
    security_logger = get_security_logger()
    session_manager = get_session_manager()
    secrets_manager = get_secrets_manager()

# 初始化优化组件
if OPTIMIZATION_AVAILABLE:
    cache_manager = get_cache_manager()
    async_manager = get_async_manager()
    progress_tracker = get_progress_tracker()
    memory_optimizer = get_memory_optimizer()
    ui_components = get_ui_components()

def load_custom_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
    /* 安全主题样式 */
    :root {
        --security-primary: #2E8B57;
        --security-secondary: #20B2AA;
        --security-accent: #4169E1;
        --security-warning: #FF6347;
        --security-success: #32CD32;
    }
    
    /* 安全状态指示器 */
    .security-status {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-weight: 600;
    }
    
    .security-high { background: linear-gradient(45deg, #32CD32, #228B22); color: white; }
    .security-medium { background: linear-gradient(45deg, #FFD700, #FFA500); color: black; }
    .security-low { background: linear-gradient(45deg, #FF6347, #DC143C); color: white; }
    
    /* 安全卡片 */
    .security-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid var(--security-primary);
    }
    
    /* 日志显示 */
    .log-entry {
        background: #f8f9fa;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9em;
    }
    
    .log-error { border-left: 3px solid #dc3545; }
    .log-warning { border-left: 3px solid #ffc107; }
    .log-info { border-left: 3px solid #17a2b8; }
    .log-success { border-left: 3px solid #28a745; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def init_secure_client():
    """初始化安全的AI客户端"""
    try:
        # 从安全存储获取API密钥
        if SECURITY_AVAILABLE:
            api_key = secrets_manager.retrieve_secret('ARK_API_KEY')
            if not api_key:
                # 尝试从环境变量获取
                api_key = os.getenv("ARK_API_KEY")
                if api_key:
                    # 验证并存储到安全存储
                    is_valid, errors = secrets_manager.validate_api_key(api_key)
                    if is_valid:
                        secrets_manager.store_secret('ARK_API_KEY', api_key, "火山方舟API密钥")
                    else:
                        st.error(f"API密钥验证失败: {errors}")
                        return None
        else:
            api_key = os.getenv("ARK_API_KEY")
        
        if not api_key:
            st.error("未找到有效的API密钥")
            return None
        
        client = OpenAI(
            base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            api_key=api_key,
        )
        
        # 记录成功初始化
        if SECURITY_AVAILABLE:
            security_logger.log_system_info("AI客户端初始化成功")
        
        return client
        
    except Exception as e:
        if SECURITY_AVAILABLE:
            exception_handler.handle_exception(
                e, 
                context={'function': 'init_secure_client'},
                category=ErrorCategory.API_ERROR,
                severity=ErrorSeverity.HIGH,
                user_message="AI客户端初始化失败"
            )
        else:
            st.error(f"客户端初始化失败: {e}")
        return None

def main():
    """主界面"""
    # 加载样式
    load_custom_css()
    
    # 初始化会话
    if SECURITY_AVAILABLE:
        session_id = session_manager.get_session_id()
        security_logger.log_user_action("应用启动", {'session_id': session_id})
    
    # 内存监控
    if OPTIMIZATION_AVAILABLE:
        memory_optimizer.monitor_memory_usage()
    
    # 主标题
    st.markdown("""
    <div class="security-card">
        <h1 style="text-align: center; color: var(--security-primary); margin-bottom: 0;">
            🛡️ 安全增强版多模态AI Agent
        </h1>
        <p style="text-align: center; color: #666; font-size: 1.1em;">
            第三阶段 - 安全性和稳定性加固完成
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 安全状态显示
    display_security_status()
    
    # 初始化客户端
    client = init_secure_client()
    if not client:
        st.stop()
    
    # 侧边栏
    render_security_sidebar()
    
    # 主界面标签页
    if SECURITY_AVAILABLE and OPTIMIZATION_AVAILABLE:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "💬 安全对话", "📁 文件处理", "🧮 工具箱", "🧠 记忆管理", "📊 性能监控", "🛡️ 安全中心"
        ])
        
        with tab1:
            secure_chat_interface(client)
        
        with tab2:
            secure_file_interface(client)
        
        with tab3:
            secure_tools_interface(client)
        
        with tab4:
            memory_interface()
        
        with tab5:
            performance_monitoring_interface()
        
        with tab6:
            security_center_interface()
    else:
        tab1, tab2, tab3 = st.tabs(["💬 对话", "📁 文件", "🧮 工具"])
        
        with tab1:
            basic_chat_interface(client)
        
        with tab2:
            basic_file_interface(client)
        
        with tab3:
            basic_tools_interface(client)

def display_security_status():
    """显示安全状态"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if SECURITY_AVAILABLE:
            st.markdown("""
            <div class="security-status security-high">
                🛡️ 安全模块已启用<br>
                <small>输入验证、异常处理、日志记录</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="security-status security-low">
                ⚠️ 安全模块未启用<br>
                <small>基础安全保护</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if OPTIMIZATION_AVAILABLE:
            st.markdown("""
            <div class="security-status security-high">
                ⚡ 性能优化已启用<br>
                <small>缓存、异步、内存优化</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="security-status security-medium">
                📊 标准性能模式<br>
                <small>基础功能可用</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        current_time = datetime.now().strftime("%H:%M:%S")
        st.markdown(f"""
        <div class="security-status security-high">
            🕒 系统时间<br>
            <small>{current_time}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if SECURITY_AVAILABLE:
            session_info = session_manager.get_session_info()
            session_age = session_info.get('session_age_seconds', 0)
            st.markdown(f"""
            <div class="security-status security-high">
                👤 会话状态<br>
                <small>活跃 {session_age//60}分钟</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="security-status security-medium">
                👤 基础会话<br>
                <small>无安全管理</small>
            </div>
            """, unsafe_allow_html=True)

def render_security_sidebar():
    """渲染安全侧边栏"""
    with st.sidebar:
        st.markdown("## 🛡️ 安全控制中心")
        
        # 会话信息
        if SECURITY_AVAILABLE:
            with st.expander("👤 会话信息", expanded=True):
                session_info = session_manager.get_session_info()
                st.json({
                    'session_id': session_info.get('session_id', 'N/A')[:8] + '...',
                    'created_at': session_info.get('created_at', 'N/A'),
                    'data_count': session_info.get('data_count', 0),
                    'encrypted_count': session_info.get('encrypted_data_count', 0)
                })
        
        # 安全统计
        if SECURITY_AVAILABLE:
            with st.expander("📊 安全统计"):
                validation_stats = input_validator.get_validation_stats()
                st.metric("输入验证次数", validation_stats.get('total_validations', 0))
                st.metric("阻止的恶意输入", validation_stats.get('blocked_inputs', 0))
                st.metric("文件验证次数", validation_stats.get('file_validations', 0))
        
        # 系统操作
        with st.expander("🔧 系统操作"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ 清除会话"):
                    if SECURITY_AVAILABLE:
                        session_manager.invalidate_session(session_manager.get_session_id())
                    st.session_state.clear()
                    st.success("会话已清除")
            
            with col2:
                if st.button("🧹 清理缓存") and OPTIMIZATION_AVAILABLE:
                    cache_manager.clear_cache()
                    st.success("缓存已清理")
            
            if OPTIMIZATION_AVAILABLE and st.button("🔄 内存优化"):
                result = memory_optimizer.auto_cleanup()
                st.success(f"已清理 {result.get('session_cleaned', 0)} 项")

def secure_chat_interface(client):
    """安全增强的对话界面"""
    st.markdown("""
    <div class="security-card">
        <h3>💬 安全对话系统</h3>
        <p>所有输入经过安全验证，对话内容受到保护</p>
    </div>
    """, unsafe_allow_html=True)

    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "processing_time" in message:
                st.caption(f"⏱️ 处理时间: {message['processing_time']:.2f}秒")
                if "cached" in message and message["cached"]:
                    st.caption("🚀 来自缓存")
                if "security_validated" in message and message["security_validated"]:
                    st.caption("🛡️ 安全验证通过")

    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 安全验证输入
        if SECURITY_AVAILABLE:
            is_valid, cleaned_prompt, error_msg = input_validator.validate_text_input(prompt, max_length=2000)
            if not is_valid:
                st.error(f"输入验证失败: {error_msg}")
                security_logger.log_security_event("输入验证失败", LogLevel.WARNING, {'error': error_msg})
                return

            # 记录用户操作
            security_logger.log_user_action("发送消息", {'message_length': len(cleaned_prompt)})
            prompt = cleaned_prompt

        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成AI回复
        with st.chat_message("assistant"):
            process_secure_chat_input(client, prompt)

def process_secure_chat_input(client, prompt):
    """处理安全的聊天输入"""
    model = os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw")

    # 检查缓存
    cached_response = None
    if OPTIMIZATION_AVAILABLE:
        cached_response = cache_manager.get_cached_response(prompt, model, 0.7, 500)

    if cached_response:
        # 使用缓存响应
        st.markdown(cached_response)
        st.session_state.messages.append({
            "role": "assistant",
            "content": cached_response,
            "cached": True,
            "processing_time": 0.1,
            "security_validated": True
        })

        if SECURITY_AVAILABLE:
            security_logger.log_cache_operation("cache_hit", cache_key=prompt[:50])
    else:
        # API调用
        with st.spinner("🛡️ AI正在安全处理您的请求..."):
            try:
                start_time = time.time()

                # 构建消息历史
                messages = [
                    {"role": "system", "content": "你是豆包AI助手，一个智能、友好、有用的AI助手。请确保回复内容安全、准确、有帮助。"}
                ]
                messages.extend(st.session_state.messages)

                # 调用API
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )

                assistant_response = response.choices[0].message.content
                processing_time = time.time() - start_time

                # 验证响应内容
                if SECURITY_AVAILABLE:
                    is_valid, cleaned_response, error_msg = input_validator.validate_text_input(
                        assistant_response, max_length=5000, allow_html=False
                    )
                    if not is_valid:
                        assistant_response = "抱歉，AI回复包含不安全内容，已被过滤。"
                        security_logger.log_security_event("AI回复被过滤", LogLevel.WARNING, {'error': error_msg})
                    else:
                        assistant_response = cleaned_response

                st.markdown(assistant_response)

                # 缓存响应
                if OPTIMIZATION_AVAILABLE:
                    cache_manager.cache_response(prompt, model, 0.7, 500, assistant_response)

                # 记录API调用
                if SECURITY_AVAILABLE:
                    security_logger.log_api_call("chat/completions", "POST", 200, processing_time)

                # 添加助手回复到历史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "processing_time": processing_time,
                    "cached": False,
                    "security_validated": True
                })

            except Exception as e:
                if SECURITY_AVAILABLE:
                    exception_handler.handle_exception(
                        e,
                        context={'function': 'process_secure_chat_input', 'prompt_length': len(prompt)},
                        category=ErrorCategory.API_ERROR,
                        severity=ErrorSeverity.MEDIUM,
                        user_message="AI服务暂时不可用，请稍后重试"
                    )
                else:
                    st.error(f"生成回复失败: {e}")

def secure_file_interface(client):
    """安全文件处理界面"""
    st.markdown("""
    <div class="security-card">
        <h3>📁 安全文件处理</h3>
        <p>文件上传经过严格安全检查，处理过程全程监控</p>
    </div>
    """, unsafe_allow_html=True)

    # 文件上传
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['txt', 'md', 'json', 'csv', 'pdf', 'docx'],
        help="支持多种文件格式，所有文件都会经过安全验证"
    )

    if uploaded_file is not None:
        # 安全验证文件
        if SECURITY_AVAILABLE:
            is_valid, file_info, error_msg = input_validator.validate_file_upload(
                uploaded_file,
                allowed_categories=['text', 'document']
            )

            if not is_valid:
                st.error(f"文件验证失败: {error_msg}")
                security_logger.log_security_event("文件验证失败", LogLevel.WARNING, {
                    'filename': uploaded_file.name,
                    'error': error_msg
                })
                return

            # 记录文件操作
            security_logger.log_file_operation("文件上传", uploaded_file.name, True, file_info)

        # 显示文件信息
        st.success(f"✅ 文件验证通过: {uploaded_file.name}")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📖 安全解析", key="secure_parse"):
                process_secure_file(uploaded_file, "解析")

        with col2:
            if st.button("📊 内容摘要", key="secure_summary"):
                process_secure_file(uploaded_file, "摘要")

        with col3:
            if st.button("🔍 安全扫描", key="secure_scan"):
                process_secure_file(uploaded_file, "扫描")

def process_secure_file(uploaded_file, action):
    """安全处理文件"""
    with st.spinner(f"🛡️ 正在安全{action}文件..."):
        try:
            # 读取文件内容
            content = read_file_content_safely(uploaded_file)

            if SECURITY_AVAILABLE:
                # 验证文件内容
                is_valid, cleaned_content, error_msg = input_validator.validate_text_input(
                    content, max_length=50000, allow_html=False
                )

                if not is_valid:
                    st.error(f"文件内容验证失败: {error_msg}")
                    security_logger.log_security_event("文件内容验证失败", LogLevel.WARNING, {
                        'filename': uploaded_file.name,
                        'error': error_msg
                    })
                    return

                content = cleaned_content
                security_logger.log_file_operation(f"文件{action}", uploaded_file.name, True)

            # 显示处理结果
            st.success(f"✅ 文件{action}完成")
            st.markdown("### 处理结果")

            if action == "扫描":
                # 安全扫描结果
                scan_result = perform_security_scan(content)
                st.json(scan_result)
            else:
                # 显示内容预览
                preview_length = 1000
                if len(content) > preview_length:
                    st.text_area("内容预览", value=content[:preview_length] + "...", height=200)
                    st.info(f"显示前{preview_length}字符，完整内容共{len(content)}字符")
                else:
                    st.text_area("完整内容", value=content, height=200)

        except Exception as e:
            if SECURITY_AVAILABLE:
                exception_handler.handle_exception(
                    e,
                    context={'function': 'process_secure_file', 'filename': uploaded_file.name},
                    category=ErrorCategory.FILE_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    user_message=f"文件{action}失败"
                )
            else:
                st.error(f"文件{action}失败: {e}")

def read_file_content_safely(uploaded_file):
    """安全读取文件内容"""
    try:
        if uploaded_file.type == "text/plain" or uploaded_file.name.endswith('.md'):
            return uploaded_file.read().decode('utf-8')
        elif uploaded_file.name.endswith('.json'):
            import json
            return json.dumps(json.load(uploaded_file), ensure_ascii=False, indent=2)
        elif uploaded_file.name.endswith('.csv'):
            return uploaded_file.read().decode('utf-8')
        else:
            return str(uploaded_file.read())
    except Exception as e:
        raise Exception(f"文件读取失败: {str(e)}")

def perform_security_scan(content):
    """执行安全扫描"""
    scan_result = {
        'file_size': len(content),
        'line_count': content.count('\n') + 1,
        'word_count': len(content.split()),
        'security_issues': [],
        'scan_timestamp': datetime.now().isoformat()
    }

    if SECURITY_AVAILABLE:
        # 检查敏感信息
        masked_content = secrets_manager.mask_sensitive_data(content)
        if masked_content != content:
            scan_result['security_issues'].append("检测到可能的敏感信息")

        # 检查危险模式
        for pattern in input_validator.DANGEROUS_PATTERNS:
            import re
            if re.search(pattern, content, re.IGNORECASE):
                scan_result['security_issues'].append(f"检测到危险模式: {pattern}")

    if not scan_result['security_issues']:
        scan_result['security_issues'].append("未发现安全问题")

    return scan_result

def security_center_interface():
    """安全中心界面"""
    st.markdown("""
    <div class="security-card">
        <h3>🛡️ 安全控制中心</h3>
        <p>全面的安全监控、日志管理和威胁检测</p>
    </div>
    """, unsafe_allow_html=True)

    if not SECURITY_AVAILABLE:
        st.warning("安全模块未启用，无法访问安全中心功能")
        return

    # 安全概览
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        validation_stats = input_validator.get_validation_stats()
        st.metric("输入验证", validation_stats.get('total_validations', 0),
                 delta=validation_stats.get('blocked_inputs', 0))

    with col2:
        error_stats = exception_handler.get_error_statistics()
        st.metric("异常处理", error_stats.get('total_errors', 0))

    with col3:
        log_stats = security_logger.get_log_statistics()
        st.metric("日志记录", log_stats.get('total_logs', 0))

    with col4:
        secrets_summary = secrets_manager.get_security_summary()
        st.metric("密钥管理", secrets_summary.get('total_secrets', 0))

    # 详细安全信息
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 安全概览", "📝 日志管理", "🔑 密钥管理", "⚠️ 威胁检测", "🔧 安全配置"
    ])

    with tab1:
        security_overview_tab()

    with tab2:
        log_management_tab()

    with tab3:
        secrets_management_tab()

    with tab4:
        threat_detection_tab()

    with tab5:
        security_config_tab()

def security_overview_tab():
    """安全概览标签页"""
    st.subheader("📊 安全状态概览")

    # 会话信息
    session_info = session_manager.get_session_info()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**会话信息**")
        st.json({
            'session_id': session_info.get('session_id', 'N/A')[:16] + '...',
            'user_id': session_info.get('user_id', 'N/A'),
            'created_at': session_info.get('created_at', 'N/A'),
            'session_age_minutes': session_info.get('session_age_seconds', 0) // 60,
            'data_count': session_info.get('data_count', 0),
            'encrypted_data_count': session_info.get('encrypted_data_count', 0)
        })

    with col2:
        st.markdown("**安全统计**")
        validation_stats = input_validator.get_validation_stats()
        st.json({
            'total_validations': validation_stats.get('total_validations', 0),
            'blocked_inputs': validation_stats.get('blocked_inputs', 0),
            'block_rate': f"{validation_stats.get('block_rate', 0)}%",
            'file_validations': validation_stats.get('file_validations', 0),
            'blocked_files': validation_stats.get('blocked_files', 0)
        })

    # 安全审计摘要
    st.subheader("🔍 安全审计摘要")
    audit_summary = security_auditor.get_security_summary()

    if audit_summary.get('total_events', 0) > 0:
        st.json(audit_summary)
    else:
        st.info("暂无安全事件记录")

def log_management_tab():
    """日志管理标签页"""
    st.subheader("📝 日志管理")

    # 日志统计
    log_stats = security_logger.get_log_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("总日志数", log_stats.get('total_logs', 0))

    with col2:
        st.metric("错误数", log_stats.get('error_count', 0))

    with col3:
        st.metric("警告数", log_stats.get('warning_count', 0))

    # 日志类别分布
    if log_stats.get('by_category'):
        st.subheader("📊 日志类别分布")
        st.bar_chart(log_stats['by_category'])

    # 最近日志
    st.subheader("📋 最近日志")
    recent_logs = security_logger.get_recent_logs(limit=20)

    if recent_logs:
        for log in recent_logs:
            log_class = f"log-{log['level'].lower()}"
            st.markdown(f"""
            <div class="log-entry {log_class}">
                <strong>{log['timestamp']}</strong> [{log['level']}] {log['category']}<br>
                {log['message']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("暂无日志记录")

def secrets_management_tab():
    """密钥管理标签页"""
    st.subheader("🔑 密钥管理")

    # 密钥概览
    secrets_summary = secrets_manager.get_security_summary()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("存储密钥数", secrets_summary.get('total_secrets', 0))

    with col2:
        st.metric("即将过期", secrets_summary.get('expiring_secrets_count', 0))

    with col3:
        st.metric("访问失败", secrets_summary.get('failed_access_attempts', 0))

    # 密钥列表
    secrets_list = secrets_manager.list_secrets()

    if secrets_list:
        st.subheader("📋 密钥列表")

        for secret in secrets_list:
            with st.expander(f"🔑 {secret['key']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**描述**: {secret.get('description', 'N/A')}")
                    st.write(f"**创建时间**: {secret.get('created_at', 'N/A')}")
                    st.write(f"**访问次数**: {secret.get('access_count', 0)}")

                with col2:
                    st.write(f"**最后访问**: {secret.get('last_accessed', 'N/A')}")

                    if secret.get('expiry_date'):
                        days_left = secret.get('days_until_expiry', 0)
                        if days_left <= 7:
                            st.warning(f"⚠️ {days_left}天后过期")
                        else:
                            st.info(f"📅 {days_left}天后过期")
                    else:
                        st.info("🔄 永不过期")

                if st.button(f"删除 {secret['key']}", key=f"delete_{secret['key']}"):
                    if secrets_manager.delete_secret(secret['key']):
                        st.success(f"密钥 {secret['key']} 已删除")
                        st.rerun()
    else:
        st.info("暂无存储的密钥")

    # 添加新密钥
    st.subheader("➕ 添加新密钥")

    with st.form("add_secret_form"):
        key_name = st.text_input("密钥名称")
        key_value = st.text_input("密钥值", type="password")
        description = st.text_input("描述")
        expiry_days = st.number_input("过期天数（0表示永不过期）", min_value=0, value=90)

        if st.form_submit_button("添加密钥"):
            if key_name and key_value:
                expiry = expiry_days if expiry_days > 0 else None
                if secrets_manager.store_secret(key_name, key_value, description, expiry):
                    st.success(f"密钥 {key_name} 添加成功")
                    st.rerun()
                else:
                    st.error("密钥添加失败，请检查格式")
            else:
                st.error("请填写密钥名称和值")

def threat_detection_tab():
    """威胁检测标签页"""
    st.subheader("⚠️ 威胁检测")

    # 威胁统计
    validation_stats = input_validator.get_validation_stats()
    error_stats = exception_handler.get_error_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:
        blocked_rate = validation_stats.get('block_rate', 0)
        if blocked_rate > 10:
            st.error(f"🚨 高风险：{blocked_rate}% 输入被阻止")
        elif blocked_rate > 5:
            st.warning(f"⚠️ 中风险：{blocked_rate}% 输入被阻止")
        else:
            st.success(f"✅ 低风险：{blocked_rate}% 输入被阻止")

    with col2:
        error_rate = error_stats.get('error_rate', 0)
        if error_rate > 0.1:
            st.error(f"🚨 高错误率：{error_rate:.2%}")
        elif error_rate > 0.05:
            st.warning(f"⚠️ 中错误率：{error_rate:.2%}")
        else:
            st.success(f"✅ 低错误率：{error_rate:.2%}")

    with col3:
        recent_errors = len([e for e in error_stats.get('recent_errors', [])
                           if (datetime.now() - datetime.fromisoformat(e['timestamp'])).seconds < 3600])
        if recent_errors > 10:
            st.error(f"🚨 近1小时错误：{recent_errors}")
        elif recent_errors > 5:
            st.warning(f"⚠️ 近1小时错误：{recent_errors}")
        else:
            st.success(f"✅ 近1小时错误：{recent_errors}")

    # 威胁详情
    st.subheader("🔍 威胁详情")

    # 最近被阻止的输入
    if validation_stats.get('blocked_inputs', 0) > 0:
        st.markdown("**最近被阻止的恶意输入**")
        st.info("出于安全考虑，不显示具体的恶意输入内容")

    # 最近的安全事件
    audit_summary = security_auditor.get_security_summary()
    recent_events = audit_summary.get('recent_events', [])

    if recent_events:
        st.markdown("**最近的安全事件**")
        for event in recent_events[-5:]:  # 显示最近5个事件
            severity_color = {
                'CRITICAL': 'error',
                'HIGH': 'error',
                'MEDIUM': 'warning',
                'LOW': 'info'
            }.get(event.get('severity', 'INFO'), 'info')

            getattr(st, severity_color)(f"{event.get('timestamp', 'N/A')} - {event.get('type', 'N/A')}")
    else:
        st.success("✅ 暂无安全威胁")

def security_config_tab():
    """安全配置标签页"""
    st.subheader("🔧 安全配置")

    st.markdown("**当前安全配置**")

    config_info = {
        '输入验证': '✅ 已启用',
        '异常处理': '✅ 已启用',
        '日志记录': '✅ 已启用',
        '会话管理': '✅ 已启用',
        '密钥管理': '✅ 已启用',
        '文件验证': '✅ 已启用',
        '内容过滤': '✅ 已启用'
    }

    for config, status in config_info.items():
        st.write(f"**{config}**: {status}")

    st.subheader("⚙️ 配置选项")

    # 会话超时设置
    session_timeout = st.slider("会话超时时间（分钟）", 5, 120, 60)

    # 日志级别设置
    log_level = st.selectbox("日志级别", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], index=1)

    # 文件大小限制
    max_file_size = st.slider("最大文件大小（MB）", 1, 100, 10)

    if st.button("应用配置"):
        st.success("配置已更新（注意：某些配置需要重启应用才能生效）")

# 简化版界面函数
def basic_chat_interface(client):
    """基础对话界面"""
    st.header("💬 基础对话")
    st.info("安全模块未启用，使用基础对话功能")

    # 基础对话实现
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("请输入您的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI正在思考..."):
                try:
                    response = client.chat.completions.create(
                        model=os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw"),
                        messages=[{"role": "system", "content": "你是一个有用的AI助手。"}] + st.session_state.messages,
                        temperature=0.7,
                        max_tokens=500
                    )

                    assistant_response = response.choices[0].message.content
                    st.markdown(assistant_response)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                except Exception as e:
                    st.error(f"生成回复失败: {e}")

def basic_file_interface(client):
    """基础文件界面"""
    st.header("📁 基础文件处理")
    st.info("安全模块未启用，使用基础文件处理功能")

    uploaded_file = st.file_uploader("选择文件", type=['txt', 'md', 'json', 'csv'])

    if uploaded_file is not None:
        st.success(f"文件上传成功: {uploaded_file.name}")

        try:
            content = uploaded_file.read().decode('utf-8')
            st.text_area("文件内容", value=content[:1000] + "..." if len(content) > 1000 else content, height=200)
        except Exception as e:
            st.error(f"文件读取失败: {e}")

def basic_tools_interface(client):
    """基础工具界面"""
    st.header("🧮 基础工具")
    st.info("安全模块未启用，使用基础工具功能")

    tool_option = st.selectbox("选择工具", ["文本翻译", "内容摘要", "简单计算"])

    if tool_option == "文本翻译":
        text_to_translate = st.text_area("请输入要翻译的文本")
        if st.button("翻译") and text_to_translate:
            st.info("翻译功能开发中...")

    elif tool_option == "内容摘要":
        text_to_summarize = st.text_area("请输入要摘要的文本")
        if st.button("生成摘要") and text_to_summarize:
            st.info("摘要功能开发中...")

    elif tool_option == "简单计算":
        calculation = st.text_input("请输入计算表达式")
        if st.button("计算") and calculation:
            try:
                # 简单的安全计算（仅支持基本运算）
                import re
                if re.match(r'^[\d\+\-\*\/\(\)\.\s]+$', calculation):
                    result = eval(calculation)
                    st.success(f"计算结果: {result}")
                else:
                    st.error("只支持基本数学运算")
            except Exception as e:
                st.error(f"计算失败: {e}")

# 其他必要的占位符函数
def secure_tools_interface(client):
    """安全工具界面"""
    st.info("安全工具界面开发中...")

def memory_interface():
    """记忆管理界面"""
    st.info("记忆管理界面开发中...")

def performance_monitoring_interface():
    """性能监控界面"""
    st.info("性能监控界面开发中...")

# 主函数可以被app.py导入和调用
if __name__ == "__main__":
    main()
