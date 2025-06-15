# -*- coding: utf-8 -*-
"""
智能多模态AI Agent - Streamlit Cloud版本
专为Streamlit Cloud环境优化，使用重构后的公共工具模块
"""
import streamlit as st
import sys

from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入公共工具模块
from utils.common import (

    APIClientManager,
    StreamlitUIHelper,
    FileProcessor,
    ChatManager
)

# 页面配置
StreamlitUIHelper.setup_page_config()


def init_streamlit_client():
    """初始化Streamlit Cloud客户端"""
    # 使用重构后的API客户端管理器
    result = APIClientManager.create_openai_client()

    if not result:
        st.error("❌ 未找到API密钥")
        StreamlitUIHelper.show_api_config_guide()
        return None

    client, model = result

    # 测试连接
    if APIClientManager.test_api_connection(client, model):
        import os

        api_type = "火山方舟API" if os.getenv("ARK_API_KEY") else "OpenAI API"
        st.success(f"✅ {api_type}连接成功")
        return client, model
    else:
        api_type = "火山方舟API" if os.getenv("ARK_API_KEY") else "OpenAI API"
        st.error(f"❌ {api_type}连接测试失败")
        st.info("请检查API密钥是否正确，以及网络连接是否正常")
        return None, None


def streamlit_chat_interface(client, model):
    """优化的对话界面 - 使用重构后的聊天管理器"""
    # 初始化对话
    ChatManager.initialize_chat()

    # 显示欢迎信息
    ChatManager.show_welcome_message()

    # 显示对话历史
    ChatManager.display_chat_history()

    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        ChatManager.process_user_input(client, model, prompt)


def streamlit_file_interface(client, model):
    """优化的文件处理界面 - 使用重构后的文件处理器"""
    st.markdown("""
    ### 📁 文件处理

    上传文件让AI帮您分析和处理：
    - 📄 **文本文件**: 总结、分析、翻译
    - 🖼️ **图片文件**: 描述、分析图片内容
    """)

    uploaded_file = st.file_uploader(
        "选择要处理的文件",
        type=['txt', 'md', 'pdf', 'docx', 'jpg', 'jpeg', 'png', 'gif'],
        help="支持文本、图片、PDF、Word等格式"
    )

    if uploaded_file is not None:
        # 显示文件信息
        FileProcessor.show_file_info(uploaded_file)

        # 处理文本文件
        if uploaded_file.type.startswith('text/') or uploaded_file.name.endswith('.md'):
            try:
                content = uploaded_file.read().decode('utf-8')

                # 文件预览
                st.markdown("#### 👀 文件预览")
                if len(content) > 1000:
                    st.text_area("内容预览", content[:1000] + "...", height=150, disabled=True)
                    st.caption(f"显示前1000字符，总长度: {len(content)}字符")
                else:
                    st.text_area("文件内容", content, height=150, disabled=True)

                # 处理选项
                st.markdown("#### 🔧 AI处理选项")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("📝 总结内容", use_container_width=True):
                        FileProcessor.process_text_file(content, client, model, "总结")

                with col2:
                    if st.button("🔍 分析内容", use_container_width=True):
                        FileProcessor.process_text_file(content, client, model, "分析")

            except Exception as e:
                st.error(f"无法读取文件: {e}")

        # 处理图片文件
        elif uploaded_file.type.startswith('image/'):
            st.markdown("#### 👀 图片预览")
            st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

            st.markdown("#### 🔧 AI处理选项")
            if st.button("🖼️ 描述图片", use_container_width=True):
                st.info("🖼️ 图片分析功能需要支持视觉的AI模型，当前版本暂不支持。")
                st.markdown("**替代方案**: 您可以描述图片内容，我来帮您分析！")

        # 其他文件类型
        else:
            st.info("📋 文件已上传，当前版本主要支持文本文件的AI分析")


def main():
    """主函数"""
    st.title("🤖 智能多模态AI Agent")

    # 初始化客户端
    result = init_streamlit_client()

    if not result or result[0] is None:
        st.stop()

    client, model = result

    # 使用重构后的侧边栏
    StreamlitUIHelper.show_sidebar_info()

    # 主界面标签页
    tab1, tab2 = st.tabs(["💬 智能对话", "📁 文件处理"])

    with tab1:
        streamlit_chat_interface(client, model)

    with tab2:
        streamlit_file_interface(client, model)

if __name__ == "__main__":
    main()
