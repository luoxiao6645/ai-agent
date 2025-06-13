"""
Web搜索工具
"""
import asyncio
import logging
from typing import Optional, Type
import aiohttp
import json

from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class WebSearchInput(BaseModel):
    """Web搜索输入模型"""
    query: str = Field(description="搜索查询")
    num_results: int = Field(default=5, description="返回结果数量")

class WebSearchTool(BaseTool):
    """Web搜索工具 - 实时网络信息检索"""

    name: str = "web_search"
    description: str = "搜索网络信息，获取最新的网络内容"
    args_schema: Type[BaseModel] = WebSearchInput
    
    def __init__(self):
        super().__init__()
        # 这里可以配置搜索API，如Google Custom Search API
        self.search_api_key = None  # 需要配置实际的API密钥
        self.search_engine_id = None  # 需要配置搜索引擎ID
    
    def _run(self, query: str, num_results: int = 5) -> str:
        """同步执行搜索"""
        return asyncio.run(self._arun(query, num_results))
    
    async def _arun(self, query: str, num_results: int = 5) -> str:
        """异步执行搜索"""
        try:
            # 如果有配置的搜索API，使用真实搜索
            if self.search_api_key and self.search_engine_id:
                return await self._real_search(query, num_results)
            else:
                # 模拟搜索结果
                return await self._mock_search(query, num_results)
                
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f"搜索失败: {str(e)}"
    
    async def _real_search(self, query: str, num_results: int) -> str:
        """执行真实的网络搜索"""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.search_api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(num_results, 10)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_search_results(data)
                    else:
                        return f"搜索API请求失败: {response.status}"
                        
        except Exception as e:
            logger.error(f"Real search failed: {e}")
            return f"搜索执行失败: {str(e)}"
    
    async def _mock_search(self, query: str, num_results: int) -> str:
        """模拟搜索结果"""
        # 模拟网络延迟
        await asyncio.sleep(1)
        
        # 生成模拟搜索结果
        mock_results = []
        for i in range(min(num_results, 5)):
            result = {
                "title": f"关于'{query}'的搜索结果 {i+1}",
                "link": f"https://example.com/result{i+1}",
                "snippet": f"这是关于'{query}'的相关信息。包含了详细的描述和相关内容..."
            }
            mock_results.append(result)
        
        return self._format_mock_results(mock_results, query)
    
    def _format_search_results(self, data: dict) -> str:
        """格式化真实搜索结果"""
        if "items" not in data:
            return "未找到搜索结果"
        
        results = []
        for item in data["items"]:
            result = f"标题: {item.get('title', 'N/A')}\n"
            result += f"链接: {item.get('link', 'N/A')}\n"
            result += f"摘要: {item.get('snippet', 'N/A')}\n"
            results.append(result)
        
        return "\n" + "="*50 + "\n".join(results)
    
    def _format_mock_results(self, results: list, query: str) -> str:
        """格式化模拟搜索结果"""
        formatted_results = [f"搜索查询: {query}\n搜索结果:"]
        
        for i, result in enumerate(results, 1):
            formatted_result = f"\n{i}. {result['title']}"
            formatted_result += f"\n   链接: {result['link']}"
            formatted_result += f"\n   摘要: {result['snippet']}"
            formatted_results.append(formatted_result)
        
        formatted_results.append(f"\n注意: 这是模拟搜索结果。要使用真实搜索，请配置Google Custom Search API。")
        
        return "\n".join(formatted_results)
    
    def configure_api(self, api_key: str, search_engine_id: str):
        """配置搜索API"""
        self.search_api_key = api_key
        self.search_engine_id = search_engine_id
        logger.info("Web search API configured")
    
    async def test_connection(self) -> bool:
        """测试搜索连接"""
        try:
            result = await self._arun("test", 1)
            return "搜索失败" not in result
        except Exception:
            return False
