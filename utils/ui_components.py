"""
UI组件库
提供增强的用户界面组件和加载动画
"""
import streamlit as st
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

class LoadingAnimations:
    """加载动画组件"""
    
    @staticmethod
    def spinner_with_text(text: str, spinner_type: str = "default"):
        """带文本的加载动画"""
        spinner_types = {
            "default": "🔄",
            "thinking": "🤔",
            "processing": "⚙️",
            "analyzing": "🔍",
            "generating": "✨",
            "uploading": "📤",
            "downloading": "📥",
            "searching": "🔎"
        }
        
        icon = spinner_types.get(spinner_type, "🔄")
        return st.spinner(f"{icon} {text}")
    
    @staticmethod
    def progress_with_steps(steps: List[str], current_step: int = 0):
        """步骤式进度指示器"""
        cols = st.columns(len(steps))
        
        for i, (col, step) in enumerate(zip(cols, steps)):
            with col:
                if i < current_step:
                    st.success(f"✅ {step}")
                elif i == current_step:
                    st.info(f"🔄 {step}")
                else:
                    st.write(f"⏳ {step}")

class StatusIndicators:
    """状态指示器"""
    
    @staticmethod
    def system_status(status: str, details: Dict[str, Any] = None):
        """系统状态指示器"""
        status_colors = {
            "online": "🟢",
            "offline": "🔴", 
            "warning": "🟡",
            "maintenance": "🟠",
            "error": "❌"
        }
        
        icon = status_colors.get(status.lower(), "⚪")
        
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.markdown(f"### {icon}")
            
            with col2:
                st.markdown(f"**系统状态**: {status.upper()}")
                if details:
                    with st.expander("详细信息"):
                        st.json(details)

class InteractiveComponents:
    """交互式组件"""
    
    @staticmethod
    def enhanced_file_uploader(
        label: str,
        accepted_types: List[str],
        max_size_mb: int = 10,
        help_text: str = None
    ):
        """增强的文件上传器"""
        
        # 文件类型说明
        type_descriptions = {
            'txt': '文本文件',
            'md': 'Markdown文档', 
            'pdf': 'PDF文档',
            'docx': 'Word文档',
            'xlsx': 'Excel表格',
            'csv': 'CSV数据',
            'json': 'JSON数据',
            'jpg': 'JPEG图片',
            'png': 'PNG图片',
            'gif': 'GIF图片'
        }
        
        # 显示支持的文件类型
        supported_types = [type_descriptions.get(t, t.upper()) for t in accepted_types]
        
        st.markdown(f"**{label}**")
        st.caption(f"支持格式: {', '.join(supported_types)} | 最大大小: {max_size_mb}MB")
        
        if help_text:
            st.info(help_text)
        
        uploaded_file = st.file_uploader(
            label="",
            type=accepted_types,
            help=f"拖拽文件到此处或点击选择文件"
        )
        
        if uploaded_file:
            # 文件信息显示
            file_size_mb = uploaded_file.size / (1024 * 1024)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("文件名", uploaded_file.name)
            
            with col2:
                st.metric("文件大小", f"{file_size_mb:.2f} MB")
            
            with col3:
                st.metric("文件类型", uploaded_file.type or "未知")
            
            # 大小检查
            if file_size_mb > max_size_mb:
                st.error(f"文件大小超过限制 ({max_size_mb}MB)")
                return None
            else:
                st.success("✅ 文件上传成功")
        
        return uploaded_file

class MetricsDisplay:
    """指标显示组件"""
    
    @staticmethod
    def performance_dashboard(metrics: Dict[str, Any]):
        """性能仪表板"""
        st.subheader("📊 性能指标")
        
        # 主要指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="响应时间",
                value=f"{metrics.get('response_time', 0):.2f}s",
                delta=f"{metrics.get('response_time_delta', 0):+.2f}s"
            )
        
        with col2:
            st.metric(
                label="缓存命中率", 
                value=f"{metrics.get('cache_hit_rate', 0):.1f}%",
                delta=f"{metrics.get('cache_hit_rate_delta', 0):+.1f}%"
            )
        
        with col3:
            st.metric(
                label="处理请求数",
                value=metrics.get('total_requests', 0),
                delta=metrics.get('requests_delta', 0)
            )
        
        with col4:
            st.metric(
                label="错误率",
                value=f"{metrics.get('error_rate', 0):.1f}%",
                delta=f"{metrics.get('error_rate_delta', 0):+.1f}%"
            )

class NotificationSystem:
    """通知系统"""
    
    @staticmethod
    def show_toast(message: str, type: str = "info", duration: int = 3):
        """显示Toast通知"""
        toast_types = {
            "success": st.success,
            "error": st.error,
            "warning": st.warning,
            "info": st.info
        }
        
        toast_func = toast_types.get(type, st.info)
        
        # 创建通知容器
        notification = toast_func(message)
        
        return notification

# 全局组件实例
loading = LoadingAnimations()
status = StatusIndicators()
interactive = InteractiveComponents()
metrics = MetricsDisplay()
notifications = NotificationSystem()

def get_ui_components():
    """获取UI组件"""
    return {
        'loading': loading,
        'status': status,
        'interactive': interactive,
        'metrics': metrics,
        'notifications': notifications
    }
