"""
部署助手脚本
帮助用户选择和配置部署平台
"""
import os
import subprocess
import sys

def check_git_repo():
    """检查是否为Git仓库"""
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def init_git_repo():
    """初始化Git仓库"""
    try:
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit for deployment'], check=True)
        print("✅ Git仓库初始化完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git初始化失败: {e}")
        return False

def check_requirements():
    """检查部署要求"""
    print("🔍 检查部署要求...")
    
    # 检查必要文件
    required_files = ['app.py', 'simple_streamlit_app.py', 'requirements.txt']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    # 检查环境变量
    if not os.path.exists('.env'):
        print("⚠️ 未找到.env文件，请确保在部署平台配置环境变量")
    
    print("✅ 部署要求检查完成")
    return True

def show_deployment_options():
    """显示部署选项"""
    print("\n🚀 选择部署平台:")
    print("1. Streamlit Cloud (推荐 - 免费)")
    print("2. Heroku (付费)")
    print("3. Railway (免费额度)")
    print("4. Render (免费额度)")
    print("5. 显示部署指南")
    print("0. 退出")

def show_streamlit_cloud_guide():
    """显示Streamlit Cloud部署指南"""
    print("\n📋 Streamlit Cloud 部署步骤:")
    print("1. 将代码推送到GitHub仓库")
    print("2. 访问 https://share.streamlit.io/")
    print("3. 使用GitHub账号登录")
    print("4. 点击 'New app'")
    print("5. 选择你的仓库和分支")
    print("6. 主文件路径设置为: app.py")
    print("7. 在Advanced settings中配置Secrets:")
    print("   ARK_API_KEY = 你的API密钥")
    print("   ARK_BASE_URL = https://ark.cn-beijing.volces.com/api/v3")
    print("   ARK_MODEL = ep-20250506230532-w7rdw")
    print("8. 点击Deploy!")

def main():
    """主函数"""
    print("🤖 多模态AI Agent 部署助手")
    print("=" * 50)
    
    # 检查部署要求
    if not check_requirements():
        print("请先解决上述问题后再进行部署")
        return
    
    # 检查Git仓库
    if not check_git_repo():
        print("📁 未检测到Git仓库")
        if input("是否初始化Git仓库? (y/n): ").lower() == 'y':
            if not init_git_repo():
                return
    
    while True:
        show_deployment_options()
        choice = input("\n请选择 (0-5): ").strip()
        
        if choice == '0':
            print("👋 再见!")
            break
        elif choice == '1':
            show_streamlit_cloud_guide()
            print("\n💡 提示: 请先将代码推送到GitHub，然后按照上述步骤操作")
        elif choice == '2':
            print("\n📋 Heroku 部署:")
            print("1. 安装 Heroku CLI")
            print("2. heroku login")
            print("3. heroku create your-app-name")
            print("4. 配置环境变量: heroku config:set ARK_API_KEY=your_key")
            print("5. git push heroku main")
        elif choice == '3':
            print("\n📋 Railway 部署:")
            print("1. 访问 https://railway.app/")
            print("2. 连接GitHub仓库")
            print("3. 配置环境变量")
            print("4. 自动部署")
        elif choice == '4':
            print("\n📋 Render 部署:")
            print("1. 访问 https://render.com/")
            print("2. 创建新的Web Service")
            print("3. 连接GitHub仓库")
            print("4. 配置启动命令: streamlit run app.py")
            print("5. 配置环境变量")
        elif choice == '5':
            print("\n📖 详细部署指南请查看 DEPLOYMENT.md 文件")
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()
