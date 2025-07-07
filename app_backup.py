# -*- coding: utf-8 -*-
"""
智能多模态AI Agent - Streamlit Cloud版本
专为Streamlit Cloud环境优化，内置所有必要功能
"""
import os
import streamlit as st
from datetime import datetime
from typing import Optional, Tuple, Any
from openai import OpenAI


class APIClientManager:
    """API客户端管理器"""

    @staticmethod
    def create_openai_client() -> Optional[Tuple[OpenAI, str]]:
        """创建OpenAI客户端"""
        try:
            # 检查火山方舟API密钥
            ark_api_key = None
            if hasattr(st, 'secrets'):
                ark_api_key = st.secrets.get("ARK_API_KEY", None)
            if not ark_api_key:
                ark_api_key = os.getenv("ARK_API_KEY")

            if ark_api_key and ark_api_key not in ["your_volcano_engine_ark_api_key_here", ""]:
                # 使用火山方舟API
                base_url = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
                model = os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw")

                if hasattr(st, 'secrets'):
                    base_url = st.secrets.get("ARK_BASE_URL", base_url)
                    model = st.secrets.get("ARK_MODEL", model)

                client = OpenAI(
                    api_key=ark_api_key,
                    base_url=base_url
                )
                return client, model

            # 检查OpenAI API密钥
            openai_api_key = None
            if hasattr(st, 'secrets'):
                openai_api_key = st.secrets.get("OPENAI_API_KEY", None)
            if not openai_api_key:
                openai_api_key = os.getenv("OPENAI_API_KEY")

            if openai_api_key and openai_api_key not in ["your_openai_api_key_here", ""]:
                # 使用OpenAI API
                client = OpenAI(api_key=openai_api_key)
                model = "gpt-3.5-turbo"
                return client, model

            return None

        except Exception as e:
            st.error(f"创建API客户端失败: {e}")
            return None

    @staticmethod
    def test_api_connection(client: OpenAI, model: str) -> bool:
        """测试API连接"""
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                timeout=10
            )
            return True
        except Exception:
            return False


class StreamlitUIHelper:
    """Streamlit UI助手"""

    @staticmethod
    def setup_page_config():
        """设置页面配置"""
        st.set_page_config(
            page_title="智能AI助手",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    @staticmethod
    def show_api_config_guide():
        """显示API配置指南"""
        st.markdown("""
        ### 🔑 API密钥配置指南

        请配置以下任一API密钥：

        #### 方法1: 火山方舟API (推荐)
        1. 访问 [火山方舟控制台](https://console.volcengine.com/ark)
        2. 创建API密钥
        3. 在Streamlit Cloud的Secrets中添加：
        ```toml
        ARK_API_KEY = "your_ark_api_key_here"
        ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
        ARK_MODEL = "your_model_endpoint"
        ```

        #### 方法2: OpenAI API
        1. 访问 [OpenAI平台](https://platform.openai.com/api-keys)
        2. 创建API密钥
        3. 在Streamlit Cloud的Secrets中添加：
        ```toml
        OPENAI_API_KEY = "your_openai_api_key_here"
        ```
        """)

    @staticmethod
    def show_sidebar_info():
        """显示侧边栏信息"""
        with st.sidebar:
            st.markdown("### 🤖 智能AI助手")
            st.markdown("---")

            st.markdown("#### ✨ 功能特性")
            st.markdown("""
            - 💬 智能对话交流
            - 📁 文件内容分析
            - 🔍 文本总结分析
            - 🎯 多种处理模式
            """)

            st.markdown("#### 📊 使用统计")
            if 'chat_count' not in st.session_state:
                st.session_state.chat_count = 0
            st.metric("对话次数", st.session_state.chat_count)

            st.markdown("---")
            st.markdown("#### 💡 使用提示")
            st.markdown("""
            - 直接输入问题开始对话
            - 上传文件进行AI分析
            - 支持多种文件格式
            """)


class FileProcessor:
    """文件处理器"""

    @staticmethod
    def show_file_info(uploaded_file):
        """显示文件信息"""
        st.markdown("#### 📋 文件信息")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("文件名", uploaded_file.name)
        with col2:
            st.metric("文件大小", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("文件类型", uploaded_file.type)

    @staticmethod
    def process_text_file(content: str, client: OpenAI, model: str, action: str):
        """处理文本文件"""
        try:
            with st.spinner(f"正在{action}文件内容..."):
                if action == "总结":
                    prompt = f"请总结以下内容的主要要点：\n\n{content[:4000]}"
                else:  # 分析
                    prompt = f"请分析以下内容的结构、主题和关键信息：\n\n{content[:4000]}"

                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )

                result = response.choices[0].message.content

                st.markdown(f"#### 🎯 {action}结果")
                st.markdown(result)

        except Exception as e:
            st.error(f"处理文件时出错: {e}")


class ChatManager:
    """聊天管理器"""

    @staticmethod
    def initialize_chat():
        """初始化聊天"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "chat_count" not in st.session_state:
            st.session_state.chat_count = 0

    @staticmethod
    def show_welcome_message():
        """显示欢迎消息"""
        if not st.session_state.messages:
            welcome_msg = """
            👋 您好！我是智能AI助手，很高兴为您服务！

            我可以帮您：
            - 💬 回答各种问题
            - 📝 文本分析和总结
            - 🔍 信息查询和解释
            - 💡 创意和建议

            请随时向我提问！
            """
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

    @staticmethod
    def display_chat_history():
        """显示聊天历史"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    @staticmethod
    def process_user_input(client: OpenAI, model: str, prompt: str):
        """处理用户输入"""
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成AI回复
        with st.chat_message("assistant"):
            try:
                with st.spinner("思考中..."):
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages[-10:]  # 保留最近10条消息
                        ],
                        max_tokens=1500,
                        temperature=0.7,
                        stream=True
                    )

                    # 流式显示回复
                    response_placeholder = st.empty()
                    full_response = ""

                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            response_placeholder.markdown(full_response + "▌")

                    response_placeholder.markdown(full_response)

                # 添加AI回复到历史
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.chat_count += 1

            except Exception as e:
                st.error(f"生成回复时出错: {e}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"抱歉，处理您的请求时出现了错误: {e}"
                })

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
