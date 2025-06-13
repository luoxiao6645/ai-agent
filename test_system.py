"""
系统测试脚本
"""
import asyncio
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multimodal_agent.core.agent import MultiModalAgent
from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始系统测试...")
    
    try:
        # 初始化Agent
        print("1. 初始化Agent...")
        agent = MultiModalAgent()
        print("✅ Agent初始化成功")
        
        # 测试基本对话
        print("\n2. 测试基本对话...")
        test_input = {
            "type": "text",
            "content": "你好，请介绍一下你自己"
        }
        
        result = await agent.process_input(test_input)
        print(f"✅ 对话测试成功")
        print(f"响应: {result['response'][:100]}...")
        
        # 测试工具管理器
        print("\n3. 测试工具管理器...")
        tools = agent.tool_manager.get_tool_names()
        print(f"✅ 可用工具数量: {len(tools)}")
        print(f"工具列表: {', '.join(tools)}")
        
        # 测试记忆系统
        print("\n4. 测试记忆系统...")
        await agent.memory_manager.save_conversation("测试输入", "测试响应")
        memory_results = await agent.memory_manager.search_memory("测试")
        print(f"✅ 记忆系统测试成功，找到 {len(memory_results)} 条记录")
        
        # 测试Agent状态
        print("\n5. 测试Agent状态...")
        status = agent.get_status()
        print(f"✅ Agent状态: {status}")
        
        print("\n🎉 所有测试通过！系统运行正常")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

async def test_tools():
    """测试工具功能"""
    print("\n🔧 测试工具功能...")
    
    try:
        agent = MultiModalAgent()
        
        # 测试计算工具
        print("测试计算工具...")
        calc_tool = agent.tool_manager.get_tool("calculator")
        if calc_tool:
            result = await calc_tool._arun("2 + 3 * 4")
            print(f"计算结果: {result}")
        
        # 测试Web搜索工具
        print("测试Web搜索工具...")
        search_tool = agent.tool_manager.get_tool("web_search")
        if search_tool:
            result = await search_tool._arun("Python编程", 3)
            print(f"搜索结果: {result[:100]}...")
        
        # 测试数据分析工具
        print("测试数据分析工具...")
        data_tool = agent.tool_manager.get_tool("data_analyzer")
        if data_tool:
            test_data = '[{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]'
            result = await data_tool._arun(test_data, "basic")
            print(f"分析结果: {result[:100]}...")
        
        print("✅ 工具测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 工具测试失败: {str(e)}")
        return False

def test_configuration():
    """测试配置"""
    print("\n⚙️ 测试配置...")
    
    try:
        config = Config()
        
        # 检查必要配置
        if not config.OPENAI_API_KEY:
            print("⚠️ 警告: OPENAI_API_KEY未设置")
            return False
        
        print(f"✅ OpenAI模型: {config.OPENAI_MODEL}")
        print(f"✅ ChromaDB目录: {config.CHROMA_PERSIST_DIR}")
        print(f"✅ Streamlit端口: {config.STREAMLIT_SERVER_PORT}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("🤖 智能多模态AI Agent系统测试")
    print("=" * 50)
    
    # 测试配置
    config_ok = test_configuration()
    if not config_ok:
        print("❌ 配置测试失败，请检查.env文件")
        return
    
    # 测试基本功能
    basic_ok = await test_basic_functionality()
    
    # 测试工具
    tools_ok = await test_tools()
    
    # 总结
    print("\n" + "=" * 50)
    if basic_ok and tools_ok:
        print("🎉 所有测试通过！系统准备就绪")
        print("\n💡 下一步:")
        print("1. 运行 start.sh (Linux/Mac) 或 start.bat (Windows)")
        print("2. 访问 http://localhost:8501 使用Web界面")
    else:
        print("❌ 部分测试失败，请检查配置和依赖")

if __name__ == "__main__":
    asyncio.run(main())
