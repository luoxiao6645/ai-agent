"""
简单系统测试脚本 - 不依赖外部库
"""
import os
import sys


def test_project_structure():
    """测试项目结构"""
    print("🏗️ 测试项目结构...")

    required_files = [
        "config.py",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "README.md",
        ".env.example",
        "multimodal_agent/__init__.py",
        "multimodal_agent/core/agent.py",
        "multimodal_agent/core/memory.py",
        "multimodal_agent/tools/tool_manager.py",
        "ui/streamlit_app.py"
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
        return False
    else:
        print("✅ 项目结构完整")
        return True


def test_configuration():
    """测试配置文件"""
    print("\n⚙️ 测试配置文件...")

    try:
        # 检查.env.example文件
        if os.path.exists(".env.example"):
            with open(".env.example", "r", encoding="utf-8") as f:
                content = f.read()
                if "OPENAI_API_KEY" in content:
                    print("✅ .env.example文件正常")
                else:
                    print("❌ .env.example文件缺少必要配置")
                    return False
        else:
            print("❌ 缺少.env.example文件")
            return False

        # 检查requirements.txt
        if os.path.exists("requirements.txt"):
            with open("requirements.txt", "r", encoding="utf-8") as f:
                content = f.read()
                required_packages = ["langchain", "openai", "streamlit", "chromadb"]
                missing_packages = []
                for package in required_packages:
                    if package not in content:
                        missing_packages.append(package)

                if missing_packages:
                    print(f"❌ requirements.txt缺少包: {missing_packages}")
                    return False
                else:
                    print("✅ requirements.txt包含必要依赖")

        return True

    except Exception as e:
        print(f"❌ 配置测试失败: {str(e)}")
        return False


def test_docker_config():
    """测试Docker配置"""
    print("\n🐳 测试Docker配置...")

    try:
        # 检查Dockerfile
        if os.path.exists("Dockerfile"):
            with open("Dockerfile", "r", encoding="utf-8") as f:
                content = f.read()
                if "FROM python:" in content and "streamlit" in content:
                    print("✅ Dockerfile配置正常")
                else:
                    print("❌ Dockerfile配置异常")
                    return False
        else:
            print("❌ 缺少Dockerfile")
            return False

        # 检查docker-compose.yml
        if os.path.exists("docker-compose.yml"):
            with open("docker-compose.yml", "r", encoding="utf-8") as f:
                content = f.read()
                if "multimodal-agent" in content and "chromadb" in content:
                    print("✅ docker-compose.yml配置正常")
                else:
                    print("❌ docker-compose.yml配置异常")
                    return False
        else:
            print("❌ 缺少docker-compose.yml")
            return False

        return True

    except Exception as e:
        print(f"❌ Docker配置测试失败: {str(e)}")
        return False


def test_startup_scripts():
    """测试启动脚本"""
    print("\n🚀 测试启动脚本...")

    scripts_exist = True

    if os.path.exists("start.sh"):
        print("✅ start.sh存在")
    else:
        print("❌ 缺少start.sh")
        scripts_exist = False

    if os.path.exists("start.bat"):
        print("✅ start.bat存在")
    else:
        print("❌ 缺少start.bat")
        scripts_exist = False

    return scripts_exist


def show_next_steps():
    """显示下一步操作"""
    print("\n📋 下一步操作:")
    print("1. 复制.env.example为.env并填入OpenAI API密钥")
    print("2. 安装依赖: pip install -r requirements.txt")
    print("3. 运行测试: python test_system.py")
    print("4. 启动系统:")
    print("   - Linux/Mac: ./start.sh")
    print("   - Windows: start.bat")
    print("5. 访问Web界面: http://localhost:8501")


def main():
    """主测试函数"""
    print("🤖 智能多模态AI Agent系统 - 简单测试")
    print("=" * 60)

    tests = [
        ("项目结构", test_project_structure),
        ("配置文件", test_configuration),
        ("Docker配置", test_docker_config),
        ("启动脚本", test_startup_scripts)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}测试异常: {str(e)}")

    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 基础测试全部通过！")
        print("✅ 项目结构正确，可以继续下一步")
        show_next_steps()
    else:
        print("⚠️ 部分测试失败，请检查项目配置")
        print("💡 建议重新按照文档要求配置项目")

if __name__ == "__main__":
    main()
