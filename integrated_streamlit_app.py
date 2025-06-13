"""
集成版智能多模态AI Agent - Streamlit应用
结合简化版的稳定性和完整版的功能
"""
import streamlit as st
import os
import sys
import asyncio
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 页面配置已在app.py中设置，这里不再重复设置

# 初始化OpenAI客户端
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
        # 不显示警告，静默处理
        return False, None, None, None

# 检查系统能力
FULL_SYSTEM_AVAILABLE, MultiModalAgent, ToolManager, Config = try_import_full_system()

def main():
    """主界面"""
    st.title("🤖 智能多模态AI Agent系统")
    
    # 显示系统状态
    if FULL_SYSTEM_AVAILABLE:
        st.success("✅ 完整多模态系统已启用")
        system_mode = "完整版"
    else:
        st.info("ℹ️ 使用简化版系统")
        system_mode = "简化版"
    
    st.markdown(f"**当前模式**: {system_mode}")
    st.markdown("---")
    
    # 初始化客户端
    client = init_client()
    if not client:
        st.error("❌ AI客户端初始化失败，请检查API配置")
        return
    
    # 侧边栏
    with st.sidebar:
        st.header("🛠️ 系统控制")
        
        # 系统状态
        st.subheader("📊 系统状态")
        st.success("✅ AI客户端已连接")
        st.info(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
        st.info(f"🔧 模式: {system_mode}")
        
        # 模型配置
        st.subheader("⚙️ 模型配置")
        model = st.selectbox(
            "选择模型",
            [os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw")],
            index=0
        )
        
        temperature = st.slider("温度", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.slider("最大令牌数", 100, 2000, 500, 100)
        
        # 清除对话
        if st.button("🗑️ 清除对话"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
        
        # 显示可用工具（如果是完整版）
        if FULL_SYSTEM_AVAILABLE:
            st.subheader("🔧 可用工具")
            try:
                if 'agent' in st.session_state:
                    tools = st.session_state.agent.tool_manager.get_tool_names()
                    for tool in tools[:5]:  # 只显示前5个
                        st.text(f"• {tool}")
                    if len(tools) > 5:
                        st.text(f"... 还有 {len(tools)-5} 个工具")
            except:
                st.text("工具信息加载中...")
    
    # 主界面标签页
    if FULL_SYSTEM_AVAILABLE:
        tab1, tab2, tab3, tab4 = st.tabs(["💬 智能对话", "📁 文件处理", "🧮 工具箱", "🧠 记忆管理"])
        
        with tab1:
            enhanced_chat_interface(client, model, temperature, max_tokens)
        
        with tab2:
            enhanced_file_interface(client, model)
        
        with tab3:
            enhanced_tools_interface(client, model)
        
        with tab4:
            memory_interface()
    else:
        tab1, tab2, tab3 = st.tabs(["💬 智能对话", "📁 文件处理", "🧮 工具箱"])
        
        with tab1:
            simple_chat_interface(client, model, temperature, max_tokens)
        
        with tab2:
            simple_file_interface(client, model)
        
        with tab3:
            simple_tools_interface(client, model)

def enhanced_chat_interface(client, model, temperature, max_tokens):
    """增强版对话界面（完整系统）"""
    st.header("💬 智能对话")
    
    # 初始化完整Agent
    if 'agent' not in st.session_state and FULL_SYSTEM_AVAILABLE:
        try:
            with st.spinner("初始化完整AI Agent系统..."):
                st.session_state.agent = MultiModalAgent()
                st.success("✅ 完整AI Agent系统初始化成功")
        except Exception as e:
            st.error(f"完整系统初始化失败: {e}")
            st.info("回退到简化版对话界面")
            simple_chat_interface(client, model, temperature, max_tokens)
            return
    
    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "processing_time" in message:
                st.caption(f"处理时间: {message['processing_time']:.2f}秒")
    
    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成AI回复（使用完整Agent）
        with st.chat_message("assistant"):
            with st.spinner("AI Agent正在思考..."):
                try:
                    # 使用完整的多模态Agent处理
                    input_data = {
                        "type": "text",
                        "content": prompt
                    }
                    
                    result = asyncio.run(st.session_state.agent.process_input(input_data))
                    assistant_response = result.get('response', '处理失败')
                    processing_time = result.get('processing_time', 0)
                    
                    st.markdown(assistant_response)
                    
                    # 添加助手回复到历史
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": assistant_response,
                        "processing_time": processing_time
                    })
                    
                except Exception as e:
                    error_msg = f"处理失败: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })

def simple_chat_interface(client, model, temperature, max_tokens):
    """简化版对话界面"""
    st.header("💬 智能对话")
    
    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成AI回复
        with st.chat_message("assistant"):
            with st.spinner("AI正在思考..."):
                try:
                    # 构建消息历史
                    messages = [
                        {"role": "system", "content": "你是豆包AI助手，一个智能、友好、有用的AI助手。"}
                    ]
                    messages.extend(st.session_state.messages)
                    
                    # 调用API
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    assistant_response = response.choices[0].message.content
                    st.markdown(assistant_response)
                    
                    # 添加助手回复到历史
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": assistant_response
                    })
                    
                except Exception as e:
                    st.error(f"生成回复失败: {e}")

def enhanced_file_interface(client, model):
    """增强版文件处理界面"""
    st.header("📁 文件处理")
    st.info("🚀 使用完整多模态处理系统")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择文件", 
        type=['txt', 'md', 'json', 'csv', 'pdf', 'docx', 'xlsx'],
        help="支持多种文件格式的智能解析"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        st.success(f"✅ 文件上传成功: {uploaded_file.name}")
        st.info(f"文件大小: {uploaded_file.size} 字节")
        
        # 保存临时文件
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📖 智能解析"):
                process_file_with_agent(temp_path, "解析")
        
        with col2:
            if st.button("📊 内容摘要"):
                process_file_with_agent(temp_path, "摘要")
        
        with col3:
            if st.button("🔍 关键信息提取"):
                process_file_with_agent(temp_path, "提取")
        
        # 清理临时文件
        try:
            os.remove(temp_path)
        except:
            pass

def simple_file_interface(client, model):
    """简化版文件处理界面"""
    st.header("📁 文件处理")
    
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
            if uploaded_file.type == "text/plain" or uploaded_file.name.endswith('.md'):
                content = uploaded_file.read().decode('utf-8')
            elif uploaded_file.name.endswith('.json'):
                content = json.dumps(json.load(uploaded_file), ensure_ascii=False, indent=2)
            elif uploaded_file.name.endswith('.csv'):
                content = uploaded_file.read().decode('utf-8')
            else:
                content = str(uploaded_file.read())
            
            # 显示文件内容预览
            st.subheader("📄 文件内容预览")
            st.text_area("内容", value=content[:1000] + "..." if len(content) > 1000 else content, height=200)
            
            # 文件分析选项
            st.subheader("🔍 文件分析")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 内容摘要"):
                    analyze_file_content(client, model, content, "请对以下文件内容进行摘要总结")
            
            with col2:
                if st.button("🔍 关键信息提取"):
                    analyze_file_content(client, model, content, "请提取以下文件内容中的关键信息")
            
        except Exception as e:
            st.error(f"文件读取失败: {e}")

def process_file_with_agent(file_path, action):
    """使用Agent处理文件"""
    if 'agent' not in st.session_state:
        st.error("Agent未初始化")
        return
    
    with st.spinner(f"正在{action}文件..."):
        try:
            input_data = {
                "type": "file",
                "content": file_path
            }
            
            result = asyncio.run(st.session_state.agent.process_input(input_data))
            
            st.success(f"✅ {action}完成")
            st.markdown("### 处理结果")
            st.markdown(result.get('response', '处理失败'))
            
            if 'processing_time' in result:
                st.caption(f"处理时间: {result['processing_time']:.2f}秒")
                
        except Exception as e:
            st.error(f"{action}失败: {str(e)}")

def analyze_file_content(client, model, content, instruction):
    """分析文件内容"""
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
            st.success("✅ 分析完成")
            st.markdown("### 分析结果")
            st.markdown(result)
            
        except Exception as e:
            st.error(f"分析失败: {e}")

def enhanced_tools_interface(client, model):
    """增强版工具箱界面"""
    st.header("🧮 AI工具箱")
    st.info("🚀 使用完整工具链系统")

    if 'agent' not in st.session_state:
        st.error("Agent未初始化，无法使用工具")
        return

    # 工具类别选择
    tool_category = st.selectbox(
        "选择工具类别",
        ["💭 创意写作", "🔤 文本翻译", "📝 内容改写", "🧮 数学计算", "📊 数据分析", "🔍 网络搜索", "💻 代码执行"]
    )

    if tool_category == "💭 创意写作":
        creative_writing_tool_enhanced(client, model)
    elif tool_category == "🔤 文本翻译":
        translation_tool_enhanced(client, model)
    elif tool_category == "📝 内容改写":
        rewriting_tool_enhanced(client, model)
    elif tool_category == "🧮 数学计算":
        math_tool_enhanced(client, model)
    elif tool_category == "📊 数据分析":
        data_analysis_tool_enhanced(client, model)
    elif tool_category == "🔍 网络搜索":
        web_search_tool_enhanced()
    elif tool_category == "💻 代码执行":
        code_execution_tool_enhanced()

def simple_tools_interface(client, model):
    """简化版工具箱界面"""
    st.header("🧮 AI工具箱")

    # 工具选择
    tool_option = st.selectbox(
        "选择工具",
        ["💭 创意写作", "🔤 文本翻译", "📝 内容改写", "🧮 数学计算", "📊 数据分析"]
    )

    if tool_option == "💭 创意写作":
        creative_writing_tool(client, model)
    elif tool_option == "🔤 文本翻译":
        translation_tool(client, model)
    elif tool_option == "📝 内容改写":
        rewriting_tool(client, model)
    elif tool_option == "🧮 数学计算":
        math_tool(client, model)
    elif tool_option == "📊 数据分析":
        data_analysis_tool(client, model)

def memory_interface():
    """记忆管理界面"""
    st.header("🧠 记忆管理")

    if 'agent' not in st.session_state:
        st.error("Agent未初始化，无法访问记忆系统")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 搜索记忆")
        search_query = st.text_input("输入搜索关键词")
        if st.button("搜索") and search_query:
            search_memory_enhanced(search_query)

    with col2:
        st.subheader("📊 记忆统计")
        if st.button("查看统计信息"):
            show_memory_stats()

    st.subheader("🗑️ 记忆管理")
    col3, col4 = st.columns(2)

    with col3:
        if st.button("清除所有记忆", type="secondary"):
            clear_all_memory()

    with col4:
        if st.button("导出记忆", type="secondary"):
            export_memory()

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
    if st.button("确认清除", type="primary"):
        try:
            asyncio.run(st.session_state.agent.clear_memory())
            st.success("✅ 所有记忆已清除")
        except Exception as e:
            st.error(f"清除失败: {str(e)}")

def export_memory():
    """导出记忆"""
    st.info("记忆导出功能开发中...")

# 增强版工具函数
def creative_writing_tool_enhanced(client, model):
    """增强版创意写作工具"""
    st.subheader("💭 创意写作助手")

    writing_type = st.selectbox("写作类型", ["文章", "故事", "诗歌", "广告文案", "邮件", "报告", "演讲稿"])
    topic = st.text_input("主题或关键词")
    style = st.selectbox("写作风格", ["正式", "轻松", "幽默", "专业", "创意", "学术", "商务"])
    length = st.selectbox("长度", ["简短", "中等", "详细", "长篇"])

    if st.button("✨ 开始创作") and topic:
        use_agent_tool("创意写作", {
            "type": writing_type,
            "topic": topic,
            "style": style,
            "length": length
        })

def translation_tool_enhanced(client, model):
    """增强版翻译工具"""
    st.subheader("🔤 智能翻译")

    source_lang = st.selectbox("源语言", ["自动检测", "中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文", "俄文"])
    target_lang = st.selectbox("目标语言", ["英文", "中文", "日文", "韩文", "法文", "德文", "西班牙文", "俄文"])

    text_to_translate = st.text_area("请输入要翻译的文本", height=150)

    if st.button("🔄 翻译") and text_to_translate:
        use_agent_tool("翻译", {
            "source_lang": source_lang,
            "target_lang": target_lang,
            "text": text_to_translate
        })

def use_agent_tool(tool_name, parameters):
    """使用Agent工具"""
    with st.spinner(f"正在使用{tool_name}工具..."):
        try:
            # 构建提示
            prompt = f"请使用{tool_name}工具处理以下请求：{parameters}"

            input_data = {
                "type": "text",
                "content": prompt
            }

            result = asyncio.run(st.session_state.agent.process_input(input_data))

            st.success(f"✅ {tool_name}完成")
            st.markdown("### 处理结果")
            st.markdown(result.get('response', '处理失败'))

            if 'processing_time' in result:
                st.caption(f"处理时间: {result['processing_time']:.2f}秒")

        except Exception as e:
            st.error(f"{tool_name}失败: {str(e)}")

# 简化版工具函数（保持原有实现）
def creative_writing_tool(client, model):
    """创意写作工具"""
    st.subheader("💭 创意写作助手")

    writing_type = st.selectbox("写作类型", ["文章", "故事", "诗歌", "广告文案", "邮件"])
    topic = st.text_input("主题或关键词")
    style = st.selectbox("写作风格", ["正式", "轻松", "幽默", "专业", "创意"])
    length = st.selectbox("长度", ["简短", "中等", "详细"])

    if st.button("✨ 开始创作") and topic:
        with st.spinner("AI正在创作..."):
            try:
                prompt = f"请写一篇{style}风格的{writing_type}，主题是：{topic}。长度要求：{length}。"

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
                st.success("✅ 创作完成")
                st.markdown("### 创作结果")
                st.markdown(result)

            except Exception as e:
                st.error(f"创作失败: {e}")

def translation_tool(client, model):
    """翻译工具"""
    st.subheader("🔤 智能翻译")

    source_lang = st.selectbox("源语言", ["自动检测", "中文", "英文", "日文", "韩文", "法文", "德文"])
    target_lang = st.selectbox("目标语言", ["英文", "中文", "日文", "韩文", "法文", "德文"])

    text_to_translate = st.text_area("请输入要翻译的文本", height=150)

    if st.button("🔄 翻译") and text_to_translate:
        with st.spinner("AI正在翻译..."):
            try:
                prompt = f"请将以下文本从{source_lang}翻译为{target_lang}：\n\n{text_to_translate}"

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的翻译助手，提供准确、自然的翻译。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )

                result = response.choices[0].message.content
                st.success("✅ 翻译完成")
                st.markdown("### 翻译结果")
                st.markdown(result)

            except Exception as e:
                st.error(f"翻译失败: {e}")

def rewriting_tool(client, model):
    """内容改写工具"""
    st.subheader("📝 内容改写")

    rewrite_style = st.selectbox("改写风格", ["更正式", "更简洁", "更详细", "更通俗", "更专业"])
    original_text = st.text_area("请输入原始文本", height=150)

    if st.button("✏️ 改写") and original_text:
        with st.spinner("AI正在改写..."):
            try:
                prompt = f"请将以下文本改写得{rewrite_style}：\n\n{original_text}"

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的文本编辑助手。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=800
                )

                result = response.choices[0].message.content
                st.success("✅ 改写完成")
                st.markdown("### 改写结果")
                st.markdown(result)

            except Exception as e:
                st.error(f"改写失败: {e}")

def math_tool(client, model):
    """数学计算工具"""
    st.subheader("🧮 数学计算助手")

    math_problem = st.text_area("请输入数学问题或计算表达式", height=100)

    if st.button("🔢 计算") and math_problem:
        with st.spinner("AI正在计算..."):
            try:
                prompt = f"请解决以下数学问题，提供详细的解题步骤：\n\n{math_problem}"

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的数学助手，擅长解决各种数学问题。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=800
                )

                result = response.choices[0].message.content
                st.success("✅ 计算完成")
                st.markdown("### 计算结果")
                st.markdown(result)

            except Exception as e:
                st.error(f"计算失败: {e}")

def data_analysis_tool(client, model):
    """数据分析工具"""
    st.subheader("📊 数据分析助手")

    data_input = st.text_area("请输入数据（支持CSV格式或描述数据）", height=150)
    analysis_type = st.selectbox("分析类型", ["基础统计", "趋势分析", "数据总结", "异常检测"])

    if st.button("📈 分析") and data_input:
        with st.spinner("AI正在分析数据..."):
            try:
                prompt = f"请对以下数据进行{analysis_type}：\n\n{data_input}"

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的数据分析师，擅长数据分析和解释。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )

                result = response.choices[0].message.content
                st.success("✅ 分析完成")
                st.markdown("### 分析结果")
                st.markdown(result)

            except Exception as e:
                st.error(f"分析失败: {e}")

# 增强版工具的其他实现
def rewriting_tool_enhanced(client, model):
    """增强版内容改写工具"""
    rewriting_tool(client, model)  # 暂时使用简化版实现

def math_tool_enhanced(client, model):
    """增强版数学计算工具"""
    math_tool(client, model)  # 暂时使用简化版实现

def data_analysis_tool_enhanced(client, model):
    """增强版数据分析工具"""
    data_analysis_tool(client, model)  # 暂时使用简化版实现

def web_search_tool_enhanced():
    """网络搜索工具"""
    st.subheader("🔍 网络搜索")
    st.info("网络搜索功能开发中...")

def code_execution_tool_enhanced():
    """代码执行工具"""
    st.subheader("💻 代码执行")
    st.info("代码执行功能开发中...")

# 主函数可以被app.py导入和调用
if __name__ == "__main__":
    main()
