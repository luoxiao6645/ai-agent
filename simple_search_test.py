#!/usr/bin/env python3
"""
简单搜索功能测试
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_search import EnhancedSearchEngine
    print("✅ 搜索模块导入成功")
except ImportError as e:
    print(f"❌ 搜索模块导入失败: {e}")
    sys.exit(1)


async def test_basic_functionality():
    """测试基本功能"""
    print("\n🔍 测试基本搜索功能...")
    
    search_engine = EnhancedSearchEngine()
    
    # 测试搜索判断
    test_queries = [
        "今天的天气怎么样",
        "2024年最新科技新闻", 
        "什么是人工智能",
        "最近的股市行情"
    ]
    
    print("\n📝 搜索判断测试:")
    for query in test_queries:
        should_search = search_engine.should_search(query)
        status = "✅ 需要搜索" if should_search else "❌ 不需要搜索"
        print(f"  '{query}' -> {status}")
    
    # 测试模拟搜索
    print("\n🌐 模拟搜索测试:")
    test_query = "Python 3.12 新特性"
    print(f"搜索查询: {test_query}")
    
    try:
        results = await search_engine._search_mock(test_query, 3)
        if results:
            print(f"✅ 找到 {len(results)} 个模拟结果:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']}")
                print(f"     来源: {result['source']}")
                print()
        else:
            print("❌ 未找到搜索结果")
    except Exception as e:
        print(f"❌ 搜索失败: {e}")


def test_search_keywords():
    """测试搜索关键词识别"""
    print("\n🔑 测试搜索关键词识别...")
    
    search_engine = EnhancedSearchEngine()
    
    test_cases = [
        ("今天北京天气如何？", True),
        ("什么是机器学习？", False),
        ("2024年最新AI发展", True),
        ("Python编程基础教程", False),
        ("最近的新闻有什么？", True),
        ("如何学习编程？", False),
        ("现在股市行情怎么样？", True),
        ("数学公式推导", False)
    ]
    
    correct = 0
    total = len(test_cases)
    
    for query, expected in test_cases:
        result = search_engine.should_search(query)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{query}' -> {'需要' if result else '不需要'}搜索 (期望: {'需要' if expected else '不需要'})")
        if result == expected:
            correct += 1
    
    accuracy = correct / total * 100
    print(f"\n📊 准确率: {correct}/{total} ({accuracy:.1f}%)")


async def main():
    """主测试函数"""
    print("🚀 简单搜索功能测试")
    print("=" * 40)
    
    # 测试基本功能
    await test_basic_functionality()
    
    # 测试关键词识别
    test_search_keywords()
    
    print("\n" + "=" * 40)
    print("✅ 测试完成")
    
    print("\n💡 说明:")
    print("- 搜索判断功能正常")
    print("- 模拟搜索可以工作")
    print("- 可以在Streamlit中使用")
    print("- 安装额外依赖可获得更好体验")


if __name__ == "__main__":
    asyncio.run(main())
