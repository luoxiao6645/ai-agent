"""
简化的Agent测试
验证测试框架工作正常
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

class SimpleAgent:
    """简化的Agent类用于测试"""
    
    def __init__(self):
        self.session_id = None
        self.conversation_history = []
    
    async def process_text(self, text: str) -> str:
        """处理文本输入"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # 简单的响应逻辑
        if "你好" in text:
            return "你好！我是AI助手，有什么可以帮助您的吗？"
        elif "计算" in text:
            return "我可以帮您进行数学计算"
        elif "再见" in text:
            return "再见！期待下次为您服务"
        else:
            return f"我收到了您的消息：{text}"
    
    def set_session(self, session_id: str):
        """设置会话ID"""
        self.session_id = session_id
    
    def add_to_history(self, role: str, content: str):
        """添加到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def get_history(self) -> list:
        """获取对话历史"""
        return self.conversation_history.copy()

@pytest.mark.unit
class TestSimpleAgent:
    """简化Agent测试"""
    
    @pytest.fixture
    def agent(self):
        """创建Agent实例"""
        return SimpleAgent()
    
    @pytest.mark.asyncio
    async def test_process_text_greeting(self, agent):
        """测试问候处理"""
        result = await agent.process_text("你好")
        assert "你好" in result
        assert "AI助手" in result
    
    @pytest.mark.asyncio
    async def test_process_text_calculation(self, agent):
        """测试计算请求"""
        result = await agent.process_text("请帮我计算")
        assert "计算" in result
    
    @pytest.mark.asyncio
    async def test_process_text_farewell(self, agent):
        """测试告别处理"""
        result = await agent.process_text("再见")
        assert "再见" in result
    
    @pytest.mark.asyncio
    async def test_process_text_general(self, agent):
        """测试一般文本处理"""
        test_text = "这是一个测试消息"
        result = await agent.process_text(test_text)
        assert test_text in result
    
    @pytest.mark.asyncio
    async def test_process_empty_text(self, agent):
        """测试空文本处理"""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await agent.process_text("")
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await agent.process_text("   ")
    
    def test_session_management(self, agent):
        """测试会话管理"""
        session_id = "test_session_123"
        agent.set_session(session_id)
        assert agent.session_id == session_id
    
    def test_conversation_history(self, agent):
        """测试对话历史"""
        # 添加对话记录
        agent.add_to_history("user", "Hello")
        agent.add_to_history("assistant", "Hi there!")
        
        # 获取历史记录
        history = agent.get_history()
        
        # 验证历史记录
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"
    
    def test_agent_initialization(self):
        """测试Agent初始化"""
        agent = SimpleAgent()
        assert agent.session_id is None
        assert agent.conversation_history == []
    
    @pytest.mark.asyncio
    async def test_multiple_interactions(self, agent):
        """测试多次交互"""
        interactions = [
            ("你好", "你好"),
            ("请帮我计算", "计算"),
            ("再见", "再见")
        ]
        
        for input_text, expected_keyword in interactions:
            result = await agent.process_text(input_text)
            assert expected_keyword in result
            
            # 记录到历史
            agent.add_to_history("user", input_text)
            agent.add_to_history("assistant", result)
        
        # 验证历史记录
        history = agent.get_history()
        assert len(history) == 6  # 3次交互，每次2条记录
