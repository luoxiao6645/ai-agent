"""
记忆管理系统
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from config import Config

logger = logging.getLogger(__name__)

class MemoryManager:
    """记忆管理器"""
    
    def __init__(self):
        """初始化记忆管理器"""
        self.config = Config()
        
        # 初始化嵌入模型
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.config.OPENAI_API_KEY,
            openai_api_base=self.config.OPENAI_BASE_URL
        )
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=self.config.CHROMA_PERSIST_DIR
        )
        
        # 初始化向量存储
        self.vectorstore = Chroma(
            client=self.client,
            embedding_function=self.embeddings,
            collection_name=self.config.CHROMA_COLLECTION_NAME
        )
        
        logger.info("MemoryManager initialized")
    
    async def save_conversation(self, user_input: str, agent_response: str, metadata: Optional[Dict[str, Any]] = None):
        """
        保存对话到长期记忆
        
        Args:
            user_input: 用户输入
            agent_response: Agent响应
            metadata: 额外元数据
        """
        try:
            # 构建对话记录
            conversation = {
                "user_input": user_input,
                "agent_response": agent_response,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # 创建文档
            conversation_text = f"User: {user_input}\nAgent: {agent_response}"
            doc_metadata = {
                "type": "conversation",
                "timestamp": conversation["timestamp"],
                **conversation["metadata"]
            }
            
            # 添加到向量存储
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vectorstore.add_texts(
                    texts=[conversation_text],
                    metadatas=[doc_metadata]
                )
            )
            
            logger.debug(f"Conversation saved to memory")
            
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            raise
    
    async def save_knowledge(self, content: str, title: str, source: str = "user", metadata: Optional[Dict[str, Any]] = None):
        """
        保存知识到长期记忆
        
        Args:
            content: 知识内容
            title: 知识标题
            source: 知识来源
            metadata: 额外元数据
        """
        try:
            doc_metadata = {
                "type": "knowledge",
                "title": title,
                "source": source,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vectorstore.add_texts(
                    texts=[content],
                    metadatas=[doc_metadata]
                )
            )
            
            logger.debug(f"Knowledge '{title}' saved to memory")
            
        except Exception as e:
            logger.error(f"Failed to save knowledge: {e}")
            raise
    
    async def search_memory(self, query: str, k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        搜索相关记忆
        
        Args:
            query: 搜索查询
            k: 返回结果数量
            filter_dict: 过滤条件
            
        Returns:
            相关文档列表
        """
        try:
            # 执行相似度搜索
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vectorstore.similarity_search(
                    query=query,
                    k=k,
                    filter=filter_dict
                )
            )
            
            logger.debug(f"Found {len(results)} relevant memories for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []
    
    async def search_conversations(self, query: str, k: int = 5) -> List[Document]:
        """搜索对话记录"""
        return await self.search_memory(
            query=query,
            k=k,
            filter_dict={"type": "conversation"}
        )
    
    async def search_knowledge(self, query: str, k: int = 5) -> List[Document]:
        """搜索知识库"""
        return await self.search_memory(
            query=query,
            k=k,
            filter_dict={"type": "knowledge"}
        )
    
    async def get_recent_conversations(self, limit: int = 10) -> List[Document]:
        """获取最近的对话记录"""
        try:
            # 获取所有对话记录并按时间排序
            all_conversations = await self.search_memory(
                query="",
                k=1000,  # 获取大量结果
                filter_dict={"type": "conversation"}
            )
            
            # 按时间戳排序
            sorted_conversations = sorted(
                all_conversations,
                key=lambda x: x.metadata.get("timestamp", ""),
                reverse=True
            )
            
            return sorted_conversations[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get recent conversations: {e}")
            return []
    
    async def delete_memory(self, ids: List[str]):
        """删除指定记忆"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vectorstore.delete(ids=ids)
            )
            logger.info(f"Deleted {len(ids)} memories")
            
        except Exception as e:
            logger.error(f"Failed to delete memories: {e}")
            raise
    
    async def clear_memory(self):
        """清除所有记忆"""
        try:
            # 重新创建集合以清除所有数据
            collection = self.client.get_or_create_collection(
                name=self.config.CHROMA_COLLECTION_NAME
            )
            collection.delete()
            
            # 重新初始化向量存储
            self.vectorstore = Chroma(
                client=self.client,
                embedding_function=self.embeddings,
                collection_name=self.config.CHROMA_COLLECTION_NAME
            )
            
            logger.info("All memories cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            raise
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        try:
            collection = self.client.get_collection(
                name=self.config.CHROMA_COLLECTION_NAME
            )
            
            count = collection.count()
            
            return {
                "total_memories": count,
                "collection_name": self.config.CHROMA_COLLECTION_NAME,
                "persist_directory": self.config.CHROMA_PERSIST_DIR
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"error": str(e)}
