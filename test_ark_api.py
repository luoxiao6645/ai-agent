"""
火山方舟API测试脚本
"""
import os

from openai import OpenAI


def test_ark_api():
    """测试火山方舟API连接"""
    print("🔥 测试火山方舟API连接...")

    # 检查环境变量
    ark_api_key = os.environ.get("ARK_API_KEY")
    if not ark_api_key or ark_api_key == "your_ark_api_key_here":
        print("❌ 请在.env文件中设置ARK_API_KEY")
        print("💡 将 'your_ark_api_key_here' 替换为您的真实API密钥")
        return False

    try:
        # 初始化客户端
        client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=ark_api_key,
        )

        print("✅ 客户端初始化成功")

        # 测试API调用
        print("🧪 测试API调用...")
        completion = client.chat.completions.create(
            model="ep-20250506230532-w7rdw",
            messages=[
                {"role": "system", "content": "你是人工智能助手"},
                {"role": "user", "content": "你好，请简单介绍一下你自己"},
            ],
            max_tokens=100
        )

        response = completion.choices[0].message.content
        print(f"✅ API调用成功!")
        print(f"📝 响应内容: {response}")

        return True

    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("🤖 火山方舟API测试")
    print("=" * 40)

    # 加载环境变量
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("✅ 环境变量加载成功")
    except ImportError:
        print("⚠️ python-dotenv未安装，请手动设置环境变量")

    # 测试API
    if test_ark_api():
        print("\n🎉 火山方舟API测试通过!")
        print("💡 现在可以运行完整的AI Agent应用了")
    else:
        print("\n❌ API测试失败")
        print("📋 请检查:")
        print("1. ARK_API_KEY是否正确设置")
        print("2. 网络连接是否正常")
        print("3. API密钥是否有效")

if __name__ == "__main__":
    main()
