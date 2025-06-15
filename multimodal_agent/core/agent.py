"""
智能多模态AI Agent核心类 - 基于最新LangGraph和ReAct技术
"""
import asyncio
import logging
import uuid

from typing import Dict, Any, List, Optional, Union

from datetime import datetime

# 最新LangChain和LangGraph导入
from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from langchain_core.tools import BaseTool

from langgraph.prebuilt import create_react_agent

from langgraph.checkpoint.memory import MemorySaver

from langgraph.graph import StateGraph, END

from config import Config

from .memory import MemoryManager

from .planner import TaskPlanner

from .executor import TaskExecutor

from ..tools import ToolManager

from ..multimodal import MultiModalProcessor

logger = logging.getLogger(__name__)


class MultiModalAgent:
    """
    智能多模态AI Agent主类
    基于最新的LangGraph ReAct框架实现
    支持多模态输入、工具调用、记忆管理和任务规划
    """


    def __init__(self):
        """初始化Agent"""
        self.config = Config()
        self.config.validate_config()

        # 初始化ChatOpenAI模型（支持最新功能）
        self.llm = ChatOpenAI(
            api_key=self.config.OPENAI_API_KEY,
            model=self.config.OPENAI_MODEL,
            temperature=self.config.OPENAI_TEMPERATURE,
            base_url=self.config.OPENAI_BASE_URL,
            max_tokens=4096,
            timeout=30
        )

        # 初始化记忆系统
        self.memory_manager = MemoryManager()
        self.memory_saver = MemorySaver()  # LangGraph记忆保存器

        # 初始化工具管理器
        self.tool_manager = ToolManager()

        # 初始化多模态处理器
        self.multimodal_processor = MultiModalProcessor()

        # 初始化任务规划器和执行器
        self.task_planner = TaskPlanner(self.llm)
        self.task_executor = TaskExecutor(self.tool_manager)

        # 初始化LangGraph ReAct Agent
        self.agent_executor = None
        self.conversation_threads = {}  # 管理多个对话线程

        # 系统提示词
        self.system_prompt = self._create_system_prompt()

        # 初始化Agent
        self._initialize_langgraph_agent()

        logger.info("MultiModalAgent initialized successfully with LangGraph ReAct framework")


    def _create_system_prompt(self) -> str:
        """创建系统提示词"""
        return """你是一个智能多模态AI助手，具备以下能力：

1. 多模态理解：能够处理文本、图像、音频、文件等多种输入
2. 工具调用：可以使用各种专业工具来完成复杂任务
3. 推理规划：使用ReAct框架进行思考-行动-观察循环
4. 记忆管理：能够记住对话历史和重要信息

请遵循以下原则：
- 仔细分析用户需求，制定合理的执行计划
- 选择最适合的工具来完成任务
- 提供准确、有用、友好的回复
- 在不确定时主动询问澄清

当前可用工具：{tools}
"""


    def _initialize_langgraph_agent(self):
        """初始化LangGraph ReAct Agent"""
        try:
            # 获取所有可用工具
            tools = self.tool_manager.get_all_tools()

            # 创建LangGraph ReAct Agent
            self.agent_executor = create_react_agent(
                model=self.llm,
                tools=tools,
                checkpointer=self.memory_saver,
                prompt=self.system_prompt.format(
                    tools=", ".join([tool.name for tool in tools])
                )
            )

            logger.info(f"LangGraph ReAct Agent initialized with {len(tools)} tools")

        except Exception as e:
            logger.error(f"Failed to initialize LangGraph agent: {e}")
            raise

    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理多模态输入 - 使用最新的LangGraph ReAct框架

        Args:
            input_data: 输入数据，包含类型、内容和元数据

        Returns:
            处理结果，包含响应、执行轨迹、性能指标等
        """
        try:
            start_time = datetime.now()

            # 获取或创建会话线程ID
            session_id = input_data.get("metadata", {}).get("session_id")
            if not session_id:
                session_id = str(uuid.uuid4())

            thread_config = {"configurable": {"thread_id": session_id}}

            # 预处理多模态输入
            processed_input = await self._preprocess_multimodal_input(input_data)

            # 创建消息
            message = HumanMessage(content=processed_input)

            # 使用LangGraph Agent执行
            execution_result = await self._execute_with_langgraph(message, thread_config)

            # 提取响应和执行轨迹
            response_content = execution_result["messages"][-1].content
            execution_trace = self._extract_execution_trace(execution_result["messages"])

            # 保存到记忆系统
            await self._save_to_memory(input_data, response_content, session_id)

            # 计算性能指标
            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "response": response_content,
                "processing_time": processing_time,
                "execution_trace": execution_trace,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "model": self.config.OPENAI_MODEL,
                    "tools_used": execution_trace.get("tools_used", []),
                    "reasoning_steps": len(execution_trace.get("steps", []))
                }
            }

        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }

    async def _preprocess_multimodal_input(self, input_data: Dict[str, Any]) -> str:
        """
        预处理多模态输入数据 - 增强版
        支持文本、图像、音频、文件等多种输入类型，并进行智能融合
        """
        input_type = input_data.get("type", "text")
        content = input_data.get("content", "")
        metadata = input_data.get("metadata", {})

        # 构建上下文信息
        context_info = []
        if metadata.get("user_id"):
            context_info.append(f"用户ID: {metadata['user_id']}")
        if metadata.get("session_id"):
            context_info.append(f"会话ID: {metadata['session_id']}")
        if metadata.get("context"):
            context_info.append(f"上下文: {metadata['context']}")

        # 获取相关历史记忆
        if isinstance(content, str) and len(content) > 10:
            try:
                relevant_memories = await self.memory_manager.search_memory(
                    query=content[:200],  # 使用前200字符搜索
                    k=3
                )
                if relevant_memories:
                    memory_context = "相关历史信息:\n"
                    for i, memory in enumerate(relevant_memories, 1):
                        memory_context += f"{i}. {memory.page_content[:100]}...\n"
                    context_info.append(memory_context)
            except Exception as e:
                logger.warning(f"Failed to retrieve relevant memories: {e}")

        context_prefix = "\n".join(context_info) + "\n\n" if context_info else ""

        # 多模态处理
        if input_type == "text":
            # 文本预处理：检测意图和实体
            processed_text = await self._enhance_text_input(content)
            return context_prefix + processed_text
        elif input_type == "image":
            image_description = await self.multimodal_processor.process_image(content)
            return context_prefix + f"[图像输入] {image_description}"
        elif input_type == "audio":
            audio_transcript = await self.multimodal_processor.process_audio(content)
            return context_prefix + f"[音频输入] {audio_transcript}"
        elif input_type == "file":
            file_content = await self.multimodal_processor.process_file(content)
            return context_prefix + f"[文件输入] {file_content}"
        elif input_type == "multimodal":
            # 多模态融合输入
            return await self._process_multimodal_fusion(input_data, context_prefix)
        else:
            return context_prefix + str(content)

    async def _enhance_text_input(self, text: str) -> str:
        """增强文本输入处理"""
        try:
            # 简单的意图检测
            intent_keywords = {
                "question": ["什么", "如何", "为什么", "怎么", "?", "？"],
                "request": ["请", "帮我", "能否", "可以"],
                "analysis": ["分析", "评估", "比较", "总结"],
                "creation": ["创建", "生成", "写", "制作"]
            }

            detected_intent = "general"
            for intent, keywords in intent_keywords.items():
                if any(keyword in text for keyword in keywords):
                    detected_intent = intent
                    break

            # 添加意图标记
            enhanced_text = f"[意图: {detected_intent}] {text}"

            return enhanced_text

        except Exception as e:
            logger.warning(f"Text enhancement failed: {e}")
            return text

    async def _process_multimodal_fusion(self, input_data: Dict[str, Any], context_prefix: str) -> str:
        """处理多模态融合输入"""
        try:
            fusion_content = input_data.get("content", {})
            fusion_result = context_prefix + "[多模态融合输入]\n"

            # 处理各种模态
            if "text" in fusion_content:
                text_enhanced = await self._enhance_text_input(fusion_content["text"])
                fusion_result += f"文本: {text_enhanced}\n"

            if "image" in fusion_content:
                image_desc = await self.multimodal_processor.process_image(fusion_content["image"])
                fusion_result += f"图像: {image_desc}\n"

            if "audio" in fusion_content:
                audio_transcript = await self.multimodal_processor.process_audio(fusion_content["audio"])
                fusion_result += f"音频: {audio_transcript}\n"

            return fusion_result

        except Exception as e:
            logger.error(f"Multimodal fusion failed: {e}")
            return context_prefix + str(input_data.get("content", ""))

    async def _execute_with_langgraph(self, message: HumanMessage, config: Dict) -> Dict:
        """使用LangGraph Agent执行任务 - 增强版"""
        try:
            # 添加执行前的准备工作
            execution_context = {
                "start_time": datetime.now(),
                "session_id": config.get("configurable", {}).get("thread_id"),
                "message_content": message.content[:100] + "..." if len(message.content) > 100 else message.content
            }

            logger.info(f"Starting LangGraph execution: {execution_context}")

            # 流式执行Agent，收集所有中间结果
            execution_steps = []
            result = None

            async for event in self.agent_executor.astream(
                {"messages": [message]},
                config=config,
                stream_mode="values"
            ):
                result = event

                # 记录执行步骤
                if "messages" in event:
                    latest_message = event["messages"][-1]
                    execution_steps.append({
                        "timestamp": datetime.now().isoformat(),
                        "message_type": type(latest_message).__name__,
                        "content_preview": str(latest_message)[:200] + "..." if len(str(latest_message)) > 200 else str(latest_message)
                    })

            # 添加执行统计信息
            if result:
                result["execution_stats"] = {
                    "total_steps": len(execution_steps),
                    "execution_time": (datetime.now() - execution_context["start_time"]).total_seconds(),
                    "session_id": execution_context["session_id"]
                }

            logger.info(f"LangGraph execution completed successfully in {result.get('execution_stats', {}).get('execution_time', 0):.2f}s")
            return result

        except Exception as e:
            logger.error(f"LangGraph execution failed: {e}")

            # 增强的错误处理
            error_response = await self._handle_execution_error(e, message, config)
            return error_response

    async def _handle_execution_error(self, error: Exception, message: HumanMessage, config: Dict) -> Dict:
        """处理执行错误"""
        try:
            error_type = type(error).__name__
            error_message = str(error)

            # 根据错误类型提供不同的处理策略
            if "timeout" in error_message.lower():
                recovery_message = "请求处理超时，请尝试简化您的问题或稍后重试。"
            elif "rate limit" in error_message.lower():
                recovery_message = "API调用频率过高，请稍后重试。"
            elif "authentication" in error_message.lower():
                recovery_message = "API认证失败，请检查配置。"
            elif "network" in error_message.lower():
                recovery_message = "网络连接问题，请检查网络连接。"
            else:
                recovery_message = f"处理过程中遇到问题：{error_message}。我会尝试用其他方式帮助您。"

            # 记录错误到日志
            logger.error(f"Execution error - Type: {error_type}, Message: {error_message}")

            # 尝试简单的回退处理
            fallback_response = await self._generate_fallback_response(message.content)

            return {
                "messages": [
                    message,
                    AIMessage(content=f"{recovery_message}\n\n{fallback_response}")
                ],
                "error_info": {
                    "error_type": error_type,
                    "error_message": error_message,
                    "recovery_attempted": True
                }
            }

        except Exception as fallback_error:
            logger.error(f"Fallback error handling failed: {fallback_error}")
            return {
                "messages": [
                    message,
                    AIMessage(content="抱歉，我遇到了一些技术问题，无法正常处理您的请求。请稍后重试。")
                ],
                "error_info": {
                    "error_type": "CriticalError",
                    "error_message": str(fallback_error)
                }
            }

    async def _generate_fallback_response(self, user_input: str) -> str:
        """生成回退响应"""
        try:
            # 简单的关键词匹配回退
            if any(keyword in user_input.lower() for keyword in ["你好", "hello", "hi"]):
                return "您好！我是您的AI助手，很高兴为您服务。"
            elif any(keyword in user_input.lower() for keyword in ["谢谢", "thank"]):
                return "不客气！如果您还有其他问题，请随时告诉我。"
            elif any(keyword in user_input.lower() for keyword in ["帮助", "help"]):
                return "我可以帮助您处理文本、图像、文件等多种类型的任务。请告诉我您需要什么帮助。"
            else:
                return "我理解您的问题，虽然遇到了一些技术困难，但我会尽力帮助您。请您重新描述一下需求，我会用其他方式来协助您。"

        except Exception as e:
            logger.error(f"Fallback response generation failed: {e}")
            return "我正在努力理解您的需求，请稍后重试。"


    def _extract_execution_trace(self, messages: List) -> Dict[str, Any]:
        """从消息列表中提取执行轨迹"""
        trace = {
            "steps": [],
            "tools_used": [],
            "reasoning_chain": []
        }

        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                # 工具调用步骤
                for tool_call in msg.tool_calls:
                    trace["tools_used"].append(tool_call.get("name", "unknown"))
                    trace["steps"].append({
                        "type": "tool_call",
                        "tool": tool_call.get("name"),
                        "args": tool_call.get("args", {}),
                        "timestamp": datetime.now().isoformat()
                    })
            elif hasattr(msg, 'content') and msg.content:
                # 推理步骤
                if "思考:" in msg.content or "Thought:" in msg.content:
                    trace["reasoning_chain"].append(msg.content)
                    trace["steps"].append({
                        "type": "reasoning",
                        "content": msg.content,
                        "timestamp": datetime.now().isoformat()
                    })

        return trace

    async def _save_to_memory(self, input_data: Dict[str, Any], response: str, session_id: str):
        """保存对话到记忆系统"""
        try:
            user_input = str(input_data.get("content", ""))

            # 保存到长期记忆
            await self.memory_manager.save_conversation(
                user_input=user_input,
                ai_response=response,
                session_id=session_id,
                metadata={
                    "input_type": input_data.get("type", "text"),
                    "timestamp": datetime.now().isoformat(),
                    "user_id": input_data.get("metadata", {}).get("user_id")
                }
            )

        except Exception as e:
            logger.error(f"Failed to save to memory: {e}")

    async def stream_response(self, input_data: Dict[str, Any]):
        """
        流式响应处理 - 实时返回Agent的思考和执行过程
        """
        try:
            session_id = input_data.get("metadata", {}).get("session_id", str(uuid.uuid4()))
            thread_config = {"configurable": {"thread_id": session_id}}

            # 预处理输入
            processed_input = await self._preprocess_multimodal_input(input_data)
            message = HumanMessage(content=processed_input)

            # 流式执行
            async for event in self.agent_executor.astream(
                {"messages": [message]},
                config=thread_config,
                stream_mode="values"
            ):
                # 提取当前步骤信息
                if "messages" in event and event["messages"]:
                    latest_message = event["messages"][-1]

                    yield {
                        "type": "step",
                        "content": latest_message.content if hasattr(latest_message, 'content') else str(latest_message),
                        "message_type": type(latest_message).__name__,
                        "timestamp": datetime.now().isoformat()
                    }

            # 最终完成信号
            yield {
                "type": "complete",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Stream response error: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def search_memory(self, query: str, k: int = None, session_id: str = None) -> List[Dict[str, Any]]:
        """
        搜索记忆 - 支持语义搜索和会话过滤
        """
        k = k or self.config.MEMORY_SEARCH_K
        return await self.memory_manager.search_memory(
            query=query,
            k=k,
            session_id=session_id
        )

    async def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取特定会话的对话历史 - 增强版"""
        try:
            # 从记忆管理器获取对话历史
            conversation_docs = await self.memory_manager.search_conversations(
                query="",  # 空查询获取所有对话
                k=limit * 2  # 获取更多结果以便过滤
            )

            # 过滤特定会话的对话
            session_conversations = []
            for doc in conversation_docs:
                if doc.metadata.get("session_id") == session_id:
                    session_conversations.append({
                        "content": doc.page_content,
                        "timestamp": doc.metadata.get("timestamp"),
                        "metadata": doc.metadata
                    })

            # 按时间排序并限制数量
            session_conversations.sort(
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )

            return session_conversations[:limit]

        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话摘要"""
        try:
            conversations = await self.get_conversation_history(session_id, limit=20)

            if not conversations:
                return {
                    "session_id": session_id,
                    "message_count": 0,
                    "summary": "暂无对话记录",
                    "topics": [],
                    "last_activity": None
                }

            # 提取主要话题
            all_content = " ".join([conv["content"] for conv in conversations])
            topics = await self._extract_topics(all_content)

            return {
                "session_id": session_id,
                "message_count": len(conversations),
                "summary": f"包含{len(conversations)}条对话记录，主要讨论了{', '.join(topics[:3])}等话题",
                "topics": topics,
                "last_activity": conversations[0]["timestamp"] if conversations else None,
                "first_activity": conversations[-1]["timestamp"] if conversations else None
            }

        except Exception as e:
            logger.error(f"Failed to get session summary: {e}")
            return {
                "session_id": session_id,
                "error": str(e)
            }

    async def _extract_topics(self, content: str) -> List[str]:
        """从内容中提取主要话题"""
        try:
            # 简单的关键词提取
            common_topics = {
                "技术": ["技术", "编程", "代码", "开发", "软件"],
                "学习": ["学习", "教育", "知识", "理解", "解释"],
                "工作": ["工作", "项目", "任务", "业务", "公司"],
                "生活": ["生活", "日常", "个人", "家庭", "健康"],
                "创作": ["写作", "创作", "设计", "艺术", "创意"],
                "分析": ["分析", "数据", "统计", "报告", "研究"]
            }

            detected_topics = []
            content_lower = content.lower()

            for topic, keywords in common_topics.items():
                if any(keyword in content_lower for keyword in keywords):
                    detected_topics.append(topic)

            return detected_topics if detected_topics else ["通用对话"]

        except Exception as e:
            logger.warning(f"Topic extraction failed: {e}")
            return ["通用对话"]

    async def clear_memory(self, session_id: str = None):
        """清除记忆 - 可以清除特定会话或全部"""
        try:
            if session_id:
                # 清除特定会话的记忆
                await self.memory_manager.clear_session_memory(session_id)
                logger.info(f"Memory cleared for session: {session_id}")
            else:
                # 清除所有记忆
                await self.memory_manager.clear_memory()
                self.conversation_threads.clear()
                logger.info("All memory cleared")

        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")


    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        tools = self.tool_manager.get_all_tools()

        return {
            "agent_type": "LangGraph ReAct Agent",
            "model": self.config.OPENAI_MODEL,
            "framework_version": "LangGraph 0.2+",
            "available_tools": len(tools),
            "tool_names": [tool.name for tool in tools],
            "active_sessions": len(self.conversation_threads),
            "memory_enabled": True,
            "multimodal_support": True,
            "status": "active",
            "capabilities": [
                "text_processing",
                "image_analysis",
                "audio_processing",
                "file_parsing",
                "web_search",
                "code_execution",
                "data_analysis"
            ],
            "last_updated": datetime.now().isoformat()
        }

    async def add_tool(self, tool: BaseTool):
        """动态添加工具"""
        try:
            self.tool_manager.add_tool(tool)
            # 重新初始化Agent以包含新工具
            self._initialize_langgraph_agent()
            logger.info(f"Tool '{tool.name}' added successfully")

        except Exception as e:
            logger.error(f"Failed to add tool: {e}")
            raise

    async def remove_tool(self, tool_name: str):
        """动态移除工具"""
        try:
            self.tool_manager.remove_tool(tool_name)
            # 重新初始化Agent
            self._initialize_langgraph_agent()
            logger.info(f"Tool '{tool_name}' removed successfully")

        except Exception as e:
            logger.error(f"Failed to remove tool: {e}")
            raise

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            "total_sessions": len(self.conversation_threads),
            "memory_usage": await self.memory_manager.get_memory_stats(),
            "tool_usage_stats": self.tool_manager.get_usage_stats(),
            "model_info": {
                "name": self.config.OPENAI_MODEL,
                "temperature": self.config.OPENAI_TEMPERATURE,
                "max_tokens": 4096
            },
            "timestamp": datetime.now().isoformat()
        }
