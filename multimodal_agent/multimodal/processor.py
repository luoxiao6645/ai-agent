"""
多模态处理器
"""
import asyncio
import logging
from typing import Dict, Any, Optional
import os

from .text_processor import TextProcessor
from .image_processor import ImageProcessor
from .audio_processor import AudioProcessor
from .file_processor import FileProcessor

logger = logging.getLogger(__name__)

class MultiModalProcessor:
    """多模态处理器 - 统一处理文本、图像、音频、文件等输入"""
    
    def __init__(self):
        """初始化多模态处理器"""
        self.text_processor = TextProcessor()
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.file_processor = FileProcessor()
        
        logger.info("MultiModalProcessor initialized")
    
    async def process_input(self, input_data: Dict[str, Any]) -> str:
        """
        处理多模态输入
        
        Args:
            input_data: 输入数据，包含类型和内容
            
        Returns:
            处理后的文本
        """
        try:
            input_type = input_data.get("type", "text")
            content = input_data.get("content", "")
            
            if input_type == "text":
                return await self.process_text(content)
            elif input_type == "image":
                return await self.process_image(content)
            elif input_type == "audio":
                return await self.process_audio(content)
            elif input_type == "file":
                return await self.process_file(content)
            else:
                return f"不支持的输入类型: {input_type}"
                
        except Exception as e:
            logger.error(f"Multimodal processing failed: {e}")
            return f"多模态处理失败: {str(e)}"
    
    async def process_text(self, text: str) -> str:
        """处理文本输入"""
        return await self.text_processor.process(text)
    
    async def process_image(self, image_data: Any) -> str:
        """处理图像输入"""
        return await self.image_processor.process(image_data)
    
    async def process_audio(self, audio_data: Any) -> str:
        """处理音频输入"""
        return await self.audio_processor.process(audio_data)
    
    async def process_file(self, file_data: Any) -> str:
        """处理文件输入"""
        return await self.file_processor.process(file_data)
    
    def get_supported_types(self) -> list:
        """获取支持的输入类型"""
        return ["text", "image", "audio", "file"]
    
    async def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证输入数据"""
        result = {
            "valid": False,
            "type": None,
            "size": 0,
            "error": None
        }
        
        try:
            input_type = input_data.get("type", "text")
            content = input_data.get("content", "")
            
            result["type"] = input_type
            
            if input_type == "text":
                result["size"] = len(str(content))
                result["valid"] = True
            elif input_type in ["image", "audio", "file"]:
                # 检查文件是否存在
                if isinstance(content, str) and os.path.exists(content):
                    result["size"] = os.path.getsize(content)
                    result["valid"] = True
                else:
                    result["error"] = "文件不存在或路径无效"
            else:
                result["error"] = f"不支持的输入类型: {input_type}"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
