# 🚀 高级版部署指南 - 第五阶段

## 📋 概述

第五阶段引入了监控集成、API优化、日志聚合等高级功能，提供了完整的生产级监控和API生态系统。

## 🆕 第五阶段新功能

### 📊 监控集成
- **Prometheus指标收集**: 系统性能、AI请求、缓存等指标
- **Grafana仪表板**: 可视化监控面板
- **自定义指标**: 业务相关的监控指标

### 🔗 API优化
- **GraphQL API**: 灵活的查询接口
- **移动端API**: 为移动应用优化的REST API
- **API文档**: 自动生成的交互式文档

### 📝 日志聚合
- **结构化日志**: JSON格式的日志输出
- **ELK Stack支持**: Elasticsearch + Kibana日志分析
- **日志分类**: 应用、安全、性能、API日志分离

## 🚀 部署方式

### 方式一：完整监控栈部署

```bash
# 克隆项目
git clone https://github.com/luoxiao6645/ai-agent.git
cd ai-agent

# 配置环境变量
cp .env.example .env
# 编辑.env文件设置API密钥

# 启动完整监控栈
docker-compose --profile monitoring --profile api --profile elk up -d
```

### 方式二：高级版本地部署

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
python secure_setup.py

# 启动高级版应用
python advanced_app.py
```

### 方式三：选择性服务部署

```bash
# 只启动监控服务
docker-compose --profile monitoring up -d

# 只启动API服务
docker-compose --profile api up -d

# 只启动日志分析
docker-compose --profile elk up -d
```

## 🌐 服务端点

### 主要服务
- **🌐 主应用**: http://localhost:8501
- **🏥 健康检查**: http://localhost:8080/health
- **📊 系统指标**: http://localhost:8080/metrics

### 监控服务
- **📈 Prometheus**: http://localhost:9090
- **📊 Grafana**: http://localhost:3000 (admin/admin)
- **📊 Prometheus指标**: http://localhost:8090/metrics

### API服务
- **🔗 GraphQL API**: http://localhost:8000/graphql
- **📱 移动端API**: http://localhost:8001/docs
- **📖 API文档**: http://localhost:8001/redoc

### 日志分析
- **🔍 Elasticsearch**: http://localhost:9200
- **📊 Kibana**: http://localhost:5601

## ⚙️ 环境变量配置

### 基础配置
```bash
# API密钥
ARK_API_KEY=your_volcano_engine_ark_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 服务端口
STREAMLIT_PORT=8501
HEALTH_CHECK_PORT=8080
PROMETHEUS_PORT=8090
GRAPHQL_PORT=8000
MOBILE_API_PORT=8001
```

### 监控配置
```bash
# Prometheus配置
PROMETHEUS_SCRAPE_INTERVAL=15s
PROMETHEUS_RETENTION_TIME=15d

# Grafana配置
GF_SECURITY_ADMIN_PASSWORD=your_secure_password
GF_USERS_ALLOW_SIGN_UP=false
```

### 日志配置
```bash
# 日志级别
LOG_LEVEL=INFO
STRUCTURED_LOGGING=true

# ELK配置
ELASTICSEARCH_HEAP_SIZE=512m
KIBANA_ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

## 📊 监控指标

### 系统指标
- `ai_agent_system_cpu_percent`: CPU使用率
- `ai_agent_system_memory_percent`: 内存使用率
- `ai_agent_system_memory_bytes`: 内存使用量

### AI请求指标
- `ai_agent_requests_total`: AI请求总数
- `ai_agent_request_duration_seconds`: 请求响应时间
- `ai_agent_tokens_total`: Token使用量

### 缓存指标
- `ai_agent_cache_hits_total`: 缓存命中数
- `ai_agent_cache_misses_total`: 缓存未命中数
- `ai_agent_cache_size`: 当前缓存大小

### 连接池指标
- `ai_agent_connection_pool_active`: 活跃连接数
- `ai_agent_connection_pool_idle`: 空闲连接数

## 🔗 GraphQL API使用

### 查询示例
```graphql
# 获取系统状态
query {
  systemStatus {
    cpuPercent
    memoryPercent
    status
    timestamp
  }
}

# 获取缓存统计
query {
  cacheStats {
    hits
    misses
    hitRatePercent
    cacheSize
  }
}
```

### 变更示例
```graphql
# 发送聊天消息
mutation {
  chat(input: {
    message: "你好，AI助手！"
    model: "default"
    temperature: 0.7
  }) {
    content
    model
    tokensUsed
    responseTime
    cached
  }
}
```

## 📱 移动端API使用

### 聊天接口
```bash
curl -X POST "http://localhost:8001/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，AI助手！",
    "model": "default",
    "temperature": 0.7
  }'
```

### 文件上传
```bash
curl -X POST "http://localhost:8001/api/v1/upload" \
  -F "file=@example.txt"
```

### 获取系统状态
```bash
curl "http://localhost:8001/api/v1/status"
```

## 📝 日志分析

### 日志格式
```json
{
  "@timestamp": "2024-01-01T12:00:00.000Z",
  "level": "INFO",
  "message": "AI request completed",
  "service": {
    "name": "ai-agent",
    "version": "1.0.0"
  },
  "ai": {
    "model": "default",
    "tokens": 150,
    "success": true
  },
  "performance": {
    "duration_ms": 1500
  }
}
```

### Kibana查询示例
```
# 查找错误日志
level:ERROR

# 查找AI请求
event_type:ai_request

# 查找慢请求
performance.duration_ms:>5000

# 查找特定用户的操作
user.id:"user123"
```

## 🔧 性能优化

### Prometheus优化
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ai-agent'
    scrape_interval: 10s
    static_configs:
      - targets: ['ai-agent:8090']
```

### Grafana仪表板
- 导入预配置的仪表板: `monitoring/grafana-dashboard.json`
- 自定义告警规则
- 设置通知渠道

### 日志优化
```bash
# 日志轮转配置
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10
LOG_ROTATION_INTERVAL=daily
```

## 🐛 故障排除

### 监控服务问题
```bash
# 检查Prometheus状态
curl http://localhost:9090/-/healthy

# 检查Grafana状态
curl http://localhost:3000/api/health

# 查看Prometheus配置
curl http://localhost:9090/api/v1/status/config
```

### API服务问题
```bash
# 检查GraphQL服务
curl http://localhost:8000/health

# 检查移动端API
curl http://localhost:8001/api/v1/health

# 查看API文档
open http://localhost:8001/docs
```

### 日志问题
```bash
# 检查Elasticsearch状态
curl http://localhost:9200/_cluster/health

# 检查Kibana状态
curl http://localhost:5601/api/status

# 查看日志文件
tail -f logs/*.jsonl
```

## 📈 扩展部署

### 负载均衡
```yaml
# nginx.conf
upstream ai_agent {
    server ai-agent-1:8501;
    server ai-agent-2:8501;
    server ai-agent-3:8501;
}

server {
    listen 80;
    location / {
        proxy_pass http://ai_agent;
    }
}
```

### 高可用部署
```bash
# 多实例部署
docker-compose up --scale ai-agent=3

# 数据库集群
# Redis集群用于会话存储
# Elasticsearch集群用于日志存储
```

## 🔒 安全配置

### API安全
```bash
# 启用API认证
API_AUTH_ENABLED=true
API_JWT_SECRET=your_jwt_secret

# 限制API访问
API_RATE_LIMIT=100/minute
API_CORS_ORIGINS=https://yourdomain.com
```

### 监控安全
```bash
# Grafana安全配置
GF_SECURITY_ADMIN_PASSWORD=strong_password
GF_AUTH_ANONYMOUS_ENABLED=false

# Prometheus安全
PROMETHEUS_WEB_ENABLE_ADMIN_API=false
```

---

**第五阶段为AI Agent系统提供了完整的生产级监控、API和日志分析能力！** 🚀
