"""
Streamlit Web界面
"""
import streamlit as st
import asyncio
import logging
import sys
import os

from datetime import datetime

from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multimodal_agent.core.agent import MultiModalAgent

from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 页面配置已在app.py中设置，这里不再重复设置

# 初始化会话状态
@st.cache_resource


def initialize_agent():
    """初始化Agent（缓存资源）"""
    try:
        return MultiModalAgent()
    except Exception as e:
        st.error(f"Agent初始化失败: {e}")
        return None

# 初始化会话状态
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'initialized' not in st.session_state:
    st.session_state.initialized = False


def main():
    """主界面"""
    st.title("🤖 智能多模态AI Agent系统")
    st.markdown("---")

    # 初始化Agent
    agent = initialize_agent()
    if not agent:
        st.error("系统初始化失败，请检查配置文件和依赖包")
        st.info("正在尝试使用简化版本...")
        return

    st.session_state.agent = agent
    st.session_state.initialized = True

    # 侧边栏
    with st.sidebar:
        st.header("🛠️ 系统控制")

        # Agent状态
        if st.button("📊 查看Agent状态"):
            status = st.session_state.agent.get_status()
            st.json(status)

        # 清除记忆
        if st.button("🗑️ 清除记忆"):
            asyncio.run(st.session_state.agent.clear_memory())
            st.session_state.conversation_history = []
            st.success("记忆已清除")

        # 工具信息
        st.subheader("🔧 可用工具")
        tools = st.session_state.agent.tool_manager.get_tool_names()
        for tool in tools:
            st.text(f"• {tool}")

    # 主界面标签页
    tab1, tab2, tab3, tab4 = st.tabs(["💬 对话", "📁 文件处理", "🖼️ 图像处理", "📊 数据分析"])

    with tab1:
        chat_interface()

    with tab2:
        file_interface()

    with tab3:
        image_interface()

    with tab4:
        data_interface()


def chat_interface():
    """对话界面"""
    st.header("💬 智能对话")

    # 显示对话历史
    if st.session_state.conversation_history:
        st.subheader("对话历史")
        for i, conv in enumerate(st.session_state.conversation_history):
            with st.expander(f"对话 {i+1} - {conv['timestamp']}", expanded=(i == len(st.session_state.conversation_history)-1)):
                st.markdown(f"**用户:** {conv['user_input']}")
                st.markdown(f"**Agent:** {conv['agent_response']}")
                if 'processing_time' in conv:
                    st.caption(f"处理时间: {conv['processing_time']:.2f}秒")

    # 输入区域
    st.subheader("新对话")
    user_input = st.text_area("请输入您的问题或指令:", height=100, key="chat_input")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 发送", key="send_chat"):
            if user_input.strip():
                process_chat_input(user_input)

    with col2:
        if st.button("🔍 搜索记忆", key="search_memory"):
            if user_input.strip():
                search_memory(user_input)


def file_interface():
    """文件处理界面"""
    st.header("📁 文件处理")

    # 文件上传
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['txt', 'pdf', 'docx', 'xlsx', 'csv', 'json', 'md'],
        key="file_upload"
    )

    if uploaded_file is not None:
        # 保存上传的文件
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"文件已上传: {uploaded_file.name}")

        # 处理文件
        if st.button("📖 解析文件", key="parse_file"):
            with st.spinner("正在解析文件..."):
                input_data = {
                    "type": "file",
                    "content": file_path
                }
                result = asyncio.run(st.session_state.agent.process_input(input_data))
                st.text_area("解析结果:", value=result['response'], height=300)

        # 清理临时文件
        if os.path.exists(file_path):
            os.remove(file_path)


def image_interface():
    """图像处理界面"""
    st.header("🖼️ 图像处理")

    # 图像上传
    uploaded_image = st.file_uploader(
        "选择图像",
        type=['jpg', 'jpeg', 'png', 'gif', 'bmp'],
        key="image_upload"
    )

    if uploaded_image is not None:
        # 显示图像
        st.image(uploaded_image, caption="上传的图像", use_column_width=True)

        # 保存图像
        image_path = f"temp_{uploaded_image.name}"
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())

        # 处理图像
        if st.button("🔍 分析图像", key="analyze_image"):
            with st.spinner("正在分析图像..."):
                input_data = {
                    "type": "image",
                    "content": image_path
                }
                result = asyncio.run(st.session_state.agent.process_input(input_data))
                st.text_area("分析结果:", value=result['response'], height=200)

        # 清理临时文件
        if os.path.exists(image_path):
            os.remove(image_path)


def data_interface():
    """数据分析界面"""
    st.header("📊 数据分析")

    # 数据输入方式选择
    data_input_method = st.radio(
        "选择数据输入方式:",
        ["手动输入", "文件上传"],
        key="data_input_method"
    )

    if data_input_method == "手动输入":
        data_text = st.text_area("输入数据 (JSON或CSV格式):", height=150, key="data_input")

        if st.button("📈 分析数据", key="analyze_data_text"):
            if data_text.strip():
                analyze_data(data_text)

    else:
        data_file = st.file_uploader(
            "上传数据文件",
            type=['csv', 'json', 'xlsx'],
            key="data_file_upload"
        )

        if data_file is not None:
            if st.button("📈 分析数据", key="analyze_data_file"):
                # 读取文件内容
                file_content = data_file.read().decode('utf-8')
                analyze_data(file_content)


def process_chat_input(user_input: str):
    """处理聊天输入"""
    with st.spinner("Agent正在思考..."):
        try:
            input_data = {
                "type": "text",
                "content": user_input
            }

            result = asyncio.run(st.session_state.agent.process_input(input_data))

            # 添加到对话历史
            conversation = {
                "user_input": user_input,
                "agent_response": result['response'],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "processing_time": result.get('processing_time', 0)
            }

            st.session_state.conversation_history.append(conversation)

            # 显示结果
            st.success("处理完成!")
            st.rerun()

        except Exception as e:
            st.error(f"处理失败: {str(e)}")


def search_memory(query: str):
    """搜索记忆"""
    with st.spinner("搜索记忆中..."):
        try:
            results = asyncio.run(st.session_state.agent.search_memory(query))

            if results:
                st.subheader("🔍 记忆搜索结果")
                for i, result in enumerate(results):
                    with st.expander(f"结果 {i+1}"):
                        st.text(result.page_content)
                        if result.metadata:
                            st.json(result.metadata)
            else:
                st.info("未找到相关记忆")

        except Exception as e:
            st.error(f"搜索失败: {str(e)}")


def analyze_data(data: str):
    """分析数据"""
    with st.spinner("分析数据中..."):
        try:
            # 使用数据分析工具
            tool = st.session_state.agent.tool_manager.get_tool("data_analyzer")
            if tool:
                result = asyncio.run(tool._arun(data, "basic"))
                st.text_area("分析结果:", value=result, height=300)
            else:
                st.error("数据分析工具不可用")

        except Exception as e:
            st.error(f"数据分析失败: {str(e)}")

if __name__ == "__main__":
    main()
