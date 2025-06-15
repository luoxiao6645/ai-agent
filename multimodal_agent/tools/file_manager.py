"""
文件管理工具
"""
import asyncio
import logging
import os
import shutil

from typing import Optional, Type

from langchain.tools.base import BaseTool

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FileManagerInput(BaseModel):
    """文件管理输入模型"""
    operation: str = Field(description="操作类型: read, write, copy, move, delete, list")
    file_path: str = Field(description="文件路径")
    content: Optional[str] = Field(default=None, description="文件内容（写入时使用）")


class FileManagerTool(BaseTool):
    """文件管理工具 - 文件上传、下载、管理"""

    name = "file_manager"
    description = "管理文件和目录，包括读取、写入、复制、移动、删除等操作"
    args_schema: Type[BaseModel] = FileManagerInput


    def _run(self, operation: str, file_path: str, content: Optional[str] = None) -> str:
        return asyncio.run(self._arun(operation, file_path, content))

    async def _arun(self, operation: str, file_path: str, content: Optional[str] = None) -> str:
        try:
            if operation == "read":
                return await self._read_file(file_path)
            elif operation == "write":
                return await self._write_file(file_path, content or "")
            elif operation == "list":
                return await self._list_directory(file_path)
            elif operation == "delete":
                return await self._delete_file(file_path)
            else:
                return f"不支持的操作: {operation}"
        except Exception as e:
            return f"文件操作失败: {str(e)}"

    async def _read_file(self, file_path: str) -> str:
        """读取文件"""
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"文件内容:\n{content}"
        except Exception as e:
            return f"读取文件失败: {str(e)}"

    async def _write_file(self, file_path: str, content: str) -> str:
        """写入文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"文件写入成功: {file_path}"
        except Exception as e:
            return f"写入文件失败: {str(e)}"

    async def _list_directory(self, dir_path: str) -> str:
        """列出目录内容"""
        if not os.path.exists(dir_path):
            return f"目录不存在: {dir_path}"

        try:
            items = os.listdir(dir_path)
            return f"目录内容 ({dir_path}):\n" + "\n".join(items)
        except Exception as e:
            return f"列出目录失败: {str(e)}"

    async def _delete_file(self, file_path: str) -> str:
        """删除文件"""
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        try:
            os.remove(file_path)
            return f"文件删除成功: {file_path}"
        except Exception as e:
            return f"删除文件失败: {str(e)}"
