# 智能多模态AI Agent系统

基于LangChain框架构建的智能多模态AI Agent，支持文本、图像、语音等多种输入模式，集成丰富的工具链，具备长期记忆能力和复杂任务规划能力。

## 🚀 功能特性

### 核心功能
- **多模态输入处理**: 支持文本、图像、语音、文件等多种输入
- **智能任务规划**: 使用ReAct框架进行复杂任务分解
- **丰富工具链**: 集成12+种专业工具
- **长期记忆**: 基于ChromaDB的向量存储和检索
- **Web界面**: 直观友好的Streamlit界面

### 集成工具
1. **Web搜索工具** - 实时网络信息检索
2. **文档解析工具** - PDF/Word/Excel文档处理
3. **代码执行工具** - Python/JavaScript/Bash代码执行
4. **数据分析工具** - 数据可视化和统计分析
5. **图像处理工具** - 图像编辑、生成、分析
6. **音频处理工具** - 语音合成和识别
7. **翻译工具** - 多语言翻译服务
8. **计算工具** - 数学计算和公式解析
9. **文件管理工具** - 文件上传、下载、管理
10. **API调用工具** - 第三方服务集成
11. **邮件工具** - 邮件发送和管理
12. **日历工具** - 日程管理和提醒

## 🛠️ 技术栈

- **后端框架**: Python 3.9+
- **AI框架**: LangChain
- **AI服务**: OpenAI API (GPT-4, DALL-E, Whisper)
- **前端界面**: Streamlit
- **向量数据库**: ChromaDB
- **容器化**: Docker & Docker Compose

## 📦 快速开始

### 环境要求
- Docker & Docker Compose
- OpenAI API密钥

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd multimodal-ai-agent
```

2. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入您的OpenAI API密钥
# OPENAI_API_KEY=your_openai_api_key_here
```

3. **启动系统**

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
start.bat
```

4. **访问系统**
- Web界面: http://localhost:8501
- ChromaDB管理: http://localhost:8000

## 🏗️ 项目结构

```
multimodal-ai-agent/
├── multimodal_agent/          # 核心模块
│   ├── core/                  # 核心组件
│   │   ├── agent.py          # 主Agent类
│   │   ├── memory.py         # 记忆管理
│   │   ├── planner.py        # 任务规划器
│   │   └── executor.py       # 任务执行器
│   ├── tools/                # 工具链
│   │   ├── web_search.py     # Web搜索
│   │   ├── document.py       # 文档处理
│   │   ├── code_exec.py      # 代码执行
│   │   └── ...               # 其他工具
│   └── multimodal/           # 多模态处理
│       ├── text_processor.py # 文本处理
│       ├── image_processor.py# 图像处理
│       └── ...               # 其他处理器
├── ui/                       # 用户界面
│   └── streamlit_app.py      # Streamlit应用
├── config.py                 # 配置管理
├── requirements.txt          # Python依赖
├── Dockerfile               # Docker配置
├── docker-compose.yml       # Docker Compose配置
└── README.md               # 项目说明
```

## 🔧 配置说明

### 环境变量配置
```bash
# OpenAI API配置
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# ChromaDB配置
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=agent_memory

# Streamlit配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 工具开关
ENABLE_WEB_SEARCH=true
ENABLE_CODE_EXECUTION=true
ENABLE_FILE_PROCESSING=true
```

## 📖 使用指南

### 基本对话
1. 打开Web界面
2. 在"对话"标签页输入问题
3. 点击"发送"获取AI回复

### 文件处理
1. 切换到"文件处理"标签页
2. 上传支持的文件格式
3. 点击"解析文件"获取内容

### 图像分析
1. 切换到"图像处理"标签页
2. 上传图像文件
3. 点击"分析图像"获取分析结果

### 数据分析
1. 切换到"数据分析"标签页
2. 输入数据或上传数据文件
3. 点击"分析数据"获取分析报告

## 🔍 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建
docker-compose build --no-cache
```

## 🐛 故障排除

### 常见问题

1. **OpenAI API错误**
   - 检查API密钥是否正确
   - 确认API账户有足够余额

2. **Docker启动失败**
   - 确认Docker服务正在运行
   - 检查端口8501和8000是否被占用

3. **文件上传失败**
   - 检查文件大小是否超过100MB限制
   - 确认文件格式是否支持

4. **记忆搜索无结果**
   - 确认ChromaDB服务正常运行
   - 检查是否有对话历史记录

## 📝 开发说明

### 添加新工具
1. 在`multimodal_agent/tools/`目录创建新工具文件
2. 继承`BaseTool`类并实现必要方法
3. 在`tool_manager.py`中注册新工具

### 扩展多模态处理
1. 在`multimodal_agent/multimodal/`目录添加处理器
2. 在`processor.py`中集成新处理器
3. 更新支持的输入类型

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📞 支持

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

*智能多模态AI Agent系统 - 让AI更智能，让交互更自然*
