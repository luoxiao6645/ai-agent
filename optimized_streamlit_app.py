"""
优化版智能多模态AI Agent - Streamlit应用
第二阶段：性能和用户体验优化
"""
import streamlit as st
import os
import sys
import asyncio
import json
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# 导入优化工具
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

# 页面配置已在app.py中设置，这里不再重复设置

# 初始化优化组件
if OPTIMIZATION_AVAILABLE:
    cache_manager = get_cache_manager()
    async_manager = get_async_manager()
    progress_tracker = get_progress_tracker()
    memory_optimizer = get_memory_optimizer()
    ui_components = get_ui_components()

# 自定义CSS样式
def load_custom_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
    /* 主题色彩 */
    :root {
        --primary-color: #FF6B6B;
        --secondary-color: #4ECDC4;
        --accent-color: #45B7D1;
        --background-color: #F8F9FA;
        --text-color: #2C3E50;
    }
    
    /* 主容器样式 */
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* 卡片样式 */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid var(--primary-color);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* 状态指示器 */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #2ECC71; }
    .status-warning { background-color: #F39C12; }
    .status-error { background-color: #E74C3C; }
    
    /* 性能指标样式 */
    .metric-container {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* 进度条样式 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-container {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .feature-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }
    
    /* 动画效果 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* 加载动画 */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid var(--primary-color);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化OpenAI客户端（带缓存）
@st.cache_resource
def init_client():
    """初始化AI客户端"""
    try:
        client = OpenAI(
            base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            api_key=os.getenv("ARK_API_KEY"),
        )
        return client
    except Exception as e:
        st.error(f"客户端初始化失败: {e}")
        return None

# 尝试导入完整系统组件
def try_import_full_system():
    """尝试导入完整系统组件"""
    try:
        # 添加项目根目录到Python路径
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from multimodal_agent.core.agent import MultiModalAgent
        from multimodal_agent.tools.tool_manager import ToolManager
        from config import Config
        return True, MultiModalAgent, ToolManager, Config
    except Exception as e:
        return False, None, None, None

# 检查系统能力
FULL_SYSTEM_AVAILABLE, MultiModalAgent, ToolManager, Config = try_import_full_system()

def main():
    """主界面"""
    # 加载自定义样式
    load_custom_css()
    
    # 内存监控（如果可用）
    if OPTIMIZATION_AVAILABLE:
        memory_optimizer.monitor_memory_usage()
    
    # 主标题
    st.markdown("""
    <div class="main-container fade-in">
        <h1 style="text-align: center; color: white; margin-bottom: 0;">
            🤖 智能多模态AI Agent系统
        </h1>
        <p style="text-align: center; color: rgba(255,255,255,0.8); font-size: 1.2em;">
            第二阶段优化版 - 性能与体验双重提升
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 系统状态显示
    display_system_status()
    
    # 初始化客户端
    client = init_client()
    if not client:
        st.error("❌ AI客户端初始化失败，请检查API配置")
        return
    
    # 侧边栏
    render_enhanced_sidebar(client)
    
    # 主界面标签页
    if FULL_SYSTEM_AVAILABLE and OPTIMIZATION_AVAILABLE:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💬 智能对话", "📁 文件处理", "🧮 工具箱", "🧠 记忆管理", "📊 性能监控"
        ])
        
        with tab1:
            enhanced_chat_interface(client)
        
        with tab2:
            enhanced_file_interface(client)
        
        with tab3:
            enhanced_tools_interface(client)
        
        with tab4:
            memory_interface()
        
        with tab5:
            performance_monitoring_interface()
    else:
        tab1, tab2, tab3 = st.tabs(["💬 智能对话", "📁 文件处理", "🧮 工具箱"])
        
        with tab1:
            optimized_chat_interface(client)
        
        with tab2:
            optimized_file_interface(client)
        
        with tab3:
            optimized_tools_interface(client)

def display_system_status():
    """显示系统状态"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if FULL_SYSTEM_AVAILABLE:
            st.markdown("""
            <div class="feature-card">
                <div class="status-indicator status-online"></div>
                <strong>完整系统</strong><br>
                <small>多模态Agent已启用</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="feature-card">
                <div class="status-indicator status-warning"></div>
                <strong>简化模式</strong><br>
                <small>基础功能可用</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if OPTIMIZATION_AVAILABLE:
            st.markdown("""
            <div class="feature-card">
                <div class="status-indicator status-online"></div>
                <strong>性能优化</strong><br>
                <small>缓存和异步已启用</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="feature-card">
                <div class="status-indicator status-warning"></div>
                <strong>标准模式</strong><br>
                <small>基础性能</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        current_time = datetime.now().strftime("%H:%M:%S")
        st.markdown(f"""
        <div class="feature-card">
            <div class="status-indicator status-online"></div>
            <strong>系统时间</strong><br>
            <small>{current_time}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if OPTIMIZATION_AVAILABLE:
            memory_usage = memory_optimizer.get_memory_usage()
            memory_mb = memory_usage.get('rss_mb', 0)
            st.markdown(f"""
            <div class="feature-card">
                <div class="status-indicator status-online"></div>
                <strong>内存使用</strong><br>
                <small>{memory_mb:.1f} MB</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="feature-card">
                <div class="status-indicator status-warning"></div>
                <strong>内存监控</strong><br>
                <small>不可用</small>
            </div>
            """, unsafe_allow_html=True)

def render_enhanced_sidebar(client):
    """渲染增强侧边栏"""
    with st.sidebar:
        st.markdown("## 🛠️ 系统控制")
        
        # 系统信息
        with st.expander("📊 系统信息", expanded=True):
            st.success("✅ AI客户端已连接")
            st.info(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
            
            if OPTIMIZATION_AVAILABLE:
                # 缓存统计
                cache_stats = cache_manager.get_cache_stats()
                st.metric("缓存命中率", f"{cache_stats['hit_rate']:.1f}%")
                st.metric("缓存大小", f"{cache_stats['cache_size']}")
        
        # 模型配置
        with st.expander("⚙️ 模型配置"):
            model = st.selectbox(
                "选择模型",
                [os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw")],
                index=0
            )
            
            temperature = st.slider("温度", 0.0, 1.0, 0.7, 0.1)
            max_tokens = st.slider("最大令牌数", 100, 2000, 500, 100)
        
        # 系统操作
        with st.expander("🔧 系统操作"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ 清除对话"):
                    st.session_state.messages = []
                    st.session_state.conversation_history = []
                    st.success("对话已清除")
            
            with col2:
                if st.button("🧹 清理缓存") and OPTIMIZATION_AVAILABLE:
                    cache_manager.clear_cache()
                    st.success("缓存已清理")
            
            if OPTIMIZATION_AVAILABLE:
                if st.button("🔄 内存优化"):
                    result = memory_optimizer.auto_cleanup()
                    st.success(f"已清理 {result.get('session_cleaned', 0)} 项")
        
        # 性能监控
        if OPTIMIZATION_AVAILABLE:
            with st.expander("📈 性能监控"):
                memory_stats = memory_optimizer.get_optimization_stats()
                
                st.metric("当前内存", f"{memory_stats['current_usage']['rss_mb']:.1f} MB")
                st.metric("峰值内存", f"{memory_stats['peak_usage']:.1f} MB")
                st.metric("清理次数", memory_stats['cleanup_count'])
                
                # 内存趋势
                trend_emoji = {
                    'increasing': '📈',
                    'decreasing': '📉', 
                    'stable': '➡️',
                    'unknown': '❓'
                }
                st.info(f"内存趋势: {trend_emoji.get(memory_stats['trend'], '❓')} {memory_stats['trend']}")

def enhanced_chat_interface(client):
    """增强版对话界面（完整系统+优化）"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3>💬 智能对话</h3>
        <p>使用完整AI Agent系统，支持工具调用和记忆管理</p>
    </div>
    """, unsafe_allow_html=True)

    # 初始化完整Agent
    if 'agent' not in st.session_state and FULL_SYSTEM_AVAILABLE:
        try:
            with ui_components['loading'].spinner_with_text("初始化完整AI Agent系统...", "processing"):
                st.session_state.agent = MultiModalAgent()
                st.success("✅ 完整AI Agent系统初始化成功")
        except Exception as e:
            st.error(f"完整系统初始化失败: {e}")
            optimized_chat_interface(client)
            return

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

    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成AI回复（使用完整Agent + 缓存）
        with st.chat_message("assistant"):
            process_enhanced_chat_input(client, prompt)

def optimized_chat_interface(client):
    """优化版对话界面（简化系统+缓存）"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3>💬 智能对话</h3>
        <p>使用缓存优化的对话系统，提升响应速度</p>
    </div>
    """, unsafe_allow_html=True)

    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if "processing_time" in message:
                    st.caption(f"⏱️ 处理时间: {message['processing_time']:.2f}秒")
                if "cached" in message and message["cached"]:
                    st.caption("🚀 来自缓存")

    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成AI回复（使用缓存优化）
        with st.chat_message("assistant"):
            process_optimized_chat_input(client, prompt)

def process_enhanced_chat_input(client, prompt):
    """处理增强版聊天输入"""
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
            "processing_time": 0.1
        })
    else:
        # 使用完整Agent处理
        with ui_components['loading'].spinner_with_text("AI Agent正在思考...", "thinking"):
            try:
                start_time = time.time()

                input_data = {
                    "type": "text",
                    "content": prompt
                }

                result = asyncio.run(st.session_state.agent.process_input(input_data))
                assistant_response = result.get('response', '处理失败')
                processing_time = time.time() - start_time

                st.markdown(assistant_response)

                # 缓存响应
                if OPTIMIZATION_AVAILABLE:
                    cache_manager.cache_response(prompt, model, 0.7, 500, assistant_response)

                # 添加助手回复到历史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "processing_time": processing_time,
                    "cached": False
                })

            except Exception as e:
                error_msg = f"处理失败: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

def process_optimized_chat_input(client, prompt):
    """处理优化版聊天输入"""
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
            "processing_time": 0.1
        })
    else:
        # 使用API调用
        with st.spinner("🤔 AI正在思考..."):
            try:
                start_time = time.time()

                # 构建消息历史
                messages = [
                    {"role": "system", "content": "你是豆包AI助手，一个智能、友好、有用的AI助手。"}
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

                st.markdown(assistant_response)

                # 缓存响应
                if OPTIMIZATION_AVAILABLE:
                    cache_manager.cache_response(prompt, model, 0.7, 500, assistant_response)

                # 添加助手回复到历史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "processing_time": processing_time,
                    "cached": False
                })

            except Exception as e:
                st.error(f"生成回复失败: {e}")

def enhanced_file_interface(client):
    """增强版文件处理界面"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3>📁 文件处理</h3>
        <p>支持多种文件格式的智能解析和批量处理</p>
    </div>
    """, unsafe_allow_html=True)

    # 使用增强的文件上传器
    if OPTIMIZATION_AVAILABLE:
        uploaded_file = ui_components['interactive'].enhanced_file_uploader(
            label="选择文件",
            accepted_types=['txt', 'md', 'json', 'csv', 'pdf', 'docx', 'xlsx'],
            max_size_mb=20,
            help_text="支持智能解析和批量处理，文件将被安全处理"
        )
    else:
        uploaded_file = st.file_uploader(
            "选择文件",
            type=['txt', 'md', 'json', 'csv', 'pdf', 'docx', 'xlsx']
        )

    if uploaded_file is not None:
        # 显示处理选项
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📖 智能解析", key="parse_file"):
                process_file_with_progress(uploaded_file, "解析")

        with col2:
            if st.button("📊 内容摘要", key="summarize_file"):
                process_file_with_progress(uploaded_file, "摘要")

        with col3:
            if st.button("🔍 关键信息提取", key="extract_file"):
                process_file_with_progress(uploaded_file, "提取")

def optimized_file_interface(client):
    """优化版文件处理界面"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3>📁 文件处理</h3>
        <p>优化的文件处理，支持缓存和进度显示</p>
    </div>
    """, unsafe_allow_html=True)

    # 文件上传
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['txt', 'md', 'json', 'csv'],
        help="支持文本文件、Markdown、JSON、CSV格式"
    )

    if uploaded_file is not None:
        # 显示文件信息
        st.success(f"✅ 文件上传成功: {uploaded_file.name}")
        st.info(f"文件大小: {uploaded_file.size} 字节")

        # 读取文件内容
        try:
            content = read_file_content(uploaded_file)

            # 显示文件内容预览
            st.subheader("📄 文件内容预览")
            st.text_area("内容", value=content[:1000] + "..." if len(content) > 1000 else content, height=200)

            # 文件分析选项
            st.subheader("🔍 文件分析")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📊 内容摘要"):
                    analyze_file_with_cache(client, content, "请对以下文件内容进行摘要总结")

            with col2:
                if st.button("🔍 关键信息提取"):
                    analyze_file_with_cache(client, content, "请提取以下文件内容中的关键信息")

        except Exception as e:
            st.error(f"文件读取失败: {e}")

def enhanced_tools_interface(client):
    """增强版工具箱界面"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3>🧮 AI工具箱</h3>
        <p>完整工具链系统，支持异步处理和批量操作</p>
    </div>
    """, unsafe_allow_html=True)

    if 'agent' not in st.session_state:
        st.error("Agent未初始化，无法使用工具")
        return

    # 工具类别选择
    tool_category = st.selectbox(
        "选择工具类别",
        ["💭 创意写作", "🔤 文本翻译", "📝 内容改写", "🧮 数学计算", "📊 数据分析", "🔍 网络搜索", "💻 代码执行"],
        key="enhanced_tool_category"
    )

    if tool_category == "💭 创意写作":
        enhanced_creative_writing_tool(client)
    elif tool_category == "🔤 文本翻译":
        enhanced_translation_tool(client)
    elif tool_category == "📝 内容改写":
        enhanced_rewriting_tool(client)
    elif tool_category == "🧮 数学计算":
        enhanced_math_tool(client)
    elif tool_category == "📊 数据分析":
        enhanced_data_analysis_tool(client)

def optimized_tools_interface(client):
    """优化版工具箱界面"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3>🧮 AI工具箱</h3>
        <p>缓存优化的工具系统，提升处理速度</p>
    </div>
    """, unsafe_allow_html=True)

    # 工具选择
    tool_option = st.selectbox(
        "选择工具",
        ["💭 创意写作", "🔤 文本翻译", "📝 内容改写", "🧮 数学计算", "📊 数据分析"],
        key="optimized_tool_option"
    )

    if tool_option == "💭 创意写作":
        optimized_creative_writing_tool(client)
    elif tool_option == "🔤 文本翻译":
        optimized_translation_tool(client)
    elif tool_option == "📝 内容改写":
        optimized_rewriting_tool(client)
    elif tool_option == "🧮 数学计算":
        optimized_math_tool(client)
    elif tool_option == "📊 数据分析":
        optimized_data_analysis_tool(client)

def memory_interface():
    """记忆管理界面"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3>🧠 记忆管理</h3>
        <p>智能记忆系统，支持搜索、统计和导出</p>
    </div>
    """, unsafe_allow_html=True)

    if 'agent' not in st.session_state:
        st.error("Agent未初始化，无法访问记忆系统")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 搜索记忆")
        search_query = st.text_input("输入搜索关键词", key="memory_search")
        if st.button("搜索", key="search_memory_btn") and search_query:
            search_memory_enhanced(search_query)

    with col2:
        st.subheader("📊 记忆统计")
        if st.button("查看统计信息", key="memory_stats_btn"):
            show_memory_stats()

    st.subheader("🗑️ 记忆管理")
    col3, col4 = st.columns(2)

    with col3:
        if st.button("清除所有记忆", type="secondary", key="clear_memory_btn"):
            clear_all_memory()

    with col4:
        if st.button("导出记忆", type="secondary", key="export_memory_btn"):
            export_memory()

def performance_monitoring_interface():
    """性能监控界面"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3>📊 性能监控</h3>
        <p>实时监控系统性能和资源使用情况</p>
    </div>
    """, unsafe_allow_html=True)

    if not OPTIMIZATION_AVAILABLE:
        st.warning("性能监控功能需要优化组件支持")
        return

    # 性能指标仪表板
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💾 内存监控")
        memory_stats = memory_optimizer.get_optimization_stats()

        # 内存使用图表
        if len(memory_stats.get('history', [])) > 1:
            import pandas as pd

            history_data = memory_stats['history'][-20:]  # 最近20条记录
            df = pd.DataFrame(history_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            st.line_chart(df.set_index('timestamp')['usage_mb'])

        # 内存指标
        ui_components['metrics'].performance_dashboard({
            'response_time': 0.5,  # 示例数据
            'cache_hit_rate': cache_manager.get_cache_stats()['hit_rate'],
            'total_requests': cache_manager.get_cache_stats()['total_requests'],
            'error_rate': 0.1
        })

    with col2:
        st.subheader("🚀 缓存监控")
        cache_stats = cache_manager.get_cache_stats()

        # 缓存指标
        st.metric("命中率", f"{cache_stats['hit_rate']:.1f}%")
        st.metric("缓存大小", f"{cache_stats['cache_size']}")
        st.metric("总请求数", cache_stats['total_requests'])

        # 缓存详细信息
        if st.button("查看缓存详情", key="cache_details_btn"):
            cache_info = cache_manager.get_cache_info()
            st.json(cache_info)

    # 系统建议
    st.subheader("💡 优化建议")
    recommendations = memory_optimizer.get_memory_recommendations()
    for i, recommendation in enumerate(recommendations):
        st.info(f"{i+1}. {recommendation}")

# 辅助函数
def process_file_with_progress(uploaded_file, action):
    """带进度显示的文件处理"""
    if not OPTIMIZATION_AVAILABLE:
        st.error("需要优化组件支持")
        return

    # 创建进度跟踪
    task_id = f"file_{action}_{int(time.time())}"
    progress_tracker.start_progress(task_id, 3, f"{action}文件中...")

    # 步骤1：读取文件
    progress_tracker.update_progress(task_id, 1, "读取文件...")
    progress_tracker.render_progress_bar(task_id)

    try:
        content = read_file_content(uploaded_file)

        # 步骤2：处理文件
        progress_tracker.update_progress(task_id, 2, f"{action}处理中...")
        progress_tracker.render_progress_bar(task_id)

        if 'agent' in st.session_state:
            input_data = {
                "type": "file",
                "content": content
            }
            result = asyncio.run(st.session_state.agent.process_input(input_data))

            # 步骤3：完成
            progress_tracker.update_progress(task_id, 3, "处理完成")
            progress_tracker.render_progress_bar(task_id)
            progress_tracker.complete_progress(task_id)

            st.success(f"✅ {action}完成")
            st.markdown("### 处理结果")
            st.markdown(result.get('response', '处理失败'))
        else:
            st.error("Agent未初始化")

    except Exception as e:
        st.error(f"{action}失败: {str(e)}")

def read_file_content(uploaded_file):
    """读取文件内容"""
    if uploaded_file.type == "text/plain" or uploaded_file.name.endswith('.md'):
        return uploaded_file.read().decode('utf-8')
    elif uploaded_file.name.endswith('.json'):
        import json
        return json.dumps(json.load(uploaded_file), ensure_ascii=False, indent=2)
    elif uploaded_file.name.endswith('.csv'):
        return uploaded_file.read().decode('utf-8')
    else:
        return str(uploaded_file.read())

def analyze_file_with_cache(client, content, instruction):
    """带缓存的文件分析"""
    model = os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw")

    # 检查缓存
    cache_key = f"{instruction}:{content[:100]}"
    cached_response = None

    if OPTIMIZATION_AVAILABLE:
        cached_response = cache_manager.get_cached_response(cache_key, model, 0.3, 800)

    if cached_response:
        st.success("✅ 分析完成（来自缓存）")
        st.markdown("### 分析结果")
        st.markdown(cached_response)
    else:
        with st.spinner("AI正在分析文件..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的文档分析助手。"},
                        {"role": "user", "content": f"{instruction}:\n\n{content[:3000]}"}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )

                result = response.choices[0].message.content

                # 缓存结果
                if OPTIMIZATION_AVAILABLE:
                    cache_manager.cache_response(cache_key, model, 0.3, 800, result)

                st.success("✅ 分析完成")
                st.markdown("### 分析结果")
                st.markdown(result)

            except Exception as e:
                st.error(f"分析失败: {e}")

# 优化版工具函数
def optimized_creative_writing_tool(client):
    """优化版创意写作工具"""
    st.subheader("💭 创意写作助手")

    # 使用智能文本输入
    if OPTIMIZATION_AVAILABLE:
        topic = ui_components['interactive'].smart_text_input(
            "主题或关键词",
            placeholder="请输入创作主题...",
            max_chars=200,
            suggestions=["科技创新", "环保生活", "人工智能", "未来世界", "教育改革"]
        )
    else:
        topic = st.text_input("主题或关键词")

    col1, col2, col3 = st.columns(3)

    with col1:
        writing_type = st.selectbox("写作类型", ["文章", "故事", "诗歌", "广告文案", "邮件"])

    with col2:
        style = st.selectbox("写作风格", ["正式", "轻松", "幽默", "专业", "创意"])

    with col3:
        length = st.selectbox("长度", ["简短", "中等", "详细"])

    if st.button("✨ 开始创作", key="optimized_creative_btn") and topic:
        create_content_with_cache(client, writing_type, topic, style, length)

def create_content_with_cache(client, writing_type, topic, style, length):
    """带缓存的内容创作"""
    model = os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw")
    prompt = f"请写一篇{style}风格的{writing_type}，主题是：{topic}。长度要求：{length}。"

    # 检查缓存
    cached_response = None
    if OPTIMIZATION_AVAILABLE:
        cached_response = cache_manager.get_cached_response(prompt, model, 0.8, 1000)

    if cached_response:
        st.success("✅ 创作完成（来自缓存）")
        st.markdown("### 创作结果")
        st.markdown(cached_response)
    else:
        with st.spinner("AI正在创作..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的创意写作助手。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=1000
                )

                result = response.choices[0].message.content

                # 缓存结果
                if OPTIMIZATION_AVAILABLE:
                    cache_manager.cache_response(prompt, model, 0.8, 1000, result)

                st.success("✅ 创作完成")
                st.markdown("### 创作结果")
                st.markdown(result)

            except Exception as e:
                st.error(f"创作失败: {e}")

# 其他优化工具函数的占位符
def optimized_translation_tool(client):
    """优化版翻译工具"""
    st.info("翻译工具优化版开发中...")

def optimized_rewriting_tool(client):
    """优化版改写工具"""
    st.info("改写工具优化版开发中...")

def optimized_math_tool(client):
    """优化版数学工具"""
    st.info("数学工具优化版开发中...")

def optimized_data_analysis_tool(client):
    """优化版数据分析工具"""
    st.info("数据分析工具优化版开发中...")

# 增强版工具函数的占位符
def enhanced_creative_writing_tool(client):
    """增强版创意写作工具"""
    st.info("增强版创意写作工具开发中...")

def enhanced_translation_tool(client):
    """增强版翻译工具"""
    st.info("增强版翻译工具开发中...")

def enhanced_rewriting_tool(client):
    """增强版改写工具"""
    st.info("增强版改写工具开发中...")

def enhanced_math_tool(client):
    """增强版数学工具"""
    st.info("增强版数学工具开发中...")

def enhanced_data_analysis_tool(client):
    """增强版数据分析工具"""
    st.info("增强版数据分析工具开发中...")

# 记忆管理函数
def search_memory_enhanced(query):
    """增强版记忆搜索"""
    with st.spinner("搜索记忆中..."):
        try:
            results = asyncio.run(st.session_state.agent.search_memory(query))

            if results:
                st.success(f"找到 {len(results)} 条相关记忆")
                for i, result in enumerate(results):
                    with st.expander(f"记忆 {i+1}"):
                        st.text(result.page_content)
                        if hasattr(result, 'metadata') and result.metadata:
                            st.json(result.metadata)
            else:
                st.info("未找到相关记忆")

        except Exception as e:
            st.error(f"搜索失败: {str(e)}")

def show_memory_stats():
    """显示记忆统计"""
    try:
        stats = st.session_state.agent.memory_manager.get_memory_stats()
        st.json(stats)
    except Exception as e:
        st.error(f"获取统计信息失败: {str(e)}")

def clear_all_memory():
    """清除所有记忆"""
    if st.button("确认清除", type="primary", key="confirm_clear_memory"):
        try:
            asyncio.run(st.session_state.agent.clear_memory())
            st.success("✅ 所有记忆已清除")
        except Exception as e:
            st.error(f"清除失败: {str(e)}")

def export_memory():
    """导出记忆"""
    st.info("记忆导出功能开发中...")

# 主函数可以被app.py导入和调用
if __name__ == "__main__":
    main()
