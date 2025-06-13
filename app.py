# -*- coding: utf-8 -*-
"""
Multimodal AI Agent - Complete System
Main Entry File
"""
import streamlit as st
import os
import sys
import asyncio
from datetime import datetime

# Set page configuration (只在主入口设置一次)
st.set_page_config(
    page_title="智能多模态AI Agent系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加当前目录到Python路径
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入集成系统
try:
    # 尝试导入集成版本（自动适配完整/简化模式）
    from integrated_streamlit_app import main as integrated_main
    # 运行集成系统
    integrated_main()
except ImportError as e:
    st.warning(f"集成系统导入失败，尝试其他版本: {e}")
    try:
        # 尝试完整系统
        from ui.streamlit_app import main as full_main
        full_main()
    except ImportError:
        try:
            # 回退到简化版本
            from simple_streamlit_app import main as simple_main
            simple_main()
        except Exception as e:
            st.error(f"所有版本加载失败: {e}")
            show_fallback_interface()
except Exception as e:
    st.error(f"系统初始化失败: {e}")
    show_fallback_interface()

def show_fallback_interface():
    """显示备用界面"""
    st.title("🤖 智能多模态AI Agent")
    st.markdown("""
    ### 欢迎使用智能多模态AI Agent！

    这是一个基于火山方舟API的智能助手，支持：
    - 💬 智能对话
    - 📄 文档处理
    - 🎨 创意写作
    - 🔧 AI工具箱

    **当前状态**: 系统正在维护中...
    """)

    st.info("请检查配置文件和依赖包是否正确安装")

    if st.button("🔄 重新加载应用"):
        st.rerun()
