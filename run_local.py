"""
本地运行脚本 - 不依赖Docker
"""
import os
import sys
import subprocess
import time

def check_dependencies():
    """检查依赖包"""
    print("📦 检查依赖包...")
    
    required_packages = [
        "streamlit",
        "openai", 
        "langchain",
        "chromadb"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 未安装")
    
    if missing_packages:
        print(f"\n⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install streamlit openai langchain chromadb langchain-openai langchain-community")
        return False
    
    return True

def check_env_file():
    """检查环境变量文件"""
    print("\n🔧 检查环境配置...")
    
    if not os.path.exists(".env"):
        print("⚠️ 未找到.env文件，从模板创建...")
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("📝 已创建.env文件，请编辑并填入您的OpenAI API密钥")
            print("💡 编辑完成后重新运行此脚本")
            return False
        else:
            print("❌ 未找到.env.example模板文件")
            return False
    
    # 检查API密钥
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
            if "your_openai_api_key_here" in content:
                print("⚠️ 请在.env文件中设置真实的OpenAI API密钥")
                return False
            elif "OPENAI_API_KEY=" in content:
                print("✅ 环境配置文件存在")
                return True
    except Exception as e:
        print(f"❌ 读取.env文件失败: {e}")
        return False
    
    return True

def create_directories():
    """创建必要的目录"""
    print("\n📁 创建必要目录...")
    
    directories = ["logs", "chroma_db", "data", "temp"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}")
        else:
            print(f"✅ 目录已存在: {directory}")

def run_streamlit():
    """运行Streamlit应用"""
    print("\n🚀 启动Streamlit应用...")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        
        # 启动Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "ui/streamlit_app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--server.headless=true"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        print("🌐 应用将在 http://localhost:8501 启动")
        print("📝 按 Ctrl+C 停止服务")
        
        # 运行应用
        process = subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🤖 智能多模态AI Agent - 本地运行")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查环境配置
    if not check_env_file():
        return
    
    # 创建目录
    create_directories()
    
    # 运行应用
    print("\n" + "=" * 50)
    run_streamlit()

if __name__ == "__main__":
    main()
