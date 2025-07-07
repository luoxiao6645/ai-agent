#!/usr/bin/env python3
"""
测试优化后的搜索功能
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_search import EnhancedSearchEngine, SmartSearchManager, DateTimeHelper
    print("✅ 优化后的搜索模块导入成功")
except ImportError as e:
    print(f"❌ 搜索模块导入失败: {e}")
    sys.exit(1)


def test_datetime_helper():
    """测试日期时间助手"""
    print("\n📅 测试日期时间助手...")
    
    # 测试直接回答功能
    test_queries = [
        "今天是几号？",
        "今天是多久？", 
        "现在是几点？",
        "今天星期几？",
        "今天是什么日期？",
        "今天几月几号？"
    ]
    
    for query in test_queries:
        can_answer, answer = DateTimeHelper.can_answer_directly(query)
        status = "✅ 可直接回答" if can_answer else "❌ 需要其他处理"
        print(f"  '{query}' -> {status}")
        if can_answer:
            print(f"    回答: {answer[:50]}...")


async def test_improved_search_logic():
    """测试改进的搜索逻辑"""
    print("\n🔍 测试改进的搜索逻辑...")
    
    search_engine = EnhancedSearchEngine()
    
    # 测试用例：(查询, 期望是否搜索, 描述)
    test_cases = [
        ("今天是几号？", False, "日期查询 - 不应搜索"),
        ("今天是多久？", False, "时间查询 - 不应搜索"),
        ("什么是人工智能？", False, "定义查询 - 不应搜索"),
        ("如何学习Python？", False, "教程查询 - 不应搜索"),
        ("今天有什么新闻？", True, "新闻查询 - 应该搜索"),
        ("2024年最新AI发展", True, "最新信息 - 应该搜索"),
        ("现在股市行情如何？", True, "实时信息 - 应该搜索"),
        ("最近发生了什么？", True, "时事查询 - 应该搜索"),
        ("天气预报", True, "天气查询 - 应该搜索"),
        ("为什么会下雨？", False, "原理查询 - 不应搜索")
    ]
    
    correct = 0
    total = len(test_cases)
    
    print("\n📝 搜索判断测试结果:")
    for query, expected, description in test_cases:
        result = search_engine.should_search(query)
        is_correct = result == expected
        status = "✅" if is_correct else "❌"
        action = "搜索" if result else "不搜索"
        expected_action = "搜索" if expected else "不搜索"
        
        print(f"  {status} '{query}'")
        print(f"      结果: {action} | 期望: {expected_action} | {description}")
        
        if is_correct:
            correct += 1
    
    accuracy = correct / total * 100
    print(f"\n📊 搜索判断准确率: {correct}/{total} ({accuracy:.1f}%)")


async def test_improved_mock_search():
    """测试改进的模拟搜索"""
    print("\n🌐 测试改进的模拟搜索...")
    
    search_engine = EnhancedSearchEngine()
    
    test_queries = [
        "今天有什么新闻？",
        "天气预报",
        "股市行情",
        "Python编程教程"
    ]
    
    for query in test_queries:
        print(f"\n搜索查询: {query}")
        try:
            results = await search_engine._search_mock(query, 3)
            if results:
                print(f"✅ 找到 {len(results)} 个结果:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     来源: {result['source']}")
                    print(f"     摘要: {result['snippet'][:60]}...")
            else:
                print("❌ 未找到搜索结果")
        except Exception as e:
            print(f"❌ 搜索失败: {e}")


class MockOpenAIClient:
    """模拟OpenAI客户端"""
    
    class Chat:
        class Completions:
            def create(self, **kwargs):
                messages = kwargs.get('messages', [])
                last_message = messages[-1]['content'] if messages else ""
                
                # 根据内容生成不同的回答
                if "搜索结果" in last_message:
                    return MockResponse(
                        "基于搜索结果，我为您整理了最新信息。搜索结果显示了相关的实时数据和分析。"
                    )
                else:
                    return MockResponse(
                        "这是基于我的知识库的回答。我会为您提供准确的信息和分析。"
                    )
        
        def __init__(self):
            self.completions = self.Completions()
    
    def __init__(self):
        self.chat = self.Chat()


class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]


class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)


class MockMessage:
    def __init__(self, content):
        self.content = content


async def test_smart_manager():
    """测试智能搜索管理器"""
    print("\n🧠 测试智能搜索管理器...")
    
    manager = SmartSearchManager()
    mock_client = MockOpenAIClient()
    
    test_queries = [
        "今天是几号？",           # 应该直接回答
        "今天有什么新闻？",       # 应该搜索
        "什么是机器学习？",       # 不应该搜索
        "最新的AI发展趋势"        # 应该搜索
    ]
    
    for query in test_queries:
        print(f"\n处理查询: {query}")
        try:
            answer, used_search = await manager.process_query(
                query, mock_client, "gpt-3.5-turbo"
            )
            
            search_status = "✅ 使用搜索" if used_search else "❌ 未使用搜索"
            print(f"  搜索状态: {search_status}")
            print(f"  回答长度: {len(answer)} 字符")
            
            # 显示回答的开头
            if len(answer) > 100:
                print(f"  回答预览: {answer[:100]}...")
            else:
                print(f"  完整回答: {answer}")
                
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")


async def main():
    """主测试函数"""
    print("🚀 优化后搜索功能测试")
    print("=" * 50)
    
    # 测试日期时间助手
    test_datetime_helper()
    
    # 测试改进的搜索逻辑
    await test_improved_search_logic()
    
    # 测试改进的模拟搜索
    await test_improved_mock_search()
    
    # 测试智能管理器
    await test_smart_manager()
    
    print("\n" + "=" * 50)
    print("✅ 优化测试完成")
    
    print("\n🎉 优化内容:")
    print("- ✅ 改进搜索判断逻辑")
    print("- ✅ 添加日期时间直接回答")
    print("- ✅ 优化模拟搜索结果")
    print("- ✅ 改进错误处理")
    print("- ✅ 更智能的问题分类")


if __name__ == "__main__":
    asyncio.run(main())
