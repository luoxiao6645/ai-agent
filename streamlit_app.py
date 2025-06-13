#!/usr/bin/env python3
"""
Streamlit Cloud专用应用
简化版智能多模态AI Agent - 只包含核心功能
"""

import os
import streamlit as st
from datetime import datetime
from openai import OpenAI

# 页面配置
st.set_page_config(
    page_title="智能AI助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_api_keys():
    """检查并设置API密钥"""
    try:
        # 从Streamlit secrets获取API密钥
        if hasattr(st, 'secrets'):
            # 检查ARK API密钥
            ark_api_key = st.secrets.get("ARK_API_KEY", None)
            if ark_api_key and ark_api_key not in ["your_volcano_engine_ark_api_key_here", ""]:
                os.environ["ARK_API_KEY"] = ark_api_key
                if "ARK_BASE_URL" in st.secrets:
                    os.environ["ARK_BASE_URL"] = st.secrets["ARK_BASE_URL"]
                if "ARK_MODEL" in st.secrets:
                    os.environ["ARK_MODEL"] = st.secrets["ARK_MODEL"]
                return "ark"
            
            # 检查OpenAI API密钥
            openai_api_key = st.secrets.get("OPENAI_API_KEY", None)
            if openai_api_key and openai_api_key not in ["your_openai_api_key_here", ""]:
                os.environ["OPENAI_API_KEY"] = openai_api_key
                return "openai"
        
        return None
    except Exception:
        return None

def init_client():
    """初始化AI客户端"""
    api_type = check_api_keys()
    
    if not api_type:
        st.error("❌ 未找到API密钥")
        st.markdown("""
        ### 🔧 配置说明
        
        请在Streamlit Cloud中配置Secrets：
        
        1. 点击应用右侧的 "⚙️" 按钮
        2. 选择 "Settings" → "Secrets"
        3. 添加以下配置：
        
        ```toml
        ARK_API_KEY = "your_api_key_here"
        ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
        ARK_MODEL = "ep-20250506230532-w7rdw"
        ```
        
        4. 保存并重新部署应用
        """)
        return None, None, None
    
    try:
        if api_type == "ark":
            client = OpenAI(
                base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
                api_key=os.getenv("ARK_API_KEY"),
            )
            model = os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw")
            api_name = "火山方舟API"
        else:
            client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
            )
            model = "gpt-3.5-turbo"
            api_name = "OpenAI API"
        
        # 测试连接
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=10
        )
        
        return client, model, api_name
        
    except Exception as e:
        st.error(f"❌ API连接失败: {e}")
        return None, None, None

def chat_interface(client, model):
    """智能对话界面"""
    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 欢迎信息
    if not st.session_state.messages:
        st.markdown("""
        ### 👋 欢迎使用智能AI助手！
        
        我可以帮助您：
        - 💬 回答各种问题
        - 📝 协助写作和创作  
        - 🧮 解决计算问题
        - 🔍 分析和总结信息
        
        请在下方输入您的问题开始对话...
        """)
    
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
            with st.spinner("🤔 AI正在思考..."):
                try:
                    # 构建消息历史
                    messages = [
                        {"role": "system", "content": "你是一个智能、友好、有帮助的AI助手。请用中文回答问题，回答要准确、简洁、有条理。"}
                    ]
                    
                    # 添加最近的对话历史
                    recent_messages = st.session_state.messages[-8:]
                    for msg in recent_messages:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=1500,
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

def file_interface(client, model):
    """文件处理界面"""
    st.markdown("""
    ### 📁 文件处理
    
    上传文件让AI帮您分析和处理：
    - 📄 **文本文件**: 总结、分析、翻译
    - 🖼️ **图片文件**: 查看和描述
    """)
    
    uploaded_file = st.file_uploader(
        "选择要处理的文件",
        type=['txt', 'md', 'csv', 'jpg', 'jpeg', 'png', 'gif'],
        help="支持文本文件和图片格式"
    )
    
    if uploaded_file is not None:
        # 文件信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 文件名", uploaded_file.name)
        with col2:
            st.metric("📊 大小", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("🏷️ 类型", uploaded_file.type.split('/')[-1].upper())
        
        # 处理文本文件
        if uploaded_file.type.startswith('text/') or uploaded_file.name.endswith(('.md', '.csv')):
            try:
                content = uploaded_file.read().decode('utf-8')
                
                # 文件预览
                st.markdown("#### 👀 文件预览")
                preview_length = min(1000, len(content))
                st.text_area("内容预览", content[:preview_length], height=150, disabled=True)
                if len(content) > 1000:
                    st.caption(f"显示前1000字符，总长度: {len(content)}字符")
                
                # AI处理选项
                st.markdown("#### 🔧 AI处理选项")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📝 总结内容", use_container_width=True):
                        process_text(content, client, model, "总结")
                
                with col2:
                    if st.button("🔍 分析内容", use_container_width=True):
                        process_text(content, client, model, "分析")
                        
            except Exception as e:
                st.error(f"无法读取文件: {e}")
        
        # 处理图片文件
        elif uploaded_file.type.startswith('image/'):
            st.markdown("#### 👀 图片预览")
            st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
            st.info("🖼️ 图片分析功能需要支持视觉的AI模型，当前版本暂不支持。")
        
        else:
            st.info("📋 当前版本主要支持文本文件的AI分析")

def process_text(content, client, model, action):
    """处理文本内容"""
    try:
        if action == "总结":
            prompt = f"请总结以下文本的主要内容，要点清晰、简洁明了：\n\n{content[:2000]}"
        else:
            prompt = f"请分析以下文本的内容、结构、主题和要点：\n\n{content[:2000]}"
        
        with st.spinner(f"🤔 AI正在{action}内容..."):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"你是一个专业的文档分析助手，请对用户提供的文本进行{action}，回答要有条理、准确、有用。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            st.markdown(f"#### 📋 {action}结果")
            st.markdown(result)
            
    except Exception as e:
        st.error(f"处理内容时出错: {e}")

def main():
    """主函数"""
    st.title("🤖 智能AI助手")
    
    # 初始化客户端
    client, model, api_name = init_client()
    
    if not client:
        st.stop()
    
    # 侧边栏
    with st.sidebar:
        st.header("🎛️ 控制面板")
        
        # API状态
        st.success(f"✅ {api_name}已连接")
        st.info(f"🤖 模型: {model}")
        
        # 清除对话
        if st.button("🗑️ 清除对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # 使用说明
        st.markdown("---")
        st.markdown("**💬 智能对话**: 与AI助手自由交流")
        st.markdown("**📁 文件处理**: 上传文档进行AI分析")
        
        # 时间显示
        st.markdown("---")
        st.caption(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    
    # 主界面标签页
    tab1, tab2 = st.tabs(["💬 智能对话", "📁 文件处理"])
    
    with tab1:
        chat_interface(client, model)
    
    with tab2:
        file_interface(client, model)

if __name__ == "__main__":
    main()
