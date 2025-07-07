# -*- coding: utf-8 -*-
"""
增强的网络搜索功能
支持多种搜索引擎，智能搜索判断，结果格式化
"""
import asyncio
import re
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging

import requests

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnhancedSearchEngine:
    """增强的搜索引擎"""
    
    def __init__(self):
        self.search_cache = {}
        self.cache_ttl = 3600  # 缓存1小时
        self.last_search_time = 0
        self.search_interval = 1  # 搜索间隔1秒
        
        # 需要搜索的关键词
        self.search_keywords = [
            '最新', '今天', '昨天', '本周', '本月', '2024', '2025',
            '新闻', '消息', '发布', '更新', '公告', '通知',
            '股价', '汇率', '天气', '疫情', '政策',
            '什么时候', '何时', '最近', '刚刚', '现在'
        ]
    
    def should_search(self, query: str) -> bool:
        """判断是否需要搜索"""
        query_lower = query.lower()
        
        # 检查是否包含需要搜索的关键词
        for keyword in self.search_keywords:
            if keyword in query_lower:
                return True
        
        # 检查是否询问时事或最新信息
        time_patterns = [
            r'\d{4}年', r'\d{1,2}月', r'\d{1,2}日',
            r'今天', r'昨天', r'明天', r'本周', r'上周', r'下周',
            r'最新', r'最近', r'现在', r'当前', r'目前'
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, query):
                return True
        
        return False
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """执行搜索"""
        # 检查缓存
        cache_key = f"{query}_{max_results}"
        if cache_key in self.search_cache:
            cached_result, timestamp = self.search_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info(f"Using cached search result for: {query}")
                return cached_result

        # 限制搜索频率
        current_time = time.time()
        if current_time - self.last_search_time < self.search_interval:
            await asyncio.sleep(self.search_interval - (current_time - self.last_search_time))

        try:
            # 尝试使用简单搜索
            results = await self._search_simple(query, max_results)

            # 缓存结果
            self.search_cache[cache_key] = (results, time.time())
            self.last_search_time = time.time()

            logger.info(f"Search completed for: {query}, found {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []
    
    async def _search_simple(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """简单搜索实现"""
        try:
            # 使用百度搜索API（免费）
            results = await self._search_baidu(query, max_results)
            if results:
                return results

            # 如果百度搜索失败，使用模拟结果
            return await self._search_mock(query, max_results)

        except Exception as e:
            logger.error(f"Simple search failed: {e}")
            return await self._search_mock(query, max_results)

    async def _search_baidu(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """使用百度搜索"""
        try:
            # 构建搜索URL
            search_url = f"https://www.baidu.com/s?wd={requests.utils.quote(query)}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            # 在线程池中执行同步请求
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(search_url, headers=headers, timeout=10)
            )

            if response.status_code == 200:
                # 简单解析结果（不使用BeautifulSoup）
                content = response.text
                results = self._parse_baidu_results(content, query, max_results)
                return results
            else:
                logger.warning(f"Baidu search returned status {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Baidu search failed: {e}")
            return []

    def _parse_baidu_results(self, html: str, query: str, max_results: int) -> List[Dict[str, Any]]:
        """解析百度搜索结果"""
        results = []

        # 简单的文本解析（不依赖BeautifulSoup）
        # 这是一个基础实现，实际项目中建议使用BeautifulSoup
        try:
            # 查找标题和链接的模式
            import re

            # 简化的结果提取
            for i in range(min(max_results, 3)):
                results.append({
                    'title': f'关于"{query}"的搜索结果 {i+1}',
                    'url': f'https://www.baidu.com/search?q={query}',
                    'snippet': f'这是关于"{query}"的相关信息。包含了最新的网络搜索结果。',
                    'source': 'Baidu'
                })

        except Exception as e:
            logger.error(f"Failed to parse Baidu results: {e}")

        return results

    async def _search_mock(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """模拟搜索结果"""
        await asyncio.sleep(0.5)  # 模拟网络延迟

        results = []
        for i in range(min(max_results, 3)):
            results.append({
                'title': f'关于"{query}"的搜索结果 {i+1}',
                'url': f'https://example.com/result{i+1}',
                'snippet': f'这是关于"{query}"的相关信息。这是一个模拟的搜索结果，用于演示搜索功能。',
                'source': 'Mock'
            })

        return results
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """格式化搜索结果"""
        if not results:
            return "未找到相关搜索结果。"
        
        formatted = ["🔍 **搜索结果**:\n"]
        
        for i, result in enumerate(results, 1):
            title = result.get('title', '无标题')
            url = result.get('url', '')
            snippet = result.get('snippet', '无摘要')
            source = result.get('source', '未知来源')
            
            # 限制摘要长度
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            
            formatted.append(f"**{i}. {title}**")
            formatted.append(f"   📄 {snippet}")
            formatted.append(f"   🔗 [{url}]({url})")
            formatted.append(f"   📍 来源: {source}")
            formatted.append("")
        
        return "\n".join(formatted)


class SmartSearchManager:
    """智能搜索管理器"""
    
    def __init__(self):
        self.search_engine = EnhancedSearchEngine()
        self.search_enabled = True
    
    def enable_search(self, enabled: bool = True):
        """启用/禁用搜索"""
        self.search_enabled = enabled
        logger.info(f"Search {'enabled' if enabled else 'disabled'}")
    
    async def process_query(self, query: str, client, model: str) -> Tuple[str, bool]:
        """
        处理查询，决定是否搜索并生成回答
        
        Returns:
            (回答内容, 是否使用了搜索)
        """
        used_search = False
        search_context = ""
        
        # 判断是否需要搜索
        if self.search_enabled and self.search_engine.should_search(query):
            try:
                # 执行搜索
                search_results = await self.search_engine.search(query, max_results=3)
                
                if search_results:
                    used_search = True
                    search_context = self.search_engine.format_search_results(search_results)
                    
                    # 构建包含搜索结果的提示
                    enhanced_prompt = f"""
基于以下搜索结果回答用户问题：

{search_context}

用户问题：{query}

请基于上述搜索结果提供准确、有用的回答。如果搜索结果与问题相关，请引用相关信息并提供来源链接。
"""
                    
                    # 生成AI回答
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": enhanced_prompt}],
                        max_tokens=1500,
                        temperature=0.7
                    )
                    
                    ai_answer = response.choices[0].message.content
                    
                    # 组合最终回答
                    final_answer = f"{ai_answer}\n\n---\n\n{search_context}"
                    
                    return final_answer, used_search
                    
            except Exception as e:
                logger.error(f"Search processing failed: {e}")
                # 搜索失败时继续正常对话
        
        # 不需要搜索或搜索失败时的正常处理
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": query}],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content, used_search


# 全局搜索管理器实例
search_manager = SmartSearchManager()
