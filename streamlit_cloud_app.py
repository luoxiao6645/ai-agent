"""
Streamlit Cloud专用应用

专为Streamlit Cloud环境优化的AI Agent应用
"""

import streamlit as st
import os
import sys
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="智能多模态AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_streamlit_secrets():
    """检查Streamlit Cloud的secrets配置"""
    try:
        # 尝试从Streamlit secrets获取API密钥
        if hasattr(st, 'secrets'):
            ark_api_key = st.secrets.get("ARK_API_KEY", None)
            if ark_api_key:
                os.environ["ARK_API_KEY"] = ark_api_key
                return True
        return False
    except Exception:
        return False

def init_streamlit_client():
    """初始化Streamlit Cloud客户端"""
    try:
        from openai import OpenAI
        
        # 首先检查Streamlit secrets
        if check_streamlit_secrets():
            st.success("✅ 从Streamlit Secrets加载API密钥")
        
        # 获取API密钥
        ark_api_key = os.getenv("ARK_API_KEY")
        
        if not ark_api_key:
            st.error("❌ 未找到API密钥")
            st.markdown("""
            ### 🔧 配置说明
            
            在Streamlit Cloud中，您需要在应用设置中添加Secrets：
            
            1. 进入应用管理页面
            2. 点击 "Settings" → "Secrets"
            3. 添加以下配置：
            
            ```toml
            ARK_API_KEY = "your_volcano_engine_ark_api_key_here"
            ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
            ARK_MODEL = "ep-20250506230532-w7rdw"
            ```
            
            4. 保存并重新部署应用
            """)
            return None
        
        # 创建客户端
        client = OpenAI(
            base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            api_key=ark_api_key,
        )
        
        # 测试连接
        try:
            response = client.chat.completions.create(
                model=os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw"),
                messages=[
                    {"role": "system", "content": "你是人工智能助手"},
                    {"role": "user", "content": "你好"}
                ],
                max_tokens=10
            )
            st.success("✅ AI客户端连接成功")
            return client
        except Exception as e:
            st.error(f"❌ API连接测试失败: {e}")
            st.info("请检查API密钥是否正确，以及网络连接是否正常")
            return None
            
    except ImportError:
        st.error("❌ openai库未安装")
        st.info("请在requirements.txt中添加: openai>=1.0.0")
        return None
    except Exception as e:
        st.error(f"❌ 客户端初始化失败: {e}")
        return None

def streamlit_chat_interface(client):
    """Streamlit Cloud优化的对话界面"""
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
                    # 构建消息历史（保留最近10条）
                    messages = [
                        {"role": "system", "content": "你是一个智能助手，请用中文回答问题。"}
                    ]
                    
                    # 添加对话历史
                    recent_messages = st.session_state.messages[-10:]
                    for msg in recent_messages:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                    
                    response = client.chat.completions.create(
                        model=os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw"),
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    
                    assistant_response = response.choices[0].message.content
                    st.markdown(assistant_response)
                    
                    # 添加助手消息
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    
                except Exception as e:
                    error_msg = f"抱歉，处理您的请求时出现错误: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def streamlit_file_interface():
    """文件处理界面"""
    st.header("📁 文件处理")
    
    uploaded_file = st.file_uploader(
        "选择文件", 
        type=['txt', 'pdf', 'docx', 'jpg', 'jpeg', 'png']
    )
    
    if uploaded_file is not None:
        st.info(f"📄 文件名: {uploaded_file.name}")
        st.info(f"📊 文件大小: {uploaded_file.size} bytes")
        
        if uploaded_file.type.startswith('text/'):
            # 处理文本文件
            try:
                content = uploaded_file.read().decode('utf-8')
                st.text_area("文件内容预览", content[:1000] + "..." if len(content) > 1000 else content, height=200)
                
                if st.button("📝 分析文件内容"):
                    st.info("💡 文件分析功能正在开发中，敬请期待！")
            except Exception as e:
                st.error(f"文件读取失败: {e}")
        
        elif uploaded_file.type.startswith('image/'):
            # 处理图像文件
            st.image(uploaded_file, caption="上传的图像", use_column_width=True)
            
            if st.button("🔍 分析图像"):
                st.info("💡 图像分析功能正在开发中，敬请期待！")
        
        else:
            st.info("📋 文件已上传，更多处理功能正在开发中")

def streamlit_tools_interface():
    """工具箱界面"""
    st.header("🧮 AI工具箱")
    
    tool_col1, tool_col2 = st.columns(2)
    
    with tool_col1:
        st.subheader("📝 文本工具")
        
        if st.button("✍️ 创意写作"):
            st.info("💡 创意写作工具正在开发中")
        
        if st.button("📊 文本分析"):
            st.info("💡 文本分析工具正在开发中")
        
        if st.button("🌐 翻译助手"):
            st.info("💡 翻译工具正在开发中")
    
    with tool_col2:
        st.subheader("🔧 实用工具")
        
        if st.button("🧮 智能计算"):
            st.info("💡 计算工具正在开发中")
        
        if st.button("📅 日程助手"):
            st.info("💡 日程工具正在开发中")
        
        if st.button("🔍 搜索助手"):
            st.info("💡 搜索工具正在开发中")

def main():
    """主函数"""
    st.title("🤖 智能多模态AI Agent")
    st.markdown("### 基于火山方舟API的智能助手")
    
    # 初始化客户端
    client = init_streamlit_client()
    
    if not client:
        st.stop()
    
    # 侧边栏
    with st.sidebar:
        st.header("🎛️ 控制面板")
        
        # 系统状态
        st.subheader("📊 系统状态")
        st.success("✅ AI客户端已连接")
        st.info(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
        
        # 模型配置
        st.subheader("⚙️ 模型配置")
        model = st.selectbox(
            "模型",
            [os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw")],
            disabled=True
        )
        
        # 清除对话
        if st.button("🗑️ 清除对话"):
            st.session_state.messages = []
            st.rerun()
        
        # 使用说明
        st.markdown("---")
        st.subheader("📖 使用说明")
        st.markdown("""
        1. 💬 **智能对话**: 与AI助手自由对话
        2. 📁 **文件处理**: 上传并处理各种文件
        3. 🧮 **工具箱**: 使用各种AI工具
        
        **提示**: 这是Streamlit Cloud版本，功能持续更新中！
        """)
    
    # 主界面标签页
    tab1, tab2, tab3 = st.tabs(["💬 智能对话", "📁 文件处理", "🧮 工具箱"])
    
    with tab1:
        streamlit_chat_interface(client)
    
    with tab2:
        streamlit_file_interface()
    
    with tab3:
        streamlit_tools_interface()
    
    # 底部信息
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("版本", "Streamlit Cloud v1.0")
    
    with col2:
        st.metric("状态", "运行中", delta="正常")
    
    with col3:
        st.metric("环境", "云端部署")

if __name__ == "__main__":
    main()
