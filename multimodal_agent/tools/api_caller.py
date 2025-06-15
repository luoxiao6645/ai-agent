"""
API调用工具
"""
import asyncio
import logging

from typing import Optional, Type
import aiohttp

from langchain.tools.base import BaseTool

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class APICallerInput(BaseModel):
    """API调用输入模型"""
    url: str = Field(description="API URL")
    method: str = Field(default="GET", description="HTTP方法")
    data: Optional[str] = Field(default=None, description="请求数据")


class APICallerTool(BaseTool):
    """API调用工具 - 第三方服务集成"""

    name = "api_caller"
    description = "调用第三方API服务"
    args_schema: Type[BaseModel] = APICallerInput


    def _run(self, url: str, method: str = "GET", data: Optional[str] = None) -> str:
        return asyncio.run(self._arun(url, method, data))

    async def _arun(self, url: str, method: str = "GET", data: Optional[str] = None) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url) as response:
                        result = await response.text()
                        return f"API调用成功 ({response.status}):\n{result[:500]}..."
                elif method.upper() == "POST":
                    async with session.post(url, data=data) as response:
                        result = await response.text()
                        return f"API调用成功 ({response.status}):\n{result[:500]}..."
                else:
                    return f"不支持的HTTP方法: {method}"
        except Exception as e:
            return f"API调用失败: {str(e)}"
