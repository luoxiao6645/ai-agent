"""
工具管理器
"""
import logging
from typing import Dict, List, Optional, Any
from langchain.tools.base import BaseTool

from config import Config
from .web_search import WebSearchTool
from .document import DocumentParserTool
from .code_exec import CodeExecutorTool
from .data_analysis import DataAnalysisTool
from .image_processor import ImageProcessorTool
from .audio_processor import AudioProcessorTool
from .translator import TranslatorTool
from .calculator import CalculatorTool
from .file_manager import FileManagerTool
from .email_sender import EmailSenderTool
from .calendar_manager import CalendarManagerTool
from .api_caller import APICallerTool

logger = logging.getLogger(__name__)

class ToolManager:
    """工具管理器 - 管理所有可用工具"""
    
    def __init__(self):
        """初始化工具管理器"""
        self.config = Config()
        self.tools: Dict[str, BaseTool] = {}
        self._initialize_tools()
        
        logger.info(f"ToolManager initialized with {len(self.tools)} tools")
    
    def _initialize_tools(self):
        """初始化所有工具"""
        try:
            # 1. Web搜索工具
            if self.config.ENABLE_WEB_SEARCH:
                self.tools["web_search"] = WebSearchTool()
            
            # 2. 文档解析工具
            if self.config.ENABLE_FILE_PROCESSING:
                self.tools["document_parser"] = DocumentParserTool()
            
            # 3. 代码执行工具
            if self.config.ENABLE_CODE_EXECUTION:
                self.tools["code_executor"] = CodeExecutorTool()
            
            # 4. 数据分析工具
            self.tools["data_analyzer"] = DataAnalysisTool()
            
            # 5. 图像处理工具
            self.tools["image_processor"] = ImageProcessorTool()
            
            # 6. 音频处理工具
            self.tools["audio_processor"] = AudioProcessorTool()
            
            # 7. 翻译工具
            self.tools["translator"] = TranslatorTool()
            
            # 8. 计算工具
            self.tools["calculator"] = CalculatorTool()
            
            # 9. 文件管理工具
            if self.config.ENABLE_FILE_PROCESSING:
                self.tools["file_manager"] = FileManagerTool()
            
            # 10. 邮件工具
            self.tools["email_sender"] = EmailSenderTool()
            
            # 11. 日历工具
            self.tools["calendar_manager"] = CalendarManagerTool()
            
            # 12. API调用工具
            self.tools["api_caller"] = APICallerTool()
            
            logger.info("All tools initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            raise
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取指定工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具实例或None
        """
        return self.tools.get(tool_name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """获取所有可用工具"""
        return list(self.tools.values())
    
    def get_tool_names(self) -> List[str]:
        """获取所有工具名称"""
        return list(self.tools.keys())
    
    def is_tool_available(self, tool_name: str) -> bool:
        """检查工具是否可用"""
        return tool_name in self.tools
    
    def add_tool(self, tool_name: str, tool: BaseTool):
        """
        添加新工具
        
        Args:
            tool_name: 工具名称
            tool: 工具实例
        """
        self.tools[tool_name] = tool
        logger.info(f"Tool '{tool_name}' added")
    
    def remove_tool(self, tool_name: str) -> bool:
        """
        移除工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            是否成功移除
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Tool '{tool_name}' removed")
            return True
        return False
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        获取工具信息
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具信息字典
        """
        tool = self.get_tool(tool_name)
        if tool:
            return {
                "name": tool.name,
                "description": tool.description,
                "args_schema": tool.args_schema.schema() if tool.args_schema else None
            }
        return None
    
    def get_all_tools_info(self) -> List[Dict[str, Any]]:
        """获取所有工具信息"""
        tools_info = []
        for tool_name in self.tools:
            info = self.get_tool_info(tool_name)
            if info:
                tools_info.append(info)
        return tools_info
    
    async def test_tool(self, tool_name: str, test_input: str = "test") -> Dict[str, Any]:
        """
        测试工具功能
        
        Args:
            tool_name: 工具名称
            test_input: 测试输入
            
        Returns:
            测试结果
        """
        try:
            tool = self.get_tool(tool_name)
            if not tool:
                return {"success": False, "error": f"Tool '{tool_name}' not found"}
            
            # 执行测试
            result = await tool.arun(test_input)
            
            return {
                "success": True,
                "tool_name": tool_name,
                "test_input": test_input,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e)
            }
    
    async def test_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """测试所有工具"""
        results = {}
        
        for tool_name in self.tools:
            results[tool_name] = await self.test_tool(tool_name)
        
        return results
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """
        按类别获取工具
        
        Args:
            category: 工具类别
            
        Returns:
            该类别的工具列表
        """
        category_mapping = {
            "search": ["web_search"],
            "processing": ["document_parser", "image_processor", "audio_processor"],
            "analysis": ["data_analyzer", "code_executor"],
            "communication": ["email_sender", "translator"],
            "utility": ["calculator", "file_manager", "calendar_manager", "api_caller"]
        }
        
        tool_names = category_mapping.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """获取工具统计信息"""
        return {
            "total_tools": len(self.tools),
            "available_tools": list(self.tools.keys()),
            "categories": {
                "search": len(self.get_tools_by_category("search")),
                "processing": len(self.get_tools_by_category("processing")),
                "analysis": len(self.get_tools_by_category("analysis")),
                "communication": len(self.get_tools_by_category("communication")),
                "utility": len(self.get_tools_by_category("utility"))
            }
        }
