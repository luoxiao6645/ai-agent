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

# 导入系统（优先使用优化版本）
try:
    # 首先尝试优化版本（第二阶段）
    from optimized_streamlit_app import main as optimized_main
    optimized_main()
except ImportError as e:
    st.info(f"优化版本不可用，使用集成版本: {e}")
    try:
        # 尝试集成版本（第一阶段）
        from integrated_streamlit_app import main as integrated_main
        integrated_main()
    except ImportError as e2:
        st.warning(f"集成版本导入失败，使用简化版本: {e2}")
        try:
            # 回退到简化版本
            from simple_streamlit_app import main as simple_main
            simple_main()
        except Exception as e3:
            st.error(f"所有版本加载失败: {e3}")
            show_fallback_interface()
except Exception as e:
    st.error(f"系统运行失败: {e}")
    show_fallback_interface()
