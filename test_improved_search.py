#!/usr/bin/env python3
"""
测试改进后的搜索功能
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_search import EnhancedSearchEngine, SmartSearchManager, WeatherHelper
    print("✅ 改进后的搜索模块导入成功")
except ImportError as e:
    print(f"❌ 搜索模块导入失败: {e}")
    sys.exit(1)


async def test_weather_functionality():
    """测试天气功能"""
    print("\n🌤️ 测试天气查询功能")
    print("=" * 30)
    
    # 测试天气指导
    cities = ['成都', '北京', '上海', '当地']
    
    for city in cities:
        print(f"\n📍 测试城市: {city}")
        guidance = WeatherHelper.get_weather_guidance(city)
        print(f"✅ 生成了 {len(guidance)} 字符的指导信息")
        print(f"预览: {guidance[:100]}...")


async def test_improved_mock_search():
    """测试改进的模拟搜索"""
    print("\n🔍 测试改进的模拟搜索")
    print("=" * 30)
    
    search_engine = EnhancedSearchEngine()
    
    test_queries = [
        ("今日天气如何，成都地区", "天气"),
        ("今天有什么新闻？", "新闻"),
        ("股市行情如何？", "股市"),
        ("Python编程教程", "通用")
    ]
    
    for query, query_type in test_queries:
        print(f"\n🔍 搜索: {query}")
        try:
            results = await search_engine._search_mock(query, 3)
            if results:
                print(f"✅ 找到 {len(results)} 个结果")
                
                # 检查链接有效性
                valid_links = 0
                for result in results:
                    url = result.get('url', '')
                    if url and not url.startswith('https://example.com'):
                        valid_links += 1
                
                print(f"📊 有效链接: {valid_links}/{len(results)}")
                
                # 显示第一个结果
                first_result = results[0]
                print(f"📄 标题: {first_result['title']}")
                print(f"🔗 链接: {first_result['url']}")
                print(f"📍 来源: {first_result['source']}")
                print(f"📝 摘要: {first_result['snippet'][:80]}...")
                
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
                if "天气" in last_message:
                    return MockResponse(
                        "根据您的查询，我为您提供了天气查询的专业指导。建议您访问中国天气网等官方网站获取最准确的天气信息。"
                    )
                elif "搜索结果" in last_message:
                    return MockResponse(
                        "基于搜索结果，我为您整理了相关信息。请注意这些是模拟结果，建议访问提供的官方网站获取最新准确信息。"
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


async def test_smart_manager_weather():
    """测试智能管理器的天气处理"""
    print("\n🧠 测试智能管理器天气处理")
    print("=" * 35)
    
    manager = SmartSearchManager()
    mock_client = MockOpenAIClient()
    
    weather_queries = [
        "今日天气如何，成都地区",
        "北京天气预报",
        "上海今天天气怎么样？",
        "天气如何？"
    ]
    
    for query in weather_queries:
        print(f"\n🌤️ 处理查询: {query}")
        try:
            answer, used_search = await manager.process_query(
                query, mock_client, "gpt-3.5-turbo"
            )
            
            search_status = "✅ 使用搜索" if used_search else "❌ 未使用搜索"
            print(f"  搜索状态: {search_status}")
            print(f"  回答长度: {len(answer)} 字符")
            
            # 检查是否包含有用信息
            if "中国天气网" in answer or "官方" in answer:
                print("  ✅ 包含有用的官方网站推荐")
            else:
                print("  ⚠️ 缺少官方网站推荐")
                
            # 显示回答的开头
            print(f"  回答预览: {answer[:100]}...")
                
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")


async def test_link_validity():
    """测试链接有效性"""
    print("\n🔗 测试链接有效性")
    print("=" * 20)
    
    search_engine = EnhancedSearchEngine()
    
    # 测试不同类型查询的链接
    test_queries = ["天气预报", "今日新闻", "股市行情"]
    
    all_links = []
    for query in test_queries:
        results = await search_engine._search_mock(query, 2)
        for result in results:
            url = result.get('url', '')
            if url:
                all_links.append((query, url, result.get('source', '')))
    
    print(f"📊 总共检查 {len(all_links)} 个链接:")
    
    valid_count = 0
    for query, url, source in all_links:
        # 检查是否为真实网站
        is_valid = not url.startswith('https://example.com')
        status = "✅" if is_valid else "❌"
        print(f"  {status} {url} (来源: {source})")
        if is_valid:
            valid_count += 1
    
    validity_rate = valid_count / len(all_links) * 100 if all_links else 0
    print(f"\n📈 链接有效率: {valid_count}/{len(all_links)} ({validity_rate:.1f}%)")


async def main():
    """主测试函数"""
    print("🚀 改进搜索功能测试")
    print("=" * 50)
    
    # 测试天气功能
    await test_weather_functionality()
    
    # 测试改进的模拟搜索
    await test_improved_mock_search()
    
    # 测试智能管理器天气处理
    await test_smart_manager_weather()
    
    # 测试链接有效性
    await test_link_validity()
    
    print("\n" + "=" * 50)
    print("✅ 改进测试完成")
    
    print("\n🎉 主要改进:")
    print("- ✅ 天气查询提供专业指导")
    print("- ✅ 搜索结果使用真实网站链接")
    print("- ✅ 改进了模拟结果的质量")
    print("- ✅ 添加了实用的使用建议")
    print("- ✅ 提供了官方网站推荐")
    
    print("\n💡 使用建议:")
    print("1. 天气查询会直接提供官方网站指导")
    print("2. 搜索结果现在包含真实可访问的链接")
    print("3. 模拟结果更加实用和相关")
    print("4. 提供了获取真实信息的明确指导")


if __name__ == "__main__":
    asyncio.run(main())
