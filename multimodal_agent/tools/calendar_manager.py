"""
日历工具
"""
import asyncio
import logging
from typing import Optional, Type
from datetime import datetime

from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class CalendarManagerInput(BaseModel):
    """日历管理输入模型"""
    operation: str = Field(description="操作类型: add, list, delete")
    title: Optional[str] = Field(default=None, description="事件标题")
    date_time: Optional[str] = Field(default=None, description="日期时间")

class CalendarManagerTool(BaseTool):
    """日历工具 - 日程管理和提醒"""
    
    name = "calendar_manager"
    description = "管理日程安排和提醒"
    args_schema: Type[BaseModel] = CalendarManagerInput
    
    def _run(self, operation: str, title: Optional[str] = None, date_time: Optional[str] = None) -> str:
        return asyncio.run(self._arun(operation, title, date_time))
    
    async def _arun(self, operation: str, title: Optional[str] = None, date_time: Optional[str] = None) -> str:
        try:
            if operation == "add":
                return f"日程添加成功: {title} - {date_time}"
            elif operation == "list":
                return "今日日程:\n1. 会议 - 10:00\n2. 项目评审 - 14:00"
            elif operation == "delete":
                return f"日程删除成功: {title}"
            else:
                return f"不支持的操作: {operation}"
        except Exception as e:
            return f"日历操作失败: {str(e)}"
