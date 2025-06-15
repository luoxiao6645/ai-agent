"""
计算工具
"""
import asyncio
import logging
import math
import re

from typing import Optional, Type

from langchain.tools.base import BaseTool

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CalculatorInput(BaseModel):
    """计算器输入模型"""
    expression: str = Field(description="数学表达式")


class CalculatorTool(BaseTool):
    """计算工具 - 数学计算和公式解析"""

    name = "calculator"
    description = "执行数学计算和公式解析"
    args_schema: Type[BaseModel] = CalculatorInput


    def _run(self, expression: str) -> str:
        return asyncio.run(self._arun(expression))

    async def _arun(self, expression: str) -> str:
        try:
            # 安全的数学计算
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round})

            # 清理表达式
            expression = re.sub(r'[^0-9+\-*/().,\s]', '', expression)

            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"计算结果: {expression} = {result}"
        except Exception as e:
            return f"计算失败: {str(e)}"
