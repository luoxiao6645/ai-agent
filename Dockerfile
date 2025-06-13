# 多模态AI Agent - 优化版Docker镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs /app/cache /app/data && \
    chown -R appuser:appuser /app

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置权限
RUN chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health/quick || exit 1

# 暴露端口
EXPOSE 8501 8080

# 启动脚本
CMD ["python", "-c", "\
import threading; \
from health_check import start_health_server_thread; \
import streamlit.web.cli as stcli; \
import sys; \
start_health_server_thread(); \
sys.argv = ['streamlit', 'run', 'enhanced_streamlit_app.py', '--server.port=8501', '--server.address=0.0.0.0']; \
sys.exit(stcli.main()) \
"]
