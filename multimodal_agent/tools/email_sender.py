"""
邮件工具
"""
import asyncio
import logging

from typing import Optional, Type

from langchain.tools.base import BaseTool

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EmailSenderInput(BaseModel):
    """邮件发送输入模型"""
    to_email: str = Field(description="收件人邮箱")
    subject: str = Field(description="邮件主题")
    content: str = Field(description="邮件内容")


class EmailSenderTool(BaseTool):
    """邮件工具 - 邮件发送和管理"""

    name = "email_sender"
    description = "发送邮件"
    args_schema: Type[BaseModel] = EmailSenderInput


    def _run(self, to_email: str, subject: str, content: str) -> str:
        return asyncio.run(self._arun(to_email, subject, content))

    async def _arun(self, to_email: str, subject: str, content: str) -> str:
        try:
            # 模拟邮件发送
            return f"邮件发送成功:\n收件人: {to_email}\n主题: {subject}\n内容: {content[:100]}..."
        except Exception as e:
            return f"邮件发送失败: {str(e)}"
