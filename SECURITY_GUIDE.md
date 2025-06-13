# 🔒 安全配置指南

## 🎯 概述

本指南帮助您安全地配置和使用智能多模态AI Agent，保护您的API密钥和其他敏感信息。

## 🔑 API密钥安全

### ❌ 不要做的事情

```bash
# 错误：直接在代码中硬编码API密钥
client = OpenAI(api_key="ak-1234567890abcdef")

# 错误：在公开文件中暴露API密钥
ARK_API_KEY=ak-1234567890abcdef

# 错误：在Git提交中包含真实API密钥
git add .env
git commit -m "添加配置文件"  # 危险！
```

### ✅ 正确的做法

#### 1. 使用环境变量
```bash
# 在 .env 文件中（不要提交到Git）
ARK_API_KEY=your_real_api_key_here

# 在代码中使用
import os
api_key = os.getenv("ARK_API_KEY")
```

#### 2. 使用配置模板
```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env 文件，替换为真实API密钥
# 确保 .env 在 .gitignore 中
```

#### 3. Streamlit Cloud配置
```toml
# 在 Streamlit Cloud Secrets 中配置
ARK_API_KEY = "your_real_api_key_here"
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
ARK_MODEL = "ep-20250506230532-w7rdw"
```

## 🛡️ 隐私保护工具

### 自动检测敏感信息
```bash
# 运行隐私保护工具
python privacy_protection.py
```

这个工具会：
- 🔍 扫描项目中的敏感信息
- 🛡️ 创建安全版本的文件
- 📝 更新.gitignore规则
- 📊 生成安全报告

### 手动检查
```bash
# 检查是否有敏感信息泄露
grep -r "ak-" . --exclude-dir=.git
grep -r "sk-" . --exclude-dir=.git
grep -r "API_KEY.*=" . --exclude-dir=.git
```

## 📁 文件安全

### .gitignore 配置
确保以下文件不被提交：

```gitignore
# 环境变量文件
.env
.env.local
.env.production
secrets.toml

# API密钥文件
**/api_keys.txt
**/secrets.txt
*.key
*.pem

# 配置文件
config/production.py
config/secrets.py

# 缓存和日志（可能包含敏感信息）
logs/
cache/
*.log

# Streamlit secrets
.streamlit/secrets.toml
```

### 文件权限
```bash
# 设置敏感文件权限（仅所有者可读写）
chmod 600 .env
chmod 600 config/secrets.py

# 设置目录权限
chmod 700 config/
chmod 700 logs/
```

## 🌐 部署安全

### 本地开发
```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑配置文件
nano .env  # 添加真实API密钥

# 3. 验证.gitignore
git status  # 确保.env不在待提交列表中

# 4. 启动应用
python enhanced_app.py
```

### Streamlit Cloud部署
```bash
# 1. 确保代码中没有硬编码的API密钥
python privacy_protection.py

# 2. 在Streamlit Cloud中配置Secrets
# Settings → Secrets → 添加配置

# 3. 部署应用
git push origin main
```

### Docker部署
```bash
# 1. 使用环境变量
docker run -e ARK_API_KEY=your_key your_app

# 2. 或使用.env文件
docker run --env-file .env your_app

# 3. 使用Docker secrets（生产环境）
docker service create --secret api_key your_app
```

## 🔐 API密钥管理

### 获取API密钥
1. **火山方舟API**
   - 访问：https://console.volcengine.com/ark
   - 创建应用并获取API密钥
   - 格式：`ak-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

2. **OpenAI API**
   - 访问：https://platform.openai.com/api-keys
   - 创建新的API密钥
   - 格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 密钥安全原则
- 🔒 **最小权限**：只授予必要的权限
- 🔄 **定期轮换**：定期更换API密钥
- 📊 **监控使用**：监控API使用情况
- 🚫 **立即撤销**：发现泄露立即撤销

### 密钥存储
```bash
# 推荐：使用密钥管理服务
# AWS Secrets Manager
# Azure Key Vault
# Google Secret Manager

# 本地开发：使用环境变量
export ARK_API_KEY="your_key_here"

# 生产环境：使用配置管理
# Kubernetes Secrets
# Docker Secrets
# HashiCorp Vault
```

## 🚨 安全检查清单

### 开发阶段
- [ ] API密钥存储在环境变量中
- [ ] .env文件在.gitignore中
- [ ] 代码中没有硬编码的密钥
- [ ] 运行隐私保护工具检查

### 部署前
- [ ] 检查所有配置文件
- [ ] 验证.gitignore规则
- [ ] 扫描敏感信息泄露
- [ ] 测试环境变量加载

### 部署后
- [ ] 验证API密钥正确加载
- [ ] 检查日志中是否有敏感信息
- [ ] 监控API使用情况
- [ ] 设置告警机制

## 🆘 安全事件响应

### 如果API密钥泄露
1. **立即行动**
   ```bash
   # 1. 立即撤销泄露的API密钥
   # 2. 生成新的API密钥
   # 3. 更新所有配置
   # 4. 重新部署应用
   ```

2. **检查影响**
   ```bash
   # 检查API使用日志
   # 查看是否有异常调用
   # 评估潜在损失
   ```

3. **预防措施**
   ```bash
   # 加强访问控制
   # 增加监控告警
   # 定期安全审计
   ```

### 紧急联系
- 火山方舟支持：https://console.volcengine.com/workorder
- OpenAI支持：https://help.openai.com/

## 🔧 工具和资源

### 安全工具
- **隐私保护工具**：`python privacy_protection.py`
- **Git secrets**：检测Git提交中的密钥
- **TruffleHog**：扫描Git历史中的密钥
- **GitLeaks**：检测密钥泄露

### 最佳实践
- 使用密钥管理服务
- 实施最小权限原则
- 定期安全审计
- 员工安全培训

---

**记住：安全是一个持续的过程，不是一次性的任务！** 🔒
