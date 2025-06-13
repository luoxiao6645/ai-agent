"""
智能多模态AI Agent - 网站部署版本
主入口文件
"""
import streamlit as st
import os
import sys

# 设置页面配置
st.set_page_config(
    page_title="智能多模态AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加当前目录到Python路径
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入主应用
try:
    # 尝试导入simple_streamlit_app的主要功能
    exec(open('simple_streamlit_app.py').read())
except Exception as e:
    st.error(f"应用加载失败: {e}")
    st.info("请检查应用配置和依赖包是否正确安装")
    
    # 显示基本信息
    st.title("🤖 智能多模态AI Agent")
    st.markdown("""
    ### 欢迎使用智能多模态AI Agent！
    
    这是一个基于火山方舟API的智能助手，支持：
    - 💬 智能对话
    - 📄 文档处理
    - 🎨 创意写作
    - 🔧 AI工具箱
    
    **部署状态**: 正在初始化...
    """)
    
    if st.button("重新加载应用"):
        st.experimental_rerun()
