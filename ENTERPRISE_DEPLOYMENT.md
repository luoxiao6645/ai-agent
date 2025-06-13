# 🏢 企业版部署指南 - 第六阶段

## 📋 概述

第六阶段引入了微服务架构、插件系统、本地模型部署和多语言支持，提供了完整的企业级AI Agent解决方案。

## 🆕 第六阶段新功能

### 🔗 微服务架构
- **服务注册中心**: 自动服务发现和健康检查
- **负载均衡**: 智能请求分发
- **服务治理**: 服务状态监控和管理

### 🔌 插件系统
- **动态加载**: 运行时加载/卸载插件
- **第三方扩展**: 支持自定义功能插件
- **钩子机制**: 灵活的事件处理

### 🤖 本地模型部署
- **HuggingFace模型**: 支持Transformers生态
- **Ollama集成**: 本地大模型推理
- **模型管理**: 动态加载/卸载模型

### 🌍 多语言支持
- **国际化界面**: 中文、英文、日文
- **动态切换**: 运行时语言切换
- **可扩展**: 支持添加新语言

## 🚀 部署方式

### 方式一：企业版完整部署

```bash
# 克隆项目
git clone https://github.com/luoxiao6645/ai-agent.git
cd ai-agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
python secure_setup.py

# 启动企业版应用
python enterprise_app.py
```

### 方式二：Docker企业版部署

```bash
# 构建企业版镜像
docker build -t ai-agent-enterprise -f Dockerfile.enterprise .

# 启动企业版服务
docker-compose -f docker-compose.enterprise.yml up -d
```

### 方式三：Kubernetes部署

```bash
# 应用Kubernetes配置
kubectl apply -f k8s/

# 检查部署状态
kubectl get pods -n ai-agent
```

## 🌐 服务端点

### 主要服务
- **🌐 主应用**: http://localhost:8501
- **🏥 健康检查**: http://localhost:8080/health
- **📊 系统指标**: http://localhost:8080/metrics
- **🔗 服务注册**: http://localhost:8080/registry

### 微服务端点
- **📈 Prometheus**: http://localhost:9090
- **📊 Grafana**: http://localhost:3000
- **🔗 GraphQL API**: http://localhost:8000/graphql
- **📱 移动端API**: http://localhost:8001/docs

### 管理端点
- **🔌 插件管理**: http://localhost:8080/plugins
- **🤖 模型管理**: http://localhost:8080/models
- **🌍 语言设置**: http://localhost:8080/i18n

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

### 企业版配置
```bash
# 微服务配置
MICROSERVICES_ENABLED=true
SERVICE_REGISTRY_PORT=8080
HEALTH_CHECK_INTERVAL=30

# 插件配置
PLUGINS_ENABLED=true
PLUGINS_DIR=plugins
AUTO_LOAD_PLUGINS=true

# 本地模型配置
LOCAL_MODELS_ENABLED=true
MODELS_DIR=local_models
DEFAULT_DEVICE=auto

# 国际化配置
I18N_ENABLED=true
DEFAULT_LANGUAGE=zh_CN
LOCALES_DIR=i18n/locales
```

## 🔌 插件开发

### 创建插件

1. **创建插件目录**
```bash
mkdir plugins/my_plugin
cd plugins/my_plugin
```

2. **创建插件文件**
```python
# plugins/my_plugin/plugin.py
from plugins.plugin_manager import PluginInterface, PluginInfo

class MyPlugin(PluginInterface):
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="my_plugin",
            version="1.0.0",
            description="我的自定义插件",
            author="Your Name",
            dependencies=[],
            entry_point="MyPlugin",
            config_schema={}
        )
    
    def initialize(self, config):
        print("插件初始化")
        return True
    
    def execute(self, *args, **kwargs):
        return "插件执行结果"
    
    def cleanup(self):
        print("插件清理")
        return True
```

3. **加载插件**
```python
from plugins.plugin_manager import get_plugin_manager

plugin_manager = get_plugin_manager()
plugin_manager.load_plugin("my_plugin")
```

### 插件配置

```json
{
  "my_plugin": {
    "enabled": true,
    "config": {
      "api_key": "your_api_key",
      "timeout": 30
    }
  }
}
```

## 🤖 本地模型部署

### 支持的模型类型

#### HuggingFace模型
```python
from local_models.model_manager import get_model_manager

model_manager = get_model_manager()

# 注册模型
model_manager.register_model(
    name="chatglm3-6b",
    model_type="huggingface",
    model_path="THUDM/chatglm3-6b",
    tokenizer_path="THUDM/chatglm3-6b"
)

# 加载模型
model_manager.load_model("chatglm3-6b")

# 生成文本
response = model_manager.generate_text(
    "chatglm3-6b", 
    "你好，请介绍一下自己"
)
```

#### Ollama模型
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull llama2

# 注册到系统
python -c "
from local_models.model_manager import get_model_manager
manager = get_model_manager()
manager.register_model('llama2', 'ollama', 'llama2')
manager.load_model('llama2')
"
```

### 模型配置

```json
{
  "models": [
    {
      "name": "chatglm3-6b",
      "model_type": "huggingface",
      "model_path": "THUDM/chatglm3-6b",
      "device": "cuda",
      "max_length": 2048,
      "temperature": 0.7
    },
    {
      "name": "llama2",
      "model_type": "ollama", 
      "model_path": "llama2",
      "device": "cpu",
      "max_length": 4096,
      "temperature": 0.8
    }
  ]
}
```

## 🌍 多语言配置

### 添加新语言

1. **创建语言文件**
```bash
# 创建韩文翻译
touch i18n/locales/ko_KR.json
```

2. **添加翻译内容**
```json
{
  "app": {
    "title": "지능형 멀티모달 AI 에이전트",
    "welcome": "지능형 AI 어시스턴트에 오신 것을 환영합니다!"
  },
  "navigation": {
    "chat": "스마트 채팅",
    "file_processing": "파일 처리"
  }
}
```

3. **使用翻译**
```python
from i18n.translator import set_language, t

# 切换语言
set_language("ko_KR")

# 获取翻译
title = t("app.title")
```

### 动态语言切换

```python
import streamlit as st
from i18n.translator import get_available_languages, set_language, t

# 语言选择器
languages = get_available_languages()
selected = st.selectbox(
    t("settings.language"),
    options=[lang["code"] for lang in languages],
    format_func=lambda x: next(lang["native"] for lang in languages if lang["code"] == x)
)

if selected:
    set_language(selected)
    st.rerun()
```

## 📊 监控和管理

### 服务监控

```bash
# 查看服务状态
curl http://localhost:8080/health

# 查看注册的服务
curl http://localhost:8080/registry

# 查看系统指标
curl http://localhost:8080/metrics
```

### 插件管理

```bash
# 列出插件
curl http://localhost:8080/plugins

# 加载插件
curl -X POST http://localhost:8080/plugins/load -d '{"name": "weather_plugin"}'

# 卸载插件
curl -X POST http://localhost:8080/plugins/unload -d '{"name": "weather_plugin"}'
```

### 模型管理

```bash
# 列出模型
curl http://localhost:8080/models

# 加载模型
curl -X POST http://localhost:8080/models/load -d '{"name": "chatglm3-6b"}'

# 卸载模型
curl -X POST http://localhost:8080/models/unload -d '{"name": "chatglm3-6b"}'
```

## 🔧 性能优化

### 模型优化

```python
# 量化配置
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# 注册量化模型
model_manager.register_model(
    name="chatglm3-6b-4bit",
    model_type="huggingface",
    model_path="THUDM/chatglm3-6b",
    quantization_config=quantization_config
)
```

### 缓存优化

```python
# 模型缓存
TRANSFORMERS_CACHE=/path/to/cache
HF_HOME=/path/to/hf_cache

# Redis缓存
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

## 🐛 故障排除

### 常见问题

#### 模型加载失败
```bash
# 检查GPU内存
nvidia-smi

# 检查模型文件
ls -la local_models/

# 查看错误日志
tail -f logs/app.jsonl
```

#### 插件加载失败
```bash
# 检查插件目录
ls -la plugins/

# 验证插件代码
python -c "from plugins.my_plugin.plugin import MyPlugin; print('OK')"

# 查看插件日志
grep "plugin" logs/app.jsonl
```

#### 服务注册失败
```bash
# 检查端口占用
netstat -tulpn | grep 8080

# 检查服务状态
curl http://localhost:8080/health

# 重启服务注册中心
python -c "
from microservices.service_registry import get_service_registry
registry = get_service_registry()
registry.stop_health_check()
registry.start_health_check()
"
```

## 📈 扩展部署

### 集群部署

```yaml
# docker-compose.cluster.yml
version: '3.8'
services:
  ai-agent-1:
    image: ai-agent-enterprise
    ports:
      - "8501:8501"
    environment:
      - INSTANCE_ID=1
      
  ai-agent-2:
    image: ai-agent-enterprise
    ports:
      - "8502:8501"
    environment:
      - INSTANCE_ID=2
      
  nginx:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### 云原生部署

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent-enterprise
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-agent
  template:
    metadata:
      labels:
        app: ai-agent
    spec:
      containers:
      - name: ai-agent
        image: ai-agent-enterprise:latest
        ports:
        - containerPort: 8501
        env:
        - name: ARK_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-agent-secrets
              key: ark-api-key
```

---

**第六阶段为AI Agent系统提供了完整的企业级架构和扩展能力！** 🏢
