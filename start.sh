#!/bin/bash

# 智能多模态AI Agent系统启动脚本

echo "🤖 启动智能多模态AI Agent系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "⚠️  未找到.env文件，从模板创建..."
    cp .env.example .env
    echo "📝 请编辑.env文件，填入您的OpenAI API密钥"
    echo "💡 编辑完成后，请重新运行此脚本"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data logs chroma_db chroma_data

# 构建并启动服务
echo "🔨 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

echo ""
echo "✅ 智能多模态AI Agent系统启动完成！"
echo ""
echo "🌐 访问地址:"
echo "   - Web界面: http://localhost:8501"
echo "   - ChromaDB: http://localhost:8000"
echo ""
echo "📋 常用命令:"
echo "   - 查看日志: docker-compose logs -f"
echo "   - 停止服务: docker-compose down"
echo "   - 重启服务: docker-compose restart"
echo ""
echo "🔧 如需修改配置，请编辑.env文件后重启服务"
