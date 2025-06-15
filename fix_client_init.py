#!/usr/bin/env python3
"""
AI客户端初始化问题诊断和修复工具

解决常见的客户端初始化失败问题
"""

import os
import sys

from pathlib import Path

from dotenv import load_dotenv


def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")

    # 检查.env文件
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        if env_example.exists():
            print("⚠️ .env文件不存在，正在从.env.example创建...")
            import shutil

            shutil.copy(env_example, env_file)
            print("✅ .env文件已创建")
        else:
            print("❌ .env和.env.example文件都不存在")
            create_env_file()
    else:
        print("✅ .env文件存在")

    # 加载环境变量
    load_dotenv()

    return True


def create_env_file():
    """创建基础.env文件"""
    print("📝 创建基础.env文件...")

    env_content = """# 智能多模态AI Agent - 环境变量配置

# ===== API配置 (必需) =====
# Volcano Engine ARK API（推荐）
ARK_API_KEY=your_volcano_engine_ark_api_key_here
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=ep-20250506230532-w7rdw

# OpenAI API（可选）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# ===== 应用配置 =====
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0
HEALTH_CHECK_PORT=8080

# ===== 性能优化配置 =====
OPTIMIZATION_LEVEL=balanced
ENABLE_CACHING=true
ENABLE_CONNECTION_POOLING=true
ENABLE_ASYNC_PROCESSING=true
ENABLE_PERFORMANCE_MONITORING=true

# 缓存配置
CACHE_MAX_SIZE=1000
CACHE_DEFAULT_TTL=3600
CACHE_EVICTION_POLICY=lru

# 连接池配置
HTTP_POOL_SIZE=10
HTTP_MAX_RETRIES=3
HTTP_TIMEOUT=30

# 异步处理配置
ASYNC_MAX_WORKERS=4
ASYNC_QUEUE_SIZE=100

# ===== 安全配置 =====
ENABLE_SECURITY=true
SESSION_TIMEOUT=3600

# ===== 调试配置 =====
DEBUG=false
LOG_LEVEL=INFO
"""

    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)

    print("✅ .env文件已创建")
    print("⚠️ 请编辑.env文件，设置您的API密钥")


def check_api_keys():
    """检查API密钥配置"""
    print("🔑 检查API密钥配置...")

    ark_api_key = os.getenv("ARK_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    issues = []

    # 检查ARK API密钥
    if not ark_api_key or ark_api_key in ["your_volcano_engine_ark_api_key_here", "your_ark_api_key_here"]:
        issues.append("ARK_API_KEY未设置或使用默认值")
    else:
        print("✅ ARK_API_KEY已设置")

    # 检查OpenAI API密钥
    if not openai_api_key or openai_api_key in ["your_openai_api_key_here"]:
        print("⚠️ OPENAI_API_KEY未设置（可选）")
    else:
        print("✅ OPENAI_API_KEY已设置")

    if issues:
        print("❌ API密钥配置问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False

    return True


def test_api_connection():
    """测试API连接"""
    print("🧪 测试API连接...")

    try:
        from openai import OpenAI

        # 测试ARK API
        ark_api_key = os.getenv("ARK_API_KEY")
        if ark_api_key and ark_api_key not in ["your_volcano_engine_ark_api_key_here", "your_ark_api_key_here"]:
            print("🔥 测试Volcano Engine ARK API...")
            try:
                client = OpenAI(
                    base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
                    api_key=ark_api_key,
                )

                response = client.chat.completions.create(
                    model=os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw"),
                    messages=[
                        {"role": "system", "content": "你是人工智能助手"},
                        {"role": "user", "content": "你好"}
                    ],
                    max_tokens=50
                )

                print("✅ ARK API连接成功")
                print(f"📝 测试响应: {response.choices[0].message.content[:50]}...")
                return True

            except Exception as e:
                print(f"❌ ARK API连接失败: {e}")

        # 测试OpenAI API
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key and openai_api_key not in ["your_openai_api_key_here"]:
            print("🤖 测试OpenAI API...")
            try:
                client = OpenAI(
                    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                    api_key=openai_api_key,
                )

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": "Hello"}
                    ],
                    max_tokens=50
                )

                print("✅ OpenAI API连接成功")
                print(f"📝 测试响应: {response.choices[0].message.content[:50]}...")
                return True

            except Exception as e:
                print(f"❌ OpenAI API连接失败: {e}")

        print("❌ 没有可用的API密钥进行测试")
        return False

    except ImportError:
        print("❌ openai库未安装，请运行: pip install openai")
        return False
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False


def check_dependencies():
    """检查依赖包"""
    print("📦 检查依赖包...")

    required_packages = [
        "streamlit",
        "openai",
        "python-dotenv",
        "requests"
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n📥 安装缺失的包:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    return True


def fix_common_issues():
    """修复常见问题"""
    print("🔧 修复常见问题...")

    # 创建必要的目录
    directories = ["logs", "cache", "data", "chroma_data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 创建目录: {directory}")

    # 检查权限
    try:
        test_file = Path("test_write.tmp")
        test_file.write_text("test")
        test_file.unlink()
        print("✅ 文件写入权限正常")
    except Exception as e:
        print(f"❌ 文件写入权限问题: {e}")

    print("✅ 常见问题修复完成")


def provide_solutions():
    """提供解决方案"""
    print("\n" + "="*50)
    print("💡 解决方案指南")
    print("="*50)

    print("\n1. 🔑 API密钥配置")
    print("   - 编辑.env文件")
    print("   - 将 'your_volcano_engine_ark_api_key_here' 替换为真实的API密钥")
    print("   - 确保API密钥有效且有足够的配额")

    print("\n2. 📦 依赖包安装")
    print("   pip install -r requirements.txt")

    print("\n3. 🌐 网络连接")
    print("   - 检查网络连接是否正常")
    print("   - 确认可以访问API端点")
    print("   - 如果在企业网络，检查代理设置")

    print("\n4. 🚀 启动应用")
    print("   # 简单版本")
    print("   python simple_streamlit_app.py")
    print("   ")
    print("   # 集成版本")
    print("   python integrated_streamlit_app.py")
    print("   ")
    print("   # 增强版本")
    print("   python enhanced_app.py")

    print("\n5. 🧪 测试API")
    print("   python test_ark_api.py")


def main():
    """主函数"""
    print("🤖 AI客户端初始化问题诊断工具")
    print("="*50)

    # 检查环境
    check_environment()

    # 检查依赖
    deps_ok = check_dependencies()

    # 检查API密钥
    api_ok = check_api_keys()

    # 修复常见问题
    fix_common_issues()

    # 测试API连接
    if deps_ok and api_ok:
        api_test_ok = test_api_connection()
    else:
        api_test_ok = False

    # 提供解决方案
    if not (deps_ok and api_ok and api_test_ok):
        provide_solutions()
    else:
        print("\n🎉 所有检查通过！现在可以启动应用了")
        print("🚀 运行: python integrated_streamlit_app.py")

if __name__ == "__main__":
    main()
