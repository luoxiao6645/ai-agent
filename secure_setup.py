#!/usr/bin/env python3
"""
安全设置脚本

帮助用户安全地配置AI Agent环境
"""

import os
import getpass

from pathlib import Path
import shutil


def print_banner():
    """打印横幅"""
    print("🔒 智能多模态AI Agent - 安全设置")
    print("=" * 50)
    print("此脚本将帮助您安全地配置环境变量")
    print("您的API密钥将被安全地存储在本地.env文件中")
    print("=" * 50)


def check_existing_env():
    """检查现有的.env文件"""
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️ 发现现有的.env文件")
        choice = input("是否要覆盖现有配置？(y/N): ").lower()
        if choice != 'y':
            print("❌ 设置已取消")
            return False

        # 备份现有文件
        backup_file = Path(f".env.backup.{int(os.path.getmtime(env_file))}")
        shutil.copy(env_file, backup_file)
        print(f"✅ 已备份现有配置到: {backup_file}")

    return True


def get_api_key(service_name: str, key_format: str = "") -> str:
    """安全地获取API密钥"""
    print(f"\n🔑 配置 {service_name} API密钥")

    if key_format:
        print(f"💡 密钥格式: {key_format}")

    while True:
        api_key = getpass.getpass(f"请输入您的 {service_name} API密钥 (输入时不会显示): ")

        if not api_key:
            print("❌ API密钥不能为空")
            continue

        if api_key.startswith(('your_', 'example', 'test')):
            print("❌ 请输入真实的API密钥，不是示例值")
            continue

        # 验证密钥格式
        if service_name == "火山方舟" and not api_key.startswith('ak-'):
            print("⚠️ 火山方舟API密钥通常以'ak-'开头，请确认密钥正确")
        elif service_name == "OpenAI" and not api_key.startswith('sk-'):
            print("⚠️ OpenAI API密钥通常以'sk-'开头，请确认密钥正确")

        # 确认密钥
        print(f"✅ 已输入 {len(api_key)} 位密钥")
        confirm = input("确认此密钥正确吗？(Y/n): ").lower()
        if confirm != 'n':
            return api_key


def create_env_file(config: dict):
    """创建.env文件"""
    env_content = f"""# 智能多模态AI Agent - 环境变量配置
# 此文件包含敏感信息，请勿提交到版本控制系统

# 火山方舟 API配置（推荐）
ARK_API_KEY={config.get('ark_api_key', 'your_volcano_engine_ark_api_key_here')}
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=ep-20250506230532-w7rdw

# OpenAI API配置（可选）
OPENAI_API_KEY={config.get('openai_api_key', 'your_openai_api_key_here')}
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# ChromaDB配置
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=agent_memory

# Streamlit配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/agent.log

# 工具开关
ENABLE_WEB_SEARCH=true
ENABLE_CODE_EXECUTION=true
ENABLE_FILE_PROCESSING=true

# 性能优化配置
OPTIMIZATION_LEVEL=balanced
ENABLE_CACHING=true
ENABLE_CONNECTION_POOLING=true
ENABLE_ASYNC_PROCESSING=true
ENABLE_PERFORMANCE_MONITORING=true

# 安全配置
ENABLE_SECURITY=true
SESSION_TIMEOUT=3600
"""

    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)

    # 设置文件权限（仅所有者可读写）
    try:
        os.chmod(".env", 0o600)
        print("✅ 已设置.env文件权限为仅所有者可读写")
    except:
        print("⚠️ 无法设置文件权限，请手动设置")


def verify_gitignore():
    """验证.gitignore配置"""
    gitignore_file = Path(".gitignore")

    if not gitignore_file.exists():
        print("⚠️ 未找到.gitignore文件")
        return False

    with open(gitignore_file, "r", encoding="utf-8") as f:
        content = f.read()

    if ".env" not in content:
        print("⚠️ .gitignore中未包含.env规则")
        choice = input("是否要添加.env到.gitignore？(Y/n): ").lower()
        if choice != 'n':
            with open(gitignore_file, "a", encoding="utf-8") as f:
                f.write("\n# 环境变量文件\n.env\n")
            print("✅ 已添加.env到.gitignore")
        return False

    print("✅ .gitignore配置正确")
    return True


def test_configuration():
    """测试配置"""
    print("\n🧪 测试配置...")

    try:
        from dotenv import load_dotenv

        load_dotenv()

        ark_api_key = os.getenv("ARK_API_KEY")
        if ark_api_key and not ark_api_key.startswith('your_'):
            print("✅ 火山方舟API密钥已配置")
        else:
            print("⚠️ 火山方舟API密钥未配置")

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key and not openai_api_key.startswith('your_'):
            print("✅ OpenAI API密钥已配置")
        else:
            print("ℹ️ OpenAI API密钥未配置（可选）")

        return True

    except ImportError:
        print("❌ python-dotenv未安装，请运行: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def show_next_steps():
    """显示后续步骤"""
    print("\n🎉 环境配置完成！")
    print("\n📋 后续步骤:")
    print("1. 🚀 启动应用:")
    print("   python enhanced_app.py")
    print("   # 或")
    print("   python quick_start.py")
    print("")
    print("2. 🌐 访问应用:")
    print("   http://localhost:8501")
    print("")
    print("3. 🔒 安全提醒:")
    print("   - 请勿将.env文件提交到版本控制")
    print("   - 定期更换API密钥")
    print("   - 监控API使用情况")
    print("")
    print("4. 📖 更多帮助:")
    print("   - 查看 SECURITY_GUIDE.md")
    print("   - 运行 python privacy_protection.py")


def main():
    """主函数"""
    print_banner()

    # 检查现有配置
    if not check_existing_env():
        return

    # 收集配置信息
    config = {}

    print("\n🎯 选择要配置的API服务:")
    print("1. 火山方舟API（推荐）")
    print("2. OpenAI API")
    print("3. 两者都配置")

    choice = input("请选择 (1/2/3): ").strip()

    if choice in ['1', '3']:
        config['ark_api_key'] = get_api_key("火山方舟", "ak-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    if choice in ['2', '3']:
        config['openai_api_key'] = get_api_key("OpenAI", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    if not config:
        print("❌ 未配置任何API密钥")
        return

    # 创建.env文件
    print("\n📝 创建配置文件...")
    create_env_file(config)
    print("✅ .env文件已创建")

    # 验证.gitignore
    verify_gitignore()

    # 测试配置
    if test_configuration():
        show_next_steps()
    else:
        print("❌ 配置测试失败，请检查配置")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ 设置已取消")
    except Exception as e:
        print(f"\n❌ 设置失败: {e}")
        print("请查看 SECURITY_GUIDE.md 获取帮助")
