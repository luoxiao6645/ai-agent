#!/usr/bin/env python3
"""
最终搜索功能测试 - 验证所有优化
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


def test_comprehensive_search_logic():
    """全面测试搜索逻辑"""
    print("\n🔍 全面搜索逻辑测试")
    print("=" * 40)
    
    search_engine = EnhancedSearchEngine()
    
    # 测试用例：(查询, 期望是否搜索, 分类)
    test_cases = [
        # 日期时间类 - 不应搜索
        ("今天是几号？", False, "日期查询"),
        ("今天是多久？", False, "日期查询"),
        ("现在是几点？", False, "时间查询"),
        ("今天星期几？", False, "星期查询"),
        
        # 知识类 - 不应搜索
        ("什么是人工智能？", False, "定义查询"),
        ("如何学习Python？", False, "教程查询"),
        ("怎么做饭？", False, "方法查询"),
        ("为什么会下雨？", False, "原理查询"),
        
        # 实时信息类 - 应该搜索
        ("今天有什么新闻？", True, "新闻查询"),
        ("最新的AI发展趋势", True, "最新信息"),
        ("现在股市行情如何？", True, "股市查询"),
        ("股市行情怎么样？", True, "股市查询"),
        ("天气预报", True, "天气查询"),
        ("最近发生了什么？", True, "时事查询"),
        ("2024年最新科技", True, "年度信息"),
        
        # 边界情况
        ("股价如何？", True, "股价查询"),
        ("行情如何？", True, "行情查询"),
        ("如何看待股市行情？", True, "股市分析"),  # 虽然有"如何"但是关于股市
    ]
    
    correct = 0
    total = len(test_cases)
    
    for query, expected, category in test_cases:
        result = search_engine.should_search(query)
        is_correct = result == expected
        status = "✅" if is_correct else "❌"
        action = "搜索" if result else "不搜索"
        expected_action = "搜索" if expected else "不搜索"
        
        print(f"{status} {query}")
        print(f"    结果: {action} | 期望: {expected_action} | 类型: {category}")
        
        if is_correct:
            correct += 1
    
    accuracy = correct / total * 100
    print(f"\n📊 搜索判断准确率: {correct}/{total} ({accuracy:.1f}%)")
    return accuracy >= 95  # 期望95%以上准确率


def test_datetime_functionality():
    """测试日期时间功能"""
    print("\n📅 日期时间功能测试")
    print("=" * 30)
    
    # 测试可以直接回答的问题
    direct_questions = [
        "今天是几号？",
        "今天是多久？",
        "现在是几点？",
        "今天星期几？",
        "今天是什么日期？"
    ]
    
    success_count = 0
    for question in direct_questions:
        can_answer, answer = DateTimeHelper.can_answer_directly(question)
        if can_answer:
            success_count += 1
            print(f"✅ {question} -> 可直接回答")
            print(f"    回答: {answer[:50]}...")
        else:
            print(f"❌ {question} -> 无法直接回答")
    
    success_rate = success_count / len(direct_questions) * 100
    print(f"\n📊 日期时间处理成功率: {success_count}/{len(direct_questions)} ({success_rate:.1f}%)")
    return success_rate >= 80


async def test_improved_search_results():
    """测试改进的搜索结果"""
    print("\n🌐 改进搜索结果测试")
    print("=" * 30)
    
    search_engine = EnhancedSearchEngine()
    
    # 测试不同类型的查询
    test_queries = [
        ("今天有什么新闻？", "新闻"),
        ("天气预报", "天气"),
        ("股市行情", "股市"),
        ("Python编程", "通用")
    ]
    
    success_count = 0
    for query, query_type in test_queries:
        print(f"\n🔍 搜索: {query} (类型: {query_type})")
        try:
            results = await search_engine._search_mock(query, 3)
            if results:
                print(f"✅ 找到 {len(results)} 个结果")
                
                # 检查结果质量
                has_relevant_content = False
                for result in results:
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    
                    # 检查是否包含相关内容
                    if query_type == "新闻" and ("新闻" in title or "报道" in title):
                        has_relevant_content = True
                    elif query_type == "天气" and "天气" in title:
                        has_relevant_content = True
                    elif query_type == "股市" and ("股市" in title or "行情" in title):
                        has_relevant_content = True
                    elif query_type == "通用":
                        has_relevant_content = True
                
                if has_relevant_content:
                    success_count += 1
                    print("    ✅ 结果相关性良好")
                else:
                    print("    ⚠️ 结果相关性一般")
                    
                # 显示第一个结果
                first_result = results[0]
                print(f"    标题: {first_result['title']}")
                print(f"    来源: {first_result['source']}")
                
            else:
                print("❌ 未找到搜索结果")
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
    
    success_rate = success_count / len(test_queries) * 100
    print(f"\n📊 搜索结果质量: {success_count}/{len(test_queries)} ({success_rate:.1f}%)")
    return success_rate >= 75


async def main():
    """主测试函数"""
    print("🚀 最终搜索功能优化测试")
    print("=" * 60)
    
    # 运行所有测试
    test_results = []
    
    # 1. 搜索逻辑测试
    logic_passed = test_comprehensive_search_logic()
    test_results.append(("搜索逻辑", logic_passed))
    
    # 2. 日期时间功能测试
    datetime_passed = test_datetime_functionality()
    test_results.append(("日期时间", datetime_passed))
    
    # 3. 搜索结果质量测试
    results_passed = await test_improved_search_results()
    test_results.append(("搜索结果", results_passed))
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("📋 测试结果总结")
    print("=" * 20)
    
    passed_count = 0
    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} {test_name}测试")
        if passed:
            passed_count += 1
    
    overall_success = passed_count / len(test_results) * 100
    print(f"\n📊 总体测试通过率: {passed_count}/{len(test_results)} ({overall_success:.1f}%)")
    
    if overall_success >= 90:
        print("\n🎉 搜索功能优化成功！")
        print("✅ 所有主要功能都已正常工作")
        print("✅ 搜索判断逻辑准确")
        print("✅ 日期时间处理完善")
        print("✅ 搜索结果质量良好")
    else:
        print("\n⚠️ 还有改进空间")
        print("需要进一步优化的功能:")
        for test_name, passed in test_results:
            if not passed:
                print(f"- {test_name}")
    
    print("\n💡 使用建议:")
    print("1. 在Streamlit应用中测试优化后的搜索功能")
    print("2. 询问'今天是多久？'应该直接显示日期信息")
    print("3. 询问'现在股市行情如何？'应该触发搜索")
    print("4. 搜索结果现在更加相关和有用")


if __name__ == "__main__":
    asyncio.run(main())
