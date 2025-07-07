#!/usr/bin/env python3
"""
搜索功能测试脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_search import EnhancedSearchEngine, SmartSearchManager
    print("✅ 搜索模块导入成功")
except ImportError as e:
    print(f"❌ 搜索模块导入失败: {e}")
    print("请安装依赖: pip install duckduckgo-search beautifulsoup4 aiohttp")
    sys.exit(1)


async def test_search_engine():
    """测试搜索引擎"""
    print("\n🔍 测试搜索引擎...")
    
    search_engine = EnhancedSearchEngine()
    
    # 测试搜索判断
    test_queries = [
        "今天的天气怎么样",
        "2024年最新科技新闻", 
        "什么是人工智能",
        "最近的股市行情",
        "Python编程教程"
    ]
    
    print("\n📝 搜索判断测试:")
    for query in test_queries:
        should_search = search_engine.should_search(query)
        print(f"  '{query}' -> {'需要搜索' if should_search else '不需要搜索'}")
    
    # 测试实际搜索
    print("\n🌐 实际搜索测试:")
    test_query = "Python 3.12 新特性"
    print(f"搜索查询: {test_query}")
    
    try:
        results = await search_engine.search(test_query, max_results=3)
        if results:
            print(f"✅ 找到 {len(results)} 个结果:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']}")
                print(f"     {result['url']}")
                print(f"     {result['snippet'][:100]}...")
                print()
        else:
            print("❌ 未找到搜索结果")
    except Exception as e:
        print(f"❌ 搜索失败: {e}")


async def test_smart_manager():
    """测试智能搜索管理器"""
    print("\n🧠 测试智能搜索管理器...")
    
    # 模拟OpenAI客户端
    class MockClient:
        class ChatCompletions:
            def create(self, **kwargs):
                class MockResponse:
                    def __init__(self):
                        self.choices = [MockChoice()]
                
                class MockChoice:
                    def __init__(self):
                        self.message = MockMessage()
                
                class MockMessage:
                    def __init__(self):
                        self.content = "这是一个模拟的AI回答。"
                
                return MockResponse()
        
        def __init__(self):
            self.chat = MockClient.ChatCompletions()
    
    manager = SmartSearchManager()
    mock_client = MockClient()
    
    test_queries = [
        "今天北京的天气如何？",
        "什么是机器学习？",
        "2024年最新的AI发展趋势"
    ]
    
    for query in test_queries:
        print(f"\n处理查询: {query}")
        try:
            answer, used_search = await manager.process_query(
                query, mock_client, "gpt-3.5-turbo"
            )
            print(f"使用搜索: {'是' if used_search else '否'}")
            print(f"回答长度: {len(answer)} 字符")
            if used_search:
                print("✅ 成功使用搜索增强回答")
            else:
                print("ℹ️ 使用普通回答")
        except Exception as e:
            print(f"❌ 处理失败: {e}")


def test_dependencies():
    """测试依赖"""
    print("🔧 检查依赖...")
    
    dependencies = [
        ('requests', 'requests'),
        ('aiohttp', 'aiohttp'),
        ('beautifulsoup4', 'bs4'),
        ('duckduckgo-search', 'duckduckgo_search')
    ]
    
    missing = []
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} (未安装)")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️ 缺少依赖: {', '.join(missing)}")
        print("安装命令: pip install " + " ".join(missing))
        return False
    else:
        print("\n✅ 所有依赖都已安装")
        return True


async def main():
    """主测试函数"""
    print("🚀 搜索功能测试开始")
    print("=" * 50)
    
    # 检查依赖
    if not test_dependencies():
        return
    
    # 测试搜索引擎
    await test_search_engine()
    
    # 测试智能管理器
    await test_smart_manager()
    
    print("\n" + "=" * 50)
    print("✅ 搜索功能测试完成")
    
    print("\n💡 使用提示:")
    print("1. 在Streamlit应用中启用搜索功能")
    print("2. 询问最新信息时会自动搜索")
    print("3. 可以在侧边栏控制搜索开关")


if __name__ == "__main__":
    asyncio.run(main())
