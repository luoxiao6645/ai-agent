# 智能多模态AI Agent - 增强版部署指南

## 🚀 快速部署

### 方式一：Docker Compose部署（推荐）

1. **克隆项目**
```bash
git clone https://github.com/luoxiao6645/ai-agent.git
cd ai-agent
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，设置必要的API密钥
```

3. **启动服务**
```bash
# 启动主服务
docker-compose up -d

# 启动包含监控的完整服务
docker-compose --profile monitoring up -d
```

4. **访问应用**
- 🌐 主应用: http://localhost:8501
- 🏥 健康检查: http://localhost:8080/health
- 📊 系统指标: http://localhost:8080/metrics
- 📈 监控面板: http://localhost:9090 (如果启用监控)

### 方式二：增强版本地部署

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置API密钥和优化参数
```

3. **启动增强版应用**
```bash
# 使用增强版启动器（推荐）
python enhanced_app.py

# 或直接启动Streamlit应用
streamlit run enhanced_streamlit_app.py
```

### 方式三：传统部署

```bash
# 启动基础版本
python app.py

# 或启动安全加固版本
python secure_streamlit_app.py
```

## ⚙️ 环境变量配置

### 🔑 API配置（必需）
```bash
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# Volcano Engine ARK API配置（可选）
ARK_API_KEY=your_ark_api_key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=ep-20250506230532-w7rdw
```

### 🚀 性能优化配置
```bash
# 优化级别: minimal, balanced, aggressive
OPTIMIZATION_LEVEL=balanced

# 功能开关
ENABLE_CACHING=true
ENABLE_CONNECTION_POOLING=true
ENABLE_ASYNC_PROCESSING=true
ENABLE_PERFORMANCE_MONITORING=true

# 缓存配置
CACHE_MAX_SIZE=1000
CACHE_DEFAULT_TTL=3600
CACHE_EVICTION_POLICY=lru
CACHE_ENABLE_PERSISTENCE=true

# 连接池配置
HTTP_POOL_SIZE=10
HTTP_MAX_RETRIES=3
HTTP_TIMEOUT=30

# 异步处理配置
ASYNC_MAX_WORKERS=4
ASYNC_QUEUE_SIZE=100

# 监控配置
MONITOR_INTERVAL=60
MONITOR_HISTORY_SIZE=1000
```

### 🛡️ 安全配置
```bash
# 安全功能开关
ENABLE_SECURITY=true
SESSION_TIMEOUT=3600

# 服务端口配置
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0
HEALTH_CHECK_PORT=8080
```

## 📊 监控和维护

### 健康检查端点
| 端点 | 描述 | 用途 |
|------|------|------|
| `GET /health` | 完整健康检查 | 系统监控 |
| `GET /health/quick` | 快速健康检查 | 负载均衡器检查 |
| `GET /ready` | 就绪检查 | Kubernetes就绪探针 |
| `GET /metrics` | 系统指标 | 监控数据收集 |
| `GET /status` | 服务状态 | 服务发现 |

### 性能监控
```bash
# 查看系统健康状态
curl http://localhost:8080/health

# 获取性能指标
curl http://localhost:8080/metrics

# 检查服务状态
curl http://localhost:8080/status
```

### 日志管理
```bash
# 日志文件位置
./logs/
├── app.log              # 应用日志
├── security.log         # 安全日志
├── performance.log      # 性能日志
├── user_action.log      # 用户操作日志
├── system_error.log     # 系统错误日志
└── api_call.log         # API调用日志

# 查看实时日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/*.log
```

## 🔧 性能优化

### 缓存优化
```bash
# 查看缓存统计
curl http://localhost:8080/metrics | jq '.metrics.performance.cache'

# 调整缓存配置
export CACHE_MAX_SIZE=5000
export CACHE_DEFAULT_TTL=7200
export OPTIMIZATION_LEVEL=aggressive
```

### 连接池优化
```bash
# 监控连接池状态
curl http://localhost:8080/metrics | jq '.metrics.performance.connection_pool'

# 调整连接池大小
export HTTP_POOL_SIZE=20
export HTTP_TIMEOUT=60
```

### 异步处理优化
```bash
# 查看异步处理统计
curl http://localhost:8080/metrics | jq '.metrics.performance.async_processor'

# 调整工作线程数
export ASYNC_MAX_WORKERS=8
export ASYNC_QUEUE_SIZE=500
```

## 🐛 故障排除

### 常见问题及解决方案

#### 1. 端口冲突
```bash
# 问题：端口已被占用
# 解决：修改端口配置
export STREAMLIT_PORT=8502
export HEALTH_CHECK_PORT=8081

# 或修改docker-compose.yml
ports:
  - "8502:8501"
  - "8081:8080"
```

#### 2. API密钥错误
```bash
# 问题：API调用失败
# 解决：检查API配置
echo $OPENAI_API_KEY
echo $ARK_API_KEY

# 测试API连接
python test_ark_api.py
```

#### 3. 内存不足
```bash
# 问题：系统内存不足
# 解决：调整Docker资源限制
# 在docker-compose.yml中：
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
```

#### 4. 缓存问题
```bash
# 清理缓存
rm -rf cache/*
rm -rf chroma_data/*

# 重启服务
docker-compose restart
```

#### 5. 性能问题
```bash
# 运行性能基准测试
python benchmark_test.py

# 查看性能报告
ls logs/benchmark_report_*.json
```

### 调试模式
```bash
# 启用调试模式
export DEBUG=true
export LOG_LEVEL=DEBUG

# 查看详细日志
python enhanced_app.py
```

## 📈 生产环境部署

### 资源要求
- **最小配置**: 2GB RAM, 1 CPU核心
- **推荐配置**: 4GB RAM, 2 CPU核心
- **高负载配置**: 8GB RAM, 4 CPU核心

### 安全建议
1. **使用HTTPS**: 配置SSL证书
2. **防火墙设置**: 只开放必要端口
3. **定期更新**: 保持依赖包最新
4. **备份策略**: 定期备份数据和配置

### 扩展部署
```bash
# 多实例部署
docker-compose up --scale ai-agent=3

# 负载均衡配置
# 使用nginx或traefik进行负载均衡
```

## 🔄 更新和维护

### 更新应用
```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d
```

### 数据备份
```bash
# 备份数据
tar -czf backup_$(date +%Y%m%d).tar.gz logs/ cache/ data/

# 恢复数据
tar -xzf backup_20240101.tar.gz
```

### 监控告警
```bash
# 设置监控告警
# 可以集成Prometheus + Grafana + AlertManager
# 或使用云服务监控
```
