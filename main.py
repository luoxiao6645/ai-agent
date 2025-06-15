#!/usr/bin/env python3
"""
智能多模态AI Agent系统 - 统一启动器
支持多种启动模式：简单模式、完整模式、测试模式
"""

import os
import sys
import argparse
import logging

from pathlib import Path

from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def setup_logging(level: str = "INFO"):
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/app.log', encoding='utf-8')
        ]
    )


def check_environment() -> bool:
    """检查环境配置"""
    print("🔍 检查环境配置...")

    # 检查Python版本
    if sys.version_info < (3, 9):
        print("❌ Python版本需要3.9或更高")
        return False

    # 检查必要目录
    required_dirs = ['logs', 'cache', 'data']
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)

    # 检查环境变量文件
    if not os.path.exists('.env'):
        print("⚠️ .env文件不存在，将从示例创建")
        if os.path.exists('.env.example'):
            import shutil

            shutil.copy('.env.example', '.env')
            print("✅ 已创建.env文件，请配置API密钥")
        else:
            print("❌ .env.example文件不存在")
            return False

    print("✅ 环境检查完成")
    return True


def install_dependencies():
    """安装依赖包"""
    print("📦 检查并安装依赖包...")

    try:
        import subprocess

        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 依赖包安装完成")
            return True
        else:
            print(f"❌ 依赖包安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安装依赖包时出错: {e}")
        return False


def run_simple_mode():
    """运行简单模式"""
    print("🚀 启动简单模式...")

    try:
        import streamlit.web.cli as stcli

        sys.argv = ["streamlit", "run", "quick_start.py", "--server.port=8501"]
        stcli.main()
    except ImportError:
        print("❌ Streamlit未安装，请运行: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


def run_full_mode():
    """运行完整模式"""
    print("🚀 启动完整模式...")

    try:
        import streamlit.web.cli as stcli

        sys.argv = ["streamlit", "run", "enhanced_app.py", "--server.port=8501"]
        stcli.main()
    except ImportError:
        print("❌ Streamlit未安装，请运行: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


def run_test_mode():
    """运行测试模式"""
    print("🧪 启动测试模式...")

    try:
        # 运行系统测试
        from simple_test import main as test_main

        test_main()

        # 启动简单界面
        import streamlit.web.cli as stcli

        sys.argv = ["streamlit", "run", "app.py", "--server.port=8502"]
        stcli.main()
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试模式启动失败: {e}")
        sys.exit(1)


def run_api_mode():
    """运行API模式"""
    print("🌐 启动API模式...")

    try:
        # 这里可以添加FastAPI或Flask API启动逻辑
        print("⚠️ API模式正在开发中...")
        print("💡 当前可以使用Streamlit Web界面")
        run_full_mode()
    except Exception as e:
        print(f"❌ API模式启动失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能多模态AI Agent系统启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
启动模式说明:
  simple    - 简单模式，基础功能，快速启动
  full      - 完整模式，所有功能，需要完整配置
  test      - 测试模式，用于开发和调试
  api       - API模式，提供REST API接口

示例:
  python main.py simple              # 简单模式
  python main.py full --port 8501    # 完整模式，指定端口
  python main.py test --install      # 测试模式，自动安装依赖
        """
    )

    parser.add_argument(
        'mode',
        choices=['simple', 'full', 'test', 'api'],
        help='启动模式'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8501,
        help='Web服务端口 (默认: 8501)'
    )

    parser.add_argument(
        '--install',
        action='store_true',
        help='自动安装依赖包'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )

    parser.add_argument(
        '--skip-check',
        action='store_true',
        help='跳过环境检查'
    )

    args = parser.parse_args()

    # 设置日志
    setup_logging(args.log_level)

    print("🤖 智能多模态AI Agent系统")
    print("=" * 50)

    # 环境检查
    if not args.skip_check:
        if not check_environment():
            print("❌ 环境检查失败")
            sys.exit(1)

    # 安装依赖
    if args.install:
        if not install_dependencies():
            print("❌ 依赖安装失败")
            sys.exit(1)

    # 设置端口环境变量
    os.environ['STREAMLIT_SERVER_PORT'] = str(args.port)

    # 根据模式启动
    try:
        if args.mode == 'simple':
            run_simple_mode()
        elif args.mode == 'full':
            run_full_mode()
        elif args.mode == 'test':
            run_test_mode()
        elif args.mode == 'api':
            run_api_mode()
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
