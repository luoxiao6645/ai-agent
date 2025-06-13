"""
文本处理器
"""
import asyncio
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

class TextProcessor:
    """文本处理器"""
    
    def __init__(self):
        """初始化文本处理器"""
        logger.info("TextProcessor initialized")
    
    async def process(self, text: Any) -> str:
        """
        处理文本输入
        
        Args:
            text: 文本内容
            
        Returns:
            处理后的文本
        """
        try:
            # 转换为字符串
            text_str = str(text)
            
            # 基本清理
            cleaned_text = self._clean_text(text_str)
            
            # 返回处理后的文本
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            return f"文本处理失败: {str(e)}"
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    async def extract_keywords(self, text: str) -> list:
        """提取关键词"""
        # 简单的关键词提取
        words = text.split()
        # 过滤短词和常见词
        keywords = [word for word in words if len(word) > 3]
        return keywords[:10]  # 返回前10个关键词
    
    async def summarize(self, text: str, max_length: int = 200) -> str:
        """文本摘要"""
        if len(text) <= max_length:
            return text
        
        # 简单的摘要：取前几句话
        sentences = text.split('。')
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + "。"
            else:
                break
        
        return summary or text[:max_length] + "..."
