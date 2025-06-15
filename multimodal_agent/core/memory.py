"""
记忆管理系统
"""
import asyncio
import logging

from typing import List, Dict, Any, Optional

from datetime import datetime

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

    async def save_conversation(self, user_input: str, ai_response: str, session_id: str = None, metadata: Optional[Dict[str, Any]] = None):
        """
        保存对话到长期记忆 - 增强版

        Args:
            user_input: 用户输入
            ai_response: AI响应
            session_id: 会话ID
            metadata: 额外元数据
        """
        try:
            # 构建对话记录
            conversation = {
                "user_input": user_input,
                "ai_response": ai_response,
                "session_id": session_id or "default",
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }

            # 创建文档
            conversation_text = f"User: {user_input}\nAssistant: {ai_response}"
            doc_metadata = {
                "type": "conversation",
                "session_id": conversation["session_id"],
                "timestamp": conversation["timestamp"],
                "user_input_length": len(user_input),
                "ai_response_length": len(ai_response),
                **conversation["metadata"]
            }

            # 提取关键信息
            keywords = await self._extract_keywords(conversation_text)
            if keywords:
                doc_metadata["keywords"] = keywords

            # 添加到向量存储
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vectorstore.add_texts(
                    texts=[conversation_text],
                    metadatas=[doc_metadata]
                )
            )

            logger.debug(f"Conversation saved to memory for session {session_id}")

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
        """获取记忆统计信息 - 增强版"""
        try:
            collection = self.client.get_collection(
                name=self.config.CHROMA_COLLECTION_NAME
            )

            count = collection.count()

            # 获取详细统计信息
            stats = {
                "total_memories": count,
                "collection_name": self.config.CHROMA_COLLECTION_NAME,
                "persist_directory": self.config.CHROMA_PERSIST_DIR,
                "memory_types": {},
                "sessions": set(),
                "date_range": {"oldest": None, "newest": None}
            }

            # 获取样本数据进行详细分析
            try:
                sample_results = collection.get(limit=min(1000, count))

                if sample_results and sample_results.get("metadatas"):
                    for metadata in sample_results["metadatas"]:
                        # 统计记忆类型
                        memory_type = metadata.get("type", "unknown")
                        stats["memory_types"][memory_type] = stats["memory_types"].get(memory_type, 0) + 1

                        # 统计会话
                        session_id = metadata.get("session_id")
                        if session_id:
                            stats["sessions"].add(session_id)

                        # 统计时间范围
                        timestamp = metadata.get("timestamp")
                        if timestamp:
                            if not stats["date_range"]["oldest"] or timestamp < stats["date_range"]["oldest"]:
                                stats["date_range"]["oldest"] = timestamp
                            if not stats["date_range"]["newest"] or timestamp > stats["date_range"]["newest"]:
                                stats["date_range"]["newest"] = timestamp

                stats["total_sessions"] = len(stats["sessions"])
                stats["sessions"] = list(stats["sessions"])  # 转换为列表以便JSON序列化

            except Exception as detail_error:
                logger.warning(f"Failed to get detailed stats: {detail_error}")

            return stats

        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"error": str(e)}

    async def clear_session_memory(self, session_id: str):
        """清除特定会话的记忆"""
        try:
            # 搜索该会话的所有记忆
            session_memories = await self.search_memory(
                query="",
                k=1000,
                filter_dict={"session_id": session_id}
            )

            if session_memories:
                # 提取ID并删除
                memory_ids = [doc.metadata.get("id") for doc in session_memories if doc.metadata.get("id")]
                if memory_ids:
                    await self.delete_memory(memory_ids)
                    logger.info(f"Cleared {len(memory_ids)} memories for session {session_id}")
                else:
                    logger.warning(f"No memory IDs found for session {session_id}")
            else:
                logger.info(f"No memories found for session {session_id}")

        except Exception as e:
            logger.error(f"Failed to clear session memory: {e}")
            raise

    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话摘要"""
        try:
            # 获取会话的所有对话
            conversations = await self.search_memory(
                query="",
                k=100,
                filter_dict={"session_id": session_id, "type": "conversation"}
            )

            if not conversations:
                return {
                    "session_id": session_id,
                    "message_count": 0,
                    "summary": "暂无对话记录",
                    "topics": [],
                    "duration": None
                }

            # 分析对话内容
            all_content = " ".join([doc.page_content for doc in conversations])
            topics = await self._extract_topics_from_content(all_content)

            # 计算时间跨度
            timestamps = [doc.metadata.get("timestamp") for doc in conversations if doc.metadata.get("timestamp")]
            duration = None
            if len(timestamps) > 1:
                timestamps.sort()
                start_time = datetime.fromisoformat(timestamps[0].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(timestamps[-1].replace('Z', '+00:00'))
                duration = str(end_time - start_time)

            return {
                "session_id": session_id,
                "message_count": len(conversations),
                "summary": f"包含{len(conversations)}条对话，主要讨论了{', '.join(topics[:3])}等话题",
                "topics": topics,
                "duration": duration,
                "first_message": timestamps[0] if timestamps else None,
                "last_message": timestamps[-1] if timestamps else None
            }

        except Exception as e:
            logger.error(f"Failed to get session summary: {e}")
            return {"session_id": session_id, "error": str(e)}

    async def _extract_topics_from_content(self, content: str) -> List[str]:
        """从内容中提取主题"""
        try:
            # 简单的主题提取
            import re

            # 常见主题关键词
            topic_keywords = {
                "技术": ["技术", "编程", "代码", "开发", "软件", "算法", "数据库"],
                "学习": ["学习", "教育", "知识", "理解", "解释", "教学"],
                "工作": ["工作", "项目", "任务", "业务", "公司", "团队"],
                "生活": ["生活", "日常", "个人", "家庭", "健康", "娱乐"],
                "创作": ["写作", "创作", "设计", "艺术", "创意", "文章"],
                "分析": ["分析", "数据", "统计", "报告", "研究", "调查"],
                "问题解决": ["问题", "解决", "帮助", "建议", "方案", "答案"]
            }

            detected_topics = []
            content_lower = content.lower()

            for topic, keywords in topic_keywords.items():
                keyword_count = sum(1 for keyword in keywords if keyword in content_lower)
                if keyword_count >= 2:  # 至少匹配2个关键词
                    detected_topics.append(topic)

            return detected_topics if detected_topics else ["通用对话"]

        except Exception as e:
            logger.warning(f"Topic extraction failed: {e}")
            return ["通用对话"]

    async def backup_memory(self, backup_path: str) -> bool:
        """备份记忆数据"""
        try:
            import json

            import os

            # 获取所有记忆数据
            all_memories = await self.search_memory(query="", k=10000)

            backup_data = {
                "backup_timestamp": datetime.now().isoformat(),
                "total_memories": len(all_memories),
                "memories": []
            }

            for doc in all_memories:
                backup_data["memories"].append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })

            # 确保备份目录存在
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)

            # 写入备份文件
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Memory backup completed: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Memory backup failed: {e}")
            return False

    async def restore_memory(self, backup_path: str) -> bool:
        """恢复记忆数据"""
        try:
            import json

            # 读取备份文件
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            memories = backup_data.get("memories", [])

            # 批量恢复记忆
            texts = [memory["content"] for memory in memories]
            metadatas = [memory["metadata"] for memory in memories]

            if texts:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
                )

            logger.info(f"Memory restore completed: {len(memories)} memories restored")
            return True

        except Exception as e:
            logger.error(f"Memory restore failed: {e}")
            return False
