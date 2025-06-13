# 🔧 故障排除指南

## ❌ AI客户端初始化失败

### 问题描述
启动应用时出现"AI客户端初始化失败"错误。

### 🔍 诊断步骤

#### 1. 运行诊断工具
```bash
python fix_client_init.py
```

#### 2. 检查API密钥配置
```bash
# 检查.env文件是否存在
ls -la .env

# 查看API密钥配置
cat .env | grep API_KEY
```

#### 3. 测试API连接
```bash
python test_ark_api.py
```

### 🛠️ 解决方案

#### 方案1：配置API密钥
1. **检查.env文件**
   ```bash
   # 如果不存在，从示例创建
   cp .env.example .env
   ```

2. **编辑.env文件**
   ```bash
   # 设置Volcano Engine ARK API密钥
   ARK_API_KEY=your_real_api_key_here
   ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
   ARK_MODEL=ep-20250506230532-w7rdw
   ```

3. **验证配置**
   ```bash
   python test_ark_api.py
   ```

#### 方案2：使用快速启动版
如果配置复杂，可以使用简化版本：
```bash
python quick_start.py
```

#### 方案3：检查网络连接
```bash
# 测试网络连接
curl -I https://ark.cn-beijing.volces.com/api/v3

# 如果在企业网络，可能需要配置代理
export https_proxy=your_proxy_server:port
```

#### 方案4：安装依赖
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 🚀 启动选项

#### 选项1：快速启动版（推荐）
```bash
python quick_start.py
```
- ✅ 最简单的启动方式
- ✅ 避免复杂的依赖问题
- ✅ 基础对话功能

#### 选项2：简化版
```bash
python simple_streamlit_app.py
```
- ✅ 基础功能
- ✅ 较少依赖

#### 选项3：集成版
```bash
python integrated_streamlit_app.py
```
- ✅ 完整功能
- ⚠️ 需要所有依赖

#### 选项4：增强版
```bash
python enhanced_app.py
```
- ✅ 最完整功能
- ⚠️ 需要所有依赖和配置

#### 选项5：Docker部署
```bash
docker-compose up -d
```
- ✅ 环境隔离
- ✅ 一键部署

## 🔧 常见问题解决

### 问题1：模块导入错误
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案：**
```bash
pip install -r requirements.txt
```

### 问题2：端口占用
```
Port 8501 is already in use
```

**解决方案：**
```bash
# 方法1：使用不同端口
streamlit run quick_start.py --server.port 8502

# 方法2：杀死占用进程
lsof -ti:8501 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8501   # Windows
```

### 问题3：权限错误
```
Permission denied
```

**解决方案：**
```bash
# 检查文件权限
chmod +x *.py

# 创建必要目录
mkdir -p logs cache data chroma_data
```

### 问题4：API配额不足
```
Rate limit exceeded
```

**解决方案：**
- 检查API配额
- 等待配额重置
- 升级API套餐

### 问题5：网络连接问题
```
Connection timeout
```

**解决方案：**
```bash
# 检查网络
ping ark.cn-beijing.volces.com

# 配置代理（如果需要）
export https_proxy=proxy_server:port
```

## 📋 完整诊断清单

### ✅ 环境检查
- [ ] Python 3.9+ 已安装
- [ ] pip 已安装
- [ ] 网络连接正常

### ✅ 文件检查
- [ ] .env 文件存在
- [ ] API密钥已正确设置
- [ ] requirements.txt 存在

### ✅ 依赖检查
- [ ] streamlit 已安装
- [ ] openai 已安装
- [ ] python-dotenv 已安装
- [ ] requests 已安装

### ✅ API检查
- [ ] API密钥有效
- [ ] API配额充足
- [ ] 网络可达API端点

### ✅ 权限检查
- [ ] 文件读写权限
- [ ] 端口使用权限
- [ ] 目录创建权限

## 🆘 获取帮助

### 1. 运行诊断工具
```bash
python fix_client_init.py
```

### 2. 查看日志
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/*.log
```

### 3. 检查系统状态
```bash
# 访问健康检查端点（如果应用已启动）
curl http://localhost:8080/health
```

### 4. 重置环境
```bash
# 清理缓存
rm -rf cache/* chroma_data/* logs/*

# 重新创建配置
rm .env
python fix_client_init.py
```

## 🎯 快速解决方案

如果遇到任何问题，最快的解决方案是：

1. **运行诊断工具**
   ```bash
   python fix_client_init.py
   ```

2. **使用快速启动版**
   ```bash
   python quick_start.py
   ```

3. **如果仍有问题，使用Docker**
   ```bash
   docker-compose up -d
   ```

这样可以避免大部分环境和配置问题，快速体验AI Agent的功能。
