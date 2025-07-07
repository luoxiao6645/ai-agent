#!/usr/bin/env python3
"""
搜索功能演示
展示如何在AI对话中集成搜索功能
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_search import SmartSearchManager


class MockOpenAIClient:
    """模拟OpenAI客户端"""

    class Chat:
        class Completions:
            def create(self, **kwargs):
                messages = kwargs.get('messages', [])
                last_message = messages[-1]['content'] if messages else ""

                # 模拟AI回答
                if "搜索结果" in last_message:
                    # 基于搜索结果的回答
                    return MockResponse(
                        "基于最新的搜索结果，我为您整理了相关信息。以上搜索结果显示了最新的发展动态，"
                        "您可以点击链接查看详细内容。如果您需要了解更多特定方面的信息，请告诉我。"
                    )
                else:
                    # 普通回答
                    return MockResponse(
                        "这是一个基于我的知识库的回答。我会根据已有的信息为您提供帮助。"
                    )

        def __init__(self):
            self.completions = self.Completions()

    def __init__(self):
        self.chat = self.Chat()


class MockResponse:
    """模拟响应"""
    def __init__(self, content):
        self.choices = [MockChoice(content)]


class MockChoice:
    """模拟选择"""
    def __init__(self, content):
        self.message = MockMessage(content)


class MockMessage:
    """模拟消息"""
    def __init__(self, content):
        self.content = content


async def demo_search_functionality():
    """演示搜索功能"""
    print("🚀 搜索功能演示")
    print("=" * 50)
    
    # 初始化搜索管理器和模拟客户端
    search_manager = SmartSearchManager()
    mock_client = MockOpenAIClient()
    model = "gpt-3.5-turbo"
    
    # 演示查询
    demo_queries = [
        {
            "query": "今天的天气怎么样？",
            "description": "时事查询 - 应该触发搜索"
        },
        {
            "query": "什么是机器学习？",
            "description": "知识查询 - 不需要搜索"
        },
        {
            "query": "2024年最新的AI发展趋势",
            "description": "最新信息查询 - 应该触发搜索"
        },
        {
            "query": "如何学习Python编程？",
            "description": "教程查询 - 不需要搜索"
        }
    ]
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n📝 演示 {i}: {demo['description']}")
        print(f"用户问题: {demo['query']}")
        print("-" * 30)
        
        try:
            # 处理查询
            answer, used_search = await search_manager.process_query(
                demo['query'], mock_client, model
            )
            
            # 显示结果
            search_status = "✅ 使用了搜索" if used_search else "❌ 未使用搜索"
            print(f"搜索状态: {search_status}")
            print(f"回答长度: {len(answer)} 字符")
            
            # 显示回答摘要
            if len(answer) > 200:
                print(f"回答摘要: {answer[:200]}...")
            else:
                print(f"完整回答: {answer}")
            
            if used_search:
                print("💡 这个回答包含了最新的搜索结果")
            else:
                print("💡 这个回答基于AI的知识库")
                
        except Exception as e:
            print(f"❌ 处理失败: {e}")
        
        print()


async def demo_search_control():
    """演示搜索控制功能"""
    print("\n🎛️ 搜索控制演示")
    print("=" * 30)
    
    search_manager = SmartSearchManager()
    mock_client = MockOpenAIClient()
    
    test_query = "今天有什么新闻？"
    
    # 启用搜索
    print("1. 启用搜索功能")
    search_manager.enable_search(True)
    answer1, used_search1 = await search_manager.process_query(
        test_query, mock_client, "gpt-3.5-turbo"
    )
    print(f"   结果: {'使用了搜索' if used_search1 else '未使用搜索'}")
    
    # 禁用搜索
    print("\n2. 禁用搜索功能")
    search_manager.enable_search(False)
    answer2, used_search2 = await search_manager.process_query(
        test_query, mock_client, "gpt-3.5-turbo"
    )
    print(f"   结果: {'使用了搜索' if used_search2 else '未使用搜索'}")
    
    # 重新启用
    print("\n3. 重新启用搜索功能")
    search_manager.enable_search(True)
    answer3, used_search3 = await search_manager.process_query(
        test_query, mock_client, "gpt-3.5-turbo"
    )
    print(f"   结果: {'使用了搜索' if used_search3 else '未使用搜索'}")


def demo_search_keywords():
    """演示搜索关键词识别"""
    print("\n🔍 搜索关键词识别演示")
    print("=" * 35)
    
    from enhanced_search import EnhancedSearchEngine
    search_engine = EnhancedSearchEngine()
    
    # 各种类型的查询
    query_categories = {
        "时间相关": [
            "今天的新闻",
            "2024年发生了什么",
            "最近的科技发展",
            "现在的股价"
        ],
        "实时信息": [
            "天气预报",
            "股市行情",
            "疫情数据",
            "汇率查询"
        ],
        "一般知识": [
            "什么是人工智能",
            "Python语法教程",
            "数学公式",
            "历史事件"
        ]
    }
    
    for category, queries in query_categories.items():
        print(f"\n📂 {category}:")
        for query in queries:
            should_search = search_engine.should_search(query)
            icon = "🔍" if should_search else "📚"
            action = "搜索" if should_search else "知识库"
            print(f"   {icon} {query} -> {action}")


async def main():
    """主演示函数"""
    print("🎯 AI Agent 搜索功能完整演示")
    print("=" * 60)
    
    # 基本搜索功能演示
    await demo_search_functionality()
    
    # 搜索控制演示
    await demo_search_control()
    
    # 关键词识别演示
    demo_search_keywords()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成")
    
    print("\n🎉 搜索功能特点:")
    print("- ✅ 智能判断是否需要搜索")
    print("- ✅ 支持搜索开关控制")
    print("- ✅ 搜索结果与AI回答结合")
    print("- ✅ 缓存机制提高效率")
    print("- ✅ 错误处理和降级方案")
    
    print("\n🚀 在Streamlit中使用:")
    print("1. 运行: streamlit run app.py")
    print("2. 在侧边栏启用搜索功能")
    print("3. 询问最新信息，如'今天的新闻'")
    print("4. 观察搜索过程和结果展示")


if __name__ == "__main__":
    asyncio.run(main())
