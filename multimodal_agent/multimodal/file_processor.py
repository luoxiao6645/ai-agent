"""
文件处理器
"""
import asyncio
import logging
import os

from typing import Any

logger = logging.getLogger(__name__)


class FileProcessor:
    """文件处理器"""


    def __init__(self):
        """初始化文件处理器"""
        self.supported_formats = ['.txt', '.md', '.pdf', '.docx', '.xlsx', '.csv', '.json']
        logger.info("FileProcessor initialized")

    async def process(self, file_data: Any) -> str:
        """
        处理文件输入

        Args:
            file_data: 文件数据（文件路径）

        Returns:
            文件内容文本
        """
        try:
            if isinstance(file_data, str):
                # 文件路径
                return await self._process_file_path(file_data)
            else:
                return f"不支持的文件数据类型: {type(file_data)}"

        except Exception as e:
            logger.error(f"File processing failed: {e}")
            return f"文件处理失败: {str(e)}"

    async def _process_file_path(self, file_path: str) -> str:
        """处理文件路径"""
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        # 检查文件格式
        _, ext = os.path.splitext(file_path.lower())
        if ext not in self.supported_formats:
            return f"不支持的文件格式: {ext}"

        # 获取文件信息
        file_size = os.path.getsize(file_path)

        # 根据文件类型处理
        if ext in ['.txt', '.md']:
            return await self._process_text_file(file_path)
        elif ext == '.json':
            return await self._process_json_file(file_path)
        else:
            # 其他格式的基本信息
            result = f"文件信息:\n"
            result += f"- 文件路径: {file_path}\n"
            result += f"- 文件大小: {file_size} 字节\n"
            result += f"- 格式: {ext}\n"
            result += f"- 说明: 需要专门的解析器处理此类文件\n"
            return result

    async def _process_text_file(self, file_path: str) -> str:
        """处理文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            result = f"文本文件内容:\n"
            result += f"- 文件: {file_path}\n"
            result += f"- 字符数: {len(content)}\n"
            result += f"- 行数: {content.count(chr(10)) + 1}\n"
            result += f"- 内容预览:\n{content[:500]}..."

            return result
        except Exception as e:
            return f"读取文本文件失败: {str(e)}"

    async def _process_json_file(self, file_path: str) -> str:
        """处理JSON文件"""
        try:
            import json

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            result = f"JSON文件内容:\n"
            result += f"- 文件: {file_path}\n"
            result += f"- 数据类型: {type(data).__name__}\n"

            if isinstance(data, dict):
                result += f"- 键数量: {len(data)}\n"
                result += f"- 主要键: {list(data.keys())[:10]}\n"
            elif isinstance(data, list):
                result += f"- 元素数量: {len(data)}\n"

            result += f"- 内容预览:\n{str(data)[:500]}..."

            return result
        except Exception as e:
            return f"读取JSON文件失败: {str(e)}"
