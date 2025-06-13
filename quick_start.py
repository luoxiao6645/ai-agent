#!/usr/bin/env python3
"""
快速启动脚本 - 避免复杂的初始化问题

提供最简单的方式启动AI Agent应用
"""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 页面配置
st.set_page_config(
    page_title="智能多模态AI Agent - 快速启动版",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载环境变量
load_dotenv()

def check_and_setup_env():
    """检查并设置环境"""
    env_file = Path(".env")
    
    if not env_file.exists():
        st.error("❌ .env文件不存在")
        st.info("请先运行: python fix_client_init.py")
        return False
    
    # 检查API密钥
    ark_api_key = os.getenv("ARK_API_KEY")
    if not ark_api_key or ark_api_key in ["your_volcano_engine_ark_api_key_here", "your_ark_api_key_here"]:
        st.error("❌ ARK_API_KEY未正确配置")
        st.info("请编辑.env文件，设置您的API密钥")
        return False
    
    return True

@st.cache_resource
def init_simple_client():
    """初始化简单客户端"""
    try:
        from openai import OpenAI
        
        ark_api_key = os.getenv("ARK_API_KEY")
        ark_base_url = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        
        if not ark_api_key:
            st.error("❌ API密钥未设置")
            return None
        
        client = OpenAI(
            base_url=ark_base_url,
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
            return None
            
    except ImportError:
        st.error("❌ openai库未安装，请运行: pip install openai")
        return None
    except Exception as e:
        st.error(f"❌ 客户端初始化失败: {e}")
        return None

def simple_chat_interface(client):
    """简单对话界面"""
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
                    response = client.chat.completions.create(
                        model=os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw"),
                        messages=[
                            {"role": "system", "content": "你是一个智能助手，请用中文回答问题。"},
                            *[{"role": m["role"], "content": m["content"]} 
                              for m in st.session_state.messages[-10:]]  # 保留最近10条消息
                        ],
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

def simple_file_interface():
    """简单文件处理界面"""
    st.header("📁 文件处理")
    
    uploaded_file = st.file_uploader(
        "选择文件", 
        type=['txt', 'pdf', 'docx', 'jpg', 'jpeg', 'png']
    )
    
    if uploaded_file is not None:
        st.info(f"文件名: {uploaded_file.name}")
        st.info(f"文件大小: {uploaded_file.size} bytes")
        
        if uploaded_file.type.startswith('text/'):
            # 处理文本文件
            content = uploaded_file.read().decode('utf-8')
            st.text_area("文件内容", content, height=200)
            
            if st.button("分析文件内容"):
                st.info("文件分析功能需要完整版本，当前为快速启动版")
        
        elif uploaded_file.type.startswith('image/'):
            # 处理图像文件
            st.image(uploaded_file, caption="上传的图像")
            
            if st.button("分析图像"):
                st.info("图像分析功能需要完整版本，当前为快速启动版")
        
        else:
            st.info("文件已上传，详细处理功能需要完整版本")

def system_status():
    """系统状态"""
    st.header("📊 系统状态")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("版本", "快速启动版 v1.0")
    
    with col2:
        st.metric("状态", "运行中", delta="正常")
    
    with col3:
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        st.metric("当前时间", current_time)
    
    # 环境信息
    st.subheader("🔧 环境信息")
    env_info = {
        "ARK_BASE_URL": os.getenv("ARK_BASE_URL", "未设置"),
        "ARK_MODEL": os.getenv("ARK_MODEL", "未设置"),
        "Python版本": sys.version.split()[0],
        "Streamlit版本": st.__version__
    }
    
    for key, value in env_info.items():
        st.text(f"{key}: {value}")

def main():
    """主函数"""
    st.title("🤖 智能多模态AI Agent - 快速启动版")
    
    # 检查环境
    if not check_and_setup_env():
        st.stop()
    
    # 初始化客户端
    client = init_simple_client()
    if not client:
        st.error("❌ 无法初始化AI客户端")
        st.info("请检查API配置或运行诊断工具: python fix_client_init.py")
        st.stop()
    
    # 侧边栏
    with st.sidebar:
        st.header("🎛️ 控制面板")
        
        # 版本信息
        st.info("当前版本: 快速启动版")
        st.success("✅ AI客户端已连接")
        
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
        
        # 升级提示
        st.markdown("---")
        st.subheader("🚀 升级到完整版")
        st.info("要使用完整功能，请运行:")
        st.code("python enhanced_app.py")
    
    # 主界面标签页
    tab1, tab2, tab3 = st.tabs(["💬 智能对话", "📁 文件处理", "📊 系统状态"])
    
    with tab1:
        simple_chat_interface(client)
    
    with tab2:
        simple_file_interface()
    
    with tab3:
        system_status()
    
    # 底部信息
    st.markdown("---")
    st.markdown(
        "💡 **提示**: 这是快速启动版，功能有限。要体验完整功能，请运行完整版应用。"
    )

if __name__ == "__main__":
    main()
