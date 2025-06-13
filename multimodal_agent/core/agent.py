"""
智能多模态AI Agent核心类
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain.agents import AgentType, initialize_agent
from langchain_openai import OpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage

from config import Config
from .memory import MemoryManager
from .planner import TaskPlanner
from .executor import TaskExecutor
from ..tools import ToolManager
from ..multimodal import MultiModalProcessor

logger = logging.getLogger(__name__)

class MultiModalAgent:
    """智能多模态AI Agent主类"""
    
    def __init__(self):
        """初始化Agent"""
        self.config = Config()
        self.config.validate_config()
        
        # 初始化组件
        self.llm = OpenAI(
            openai_api_key=self.config.OPENAI_API_KEY,
            model_name=self.config.OPENAI_MODEL,
            temperature=self.config.OPENAI_TEMPERATURE,
            openai_api_base=self.config.OPENAI_BASE_URL
        )
        
        # 初始化记忆系统
        self.memory_manager = MemoryManager()
        self.short_term_memory = ConversationBufferWindowMemory(
            k=self.config.MCP_CONTEXT_LIMIT,
            return_messages=True
        )
        
        # 初始化工具管理器
        self.tool_manager = ToolManager()
        
        # 初始化多模态处理器
        self.multimodal_processor = MultiModalProcessor()
        
        # 初始化任务规划器和执行器
        self.task_planner = TaskPlanner(self.llm)
        self.task_executor = TaskExecutor(self.tool_manager)
        
        # 初始化Agent
        self.agent = None
        self._initialize_agent()
        
        logger.info("MultiModalAgent initialized successfully")
    
    def _initialize_agent(self):
        """初始化LangChain Agent"""
        try:
            tools = self.tool_manager.get_all_tools()
            self.agent = initialize_agent(
                tools=tools,
                llm=self.llm,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                memory=self.short_term_memory,
                verbose=True,
                max_iterations=10,
                early_stopping_method="generate"
            )
            logger.info("LangChain Agent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理多模态输入
        
        Args:
            input_data: 输入数据，包含类型和内容
            
        Returns:
            处理结果
        """
        try:
            start_time = datetime.now()
            
            # 预处理输入
            processed_input = await self._preprocess_input(input_data)
            
            # 任务规划
            task_plan = await self.task_planner.plan_task(processed_input)
            
            # 执行任务
            response = await self._execute_task(task_plan)
            
            # 保存到记忆
            await self._save_to_memory(input_data, response)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "response": response,
                "processing_time": processing_time,
                "task_plan": task_plan,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _preprocess_input(self, input_data: Dict[str, Any]) -> str:
        """预处理输入数据"""
        input_type = input_data.get("type", "text")
        content = input_data.get("content", "")
        
        if input_type == "text":
            return content
        elif input_type == "image":
            return await self.multimodal_processor.process_image(content)
        elif input_type == "audio":
            return await self.multimodal_processor.process_audio(content)
        elif input_type == "file":
            return await self.multimodal_processor.process_file(content)
        else:
            return str(content)
    
    async def _execute_task(self, task_plan: Dict[str, Any]) -> str:
        """执行任务"""
        if task_plan.get("use_agent", True):
            # 使用Agent执行
            return await self.agent.arun(task_plan["query"])
        else:
            # 直接执行工具
            return await self.task_executor.execute_plan(task_plan)
    
    async def _save_to_memory(self, input_data: Dict[str, Any], response: str):
        """保存对话到记忆系统"""
        try:
            user_input = str(input_data.get("content", ""))
            await self.memory_manager.save_conversation(user_input, response)
        except Exception as e:
            logger.error(f"Failed to save to memory: {e}")
    
    async def search_memory(self, query: str, k: int = None) -> List[str]:
        """搜索记忆"""
        k = k or self.config.MEMORY_SEARCH_K
        return await self.memory_manager.search_memory(query, k)
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """获取对话历史"""
        return self.short_term_memory.chat_memory.messages
    
    async def clear_memory(self):
        """清除记忆"""
        self.short_term_memory.clear()
        await self.memory_manager.clear_memory()
        logger.info("Memory cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "model": self.config.OPENAI_MODEL,
            "memory_size": len(self.short_term_memory.chat_memory.messages),
            "available_tools": len(self.tool_manager.get_all_tools()),
            "status": "active"
        }
