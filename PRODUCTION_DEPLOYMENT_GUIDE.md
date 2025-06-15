# 智能多模态AI Agent系统 - 生产部署指南

## 🚀 生产环境部署架构

### 整体架构设计
```
┌─────────────────────────────────────────────────────────────┐
│                    负载均衡层 (Load Balancer)                │
│                    Nginx / HAProxy                          │
├─────────────────────────────────────────────────────────────┤
│                    应用服务层 (Application Layer)            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ AI Agent    │  │ AI Agent    │  │ AI Agent    │          │
│  │ Instance 1  │  │ Instance 2  │  │ Instance 3  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    缓存层 (Cache Layer)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Redis       │  │ Memcached   │  │ Local Cache │          │
│  │ Cluster     │  │ Pool        │  │ (In-Memory) │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    数据存储层 (Data Layer)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ ChromaDB    │  │ PostgreSQL  │  │ MinIO       │          │
│  │ (Vector DB) │  │ (Metadata)  │  │ (File Store)│          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    监控层 (Monitoring Layer)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Prometheus  │  │ Grafana     │  │ ELK Stack   │          │
│  │ (Metrics)   │  │ (Dashboard) │  │ (Logs)      │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 🐳 Docker生产配置

### 优化的Dockerfile
```dockerfile
# 多阶段构建优化
FROM python:3.11-slim as builder

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 生产镜像
FROM python:3.11-slim

# 创建非root用户
RUN groupadd -r aiagent && useradd -r -g aiagent aiagent

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY --chown=aiagent:aiagent . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python health_check.py

# 切换到非root用户
USER aiagent

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8501", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "app:app"]
```

### 生产级docker-compose.yml
```yaml
version: '3.8'

services:
  # AI Agent应用
  ai-agent:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    image: ai-agent:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - ENV=production
      - LOG_LEVEL=INFO
      - REDIS_URL=redis://redis:6379
      - POSTGRES_URL=postgresql://user:pass@postgres:5432/aiagent
      - CHROMA_HOST=chromadb
    depends_on:
      - redis
      - postgres
      - chromadb
    networks:
      - ai-agent-network
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads

  # 负载均衡器
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-agent
    networks:
      - ai-agent-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - ai-agent-network
    deploy:
      resources:
        limits:
          memory: 1G

  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: aiagent
      POSTGRES_USER: aiagent
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - ai-agent-network
    deploy:
      resources:
        limits:
          memory: 2G

  # ChromaDB向量数据库
  chromadb:
    image: chromadb/chroma:latest
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
      - CHROMA_SERVER_HTTP_PORT=8000
    volumes:
      - chroma_data:/chroma/chroma
    networks:
      - ai-agent-network
    deploy:
      resources:
        limits:
          memory: 2G

  # Prometheus监控
  prometheus:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - ai-agent-network

  # Grafana仪表板
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    networks:
      - ai-agent-network

volumes:
  redis_data:
  postgres_data:
  chroma_data:
  prometheus_data:
  grafana_data:

networks:
  ai-agent-network:
    driver: bridge
```

## ⚙️ 系统配置优化

### Nginx配置
```nginx
# nginx.conf
events {
    worker_connections 1024;
    use epoll;
}

http {
    upstream ai_agent_backend {
        least_conn;
        server ai-agent:8501 max_fails=3 fail_timeout=30s;
        server ai-agent:8502 max_fails=3 fail_timeout=30s;
        server ai-agent:8503 max_fails=3 fail_timeout=30s;
    }

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=1r/s;

    server {
        listen 80;
        server_name your-domain.com;

        # 安全头部
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000";

        # API接口
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://ai_agent_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_timeout 60s;
        }

        # 文件上传
        location /upload/ {
            limit_req zone=upload burst=5 nodelay;
            client_max_body_size 100M;
            proxy_pass http://ai_agent_backend;
            proxy_request_buffering off;
        }

        # 静态文件
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            root /var/www;
        }
    }
}
```

### 环境变量配置
```bash
# .env.production
ENV=production
DEBUG=false

# API配置
ARK_API_KEY=your_production_api_key
OPENAI_MODEL=ep-20250506230532-w7rdw
OPENAI_TEMPERATURE=0.7

# 数据库配置
POSTGRES_URL=postgresql://aiagent:${POSTGRES_PASSWORD}@postgres:5432/aiagent
REDIS_URL=redis://redis:6379/0
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# 安全配置
SECRET_KEY=your_super_secret_key_here
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here

# 性能配置
MAX_WORKERS=4
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=60
CACHE_TTL=3600

# 监控配置
PROMETHEUS_ENABLED=true
METRICS_PORT=9090
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn_here
```

## 📊 监控和告警

### Prometheus配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'ai-agent'
    static_configs:
      - targets: ['ai-agent:9090']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 告警规则
```yaml
# alert_rules.yml
groups:
  - name: ai_agent_alerts
    rules:
      - alert: HighResponseTime
        expr: avg(http_request_duration_seconds) > 5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "AI Agent响应时间过高"
          description: "平均响应时间超过5秒"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "AI Agent错误率过高"
          description: "5分钟内错误率超过5%"

      - alert: MemoryUsageHigh
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高"
          description: "内存使用率超过80%"
```

## 🔒 安全配置

### SSL/TLS配置
```bash
# 生成SSL证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/private.key \
    -out ssl/certificate.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=YourOrg/CN=your-domain.com"
```

### 防火墙配置
```bash
# UFW防火墙规则
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 备份策略
```bash
#!/bin/bash
# backup.sh - 自动备份脚本

# 数据库备份
docker exec postgres pg_dump -U aiagent aiagent > backup/db_$(date +%Y%m%d_%H%M%S).sql

# 向量数据库备份
docker exec chromadb tar -czf - /chroma/chroma > backup/chroma_$(date +%Y%m%d_%H%M%S).tar.gz

# 上传文件备份
tar -czf backup/uploads_$(date +%Y%m%d_%H%M%S).tar.gz uploads/

# 清理旧备份（保留7天）
find backup/ -name "*.sql" -mtime +7 -delete
find backup/ -name "*.tar.gz" -mtime +7 -delete
```

## 🚀 部署流程

### 1. 环境准备
```bash
# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装Docker Compose
pip install docker-compose

# 创建项目目录
mkdir -p /opt/ai-agent
cd /opt/ai-agent
```

### 2. 配置部署
```bash
# 克隆代码
git clone https://github.com/luoxiao6645/ai-agent.git .

# 配置环境变量
cp .env.example .env.production
# 编辑 .env.production 文件

# 构建镜像
docker-compose -f docker-compose.prod.yml build
```

### 3. 启动服务
```bash
# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f ai-agent
```

### 4. 健康检查
```bash
# 检查应用健康状态
curl http://localhost/health

# 检查监控指标
curl http://localhost:9090/metrics
```

## 📈 性能调优

### 系统级优化
```bash
# 内核参数优化
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
echo 'fs.file-max = 100000' >> /etc/sysctl.conf
sysctl -p
```

### 应用级优化
```python
# gunicorn配置
bind = "0.0.0.0:8501"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 60
keepalive = 5
```

---

*本部署指南基于生产环境最佳实践，建议根据实际需求调整配置参数。*
