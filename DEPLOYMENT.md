# 🚀 多模态AI Agent 网站部署指南

## 部署平台选择

### 1. Streamlit Cloud（推荐 - 免费）

**优势**：
- ✅ 专为Streamlit设计
- ✅ 完全免费
- ✅ 自动部署
- ✅ 支持GitHub集成

**部署步骤**：

1. **上传到GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/你的用户名/multimodal-ai-agent.git
   git push -u origin main
   ```

2. **访问Streamlit Cloud**
   - 访问：https://share.streamlit.io/
   - 使用GitHub账号登录
   - 点击"New app"
   - 选择你的仓库
   - 主文件选择：`app.py`

3. **配置环境变量**
   在Streamlit Cloud的Secrets中添加：
   ```toml
   ARK_API_KEY = "你的API密钥"
   ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
   ARK_MODEL = "ep-20250506230532-w7rdw"
   ```

### 2. Heroku（付费）

**优势**：
- ✅ 稳定可靠
- ✅ 支持自定义域名
- ✅ 丰富的插件生态

**部署文件**：
- `Procfile`
- `runtime.txt`
- `requirements.txt`

### 3. Railway（免费额度）

**优势**：
- ✅ 简单易用
- ✅ 自动部署
- ✅ 支持多种语言

### 4. Render（免费额度）

**优势**：
- ✅ 免费SSL
- ✅ 自动部署
- ✅ 支持静态网站

## 环境变量配置

无论选择哪个平台，都需要配置以下环境变量：

```
ARK_API_KEY=你的火山方舟API密钥
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=ep-20250506230532-w7rdw
```

## 文件结构

```
multimodal-ai-agent/
├── app.py                    # 主入口文件
├── simple_streamlit_app.py   # 核心应用逻辑
├── requirements.txt          # Python依赖
├── .streamlit/
│   └── config.toml          # Streamlit配置
├── secrets.toml.example     # 密钥配置示例
├── config.py               # 应用配置
├── .env.example            # 环境变量示例
└── README.md               # 项目说明

```

## 部署检查清单

- [ ] 代码已上传到GitHub
- [ ] requirements.txt已优化
- [ ] 环境变量已配置
- [ ] API密钥已设置
- [ ] 应用可以本地运行
- [ ] 选择了部署平台
- [ ] 完成了平台配置

## 常见问题

### Q: 部署后应用无法启动？
A: 检查requirements.txt中的依赖版本，确保与部署平台兼容。

### Q: API调用失败？
A: 确认环境变量ARK_API_KEY已正确配置。

### Q: 文件上传功能不工作？
A: 检查平台的文件上传限制和临时存储配置。

## 监控和维护

- 定期检查应用状态
- 监控API使用量
- 更新依赖包版本
- 备份重要配置

## 支持

如有问题，请检查：
1. 平台日志
2. 环境变量配置
3. 依赖包版本
4. API密钥有效性
