"""
简化版Streamlit应用 - 用于测试
"""
import streamlit as st
import os
import sys
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="智能多模态AI Agent - 测试版",
    page_icon="🤖",
    layout="wide"
)

def main():
    """主界面"""
    st.title("🤖 智能多模态AI Agent系统")
    st.markdown("---")
    
    # 系统状态检查
    st.header("📊 系统状态")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Python版本", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    with col2:
        st.metric("当前时间", datetime.now().strftime("%H:%M:%S"))
    
    with col3:
        env_status = "✅ 已配置" if os.path.exists(".env") else "❌ 未配置"
        st.metric("环境配置", env_status)
    
    # 依赖检查
    st.header("📦 依赖检查")
    
    dependencies = {
        "streamlit": "Streamlit Web框架",
        "openai": "OpenAI API客户端", 
        "langchain": "LangChain AI框架",
        "chromadb": "ChromaDB向量数据库"
    }
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            st.success(f"✅ {package} - {description}")
        except ImportError:
            st.error(f"❌ {package} - {description} (未安装)")
    
    # 简单功能测试
    st.header("🧪 功能测试")
    
    # 文本输入测试
    user_input = st.text_area("输入测试文本:", value="你好，这是一个测试")
    
    if st.button("🚀 处理文本"):
        if user_input:
            st.success("✅ 文本处理成功!")
            st.info(f"输入内容: {user_input}")
            st.info(f"字符数: {len(user_input)}")
            st.info(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning("请输入一些文本")
    
    # 文件上传测试
    st.header("📁 文件上传测试")
    
    uploaded_file = st.file_uploader("选择文件", type=['txt', 'md', 'json'])
    
    if uploaded_file is not None:
        st.success(f"✅ 文件上传成功: {uploaded_file.name}")
        st.info(f"文件大小: {uploaded_file.size} 字节")
        
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode('utf-8')
            st.text_area("文件内容:", value=content[:500], height=200)
    
    # 配置信息
    st.header("⚙️ 配置信息")
    
    if os.path.exists(".env"):
        st.success("✅ 环境配置文件存在")
        
        try:
            with open(".env", "r", encoding="utf-8") as f:
                env_content = f.read()
                
            if "OPENAI_API_KEY" in env_content:
                if "your_openai_api_key_here" in env_content:
                    st.warning("⚠️ 请设置真实的OpenAI API密钥")
                else:
                    st.success("✅ OpenAI API密钥已配置")
            else:
                st.error("❌ 缺少OpenAI API密钥配置")
                
        except Exception as e:
            st.error(f"❌ 读取配置文件失败: {e}")
    else:
        st.error("❌ 环境配置文件不存在")
        st.info("请复制 .env.example 为 .env 并配置")
    
    # 下一步指导
    st.header("📋 下一步操作")
    
    st.markdown("""
    ### 如果这个测试页面正常显示，说明基础环境OK！
    
    **接下来的步骤:**
    
    1. **安装缺失的依赖包**:
       ```bash
       pip install streamlit openai langchain chromadb langchain-openai langchain-community
       ```
    
    2. **配置环境变量**:
       - 复制 `.env.example` 为 `.env`
       - 在 `.env` 文件中填入您的 OpenAI API 密钥
    
    3. **运行完整应用**:
       ```bash
       python run_local.py
       ```
    
    4. **或者使用Docker** (需要先启动Docker Desktop):
       ```bash
       start.bat  # Windows
       ./start.sh # Linux/Mac
       ```
    """)
    
    # 侧边栏信息
    with st.sidebar:
        st.header("🛠️ 系统信息")
        st.info(f"Python: {sys.version}")
        st.info(f"工作目录: {os.getcwd()}")
        st.info(f"Streamlit版本: {st.__version__}")
        
        if st.button("🔄 刷新页面"):
            st.rerun()

if __name__ == "__main__":
    main()
