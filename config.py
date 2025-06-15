"""
智能多模态AI Agent系统配置文件
"""
import os

from typing import Dict, Any, Optional

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """系统配置类"""

    # 火山方舟API配置
    ARK_API_KEY: Optional[str] = os.getenv("ARK_API_KEY")
    ARK_BASE_URL: str = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    ARK_MODEL: str = os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw")

    # OpenAI兼容配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY") or os.getenv("ARK_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", os.getenv("ARK_MODEL", "ep-20250506230532-w7rdw"))
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # ChromaDB配置
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "agent_memory")

    # MCP配置
    MCP_SERVER_PATH: str = os.getenv("MCP_SERVER_PATH", "./context7_server")
    MCP_PROTOCOL_VERSION: str = os.getenv("MCP_PROTOCOL_VERSION", "2024-11-05")
    MCP_CONTEXT_LIMIT: int = int(os.getenv("MCP_CONTEXT_LIMIT", "7"))

    # 应用配置
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    SESSION_TIMEOUT: int = 7200  # 2小时
    MAX_CONCURRENT_REQUESTS: int = 5
    MAX_USERS: int = 50

    # Streamlit配置
    STREAMLIT_SERVER_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_ADDRESS: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

    # 性能配置
    RESPONSE_TIMEOUT_TEXT: int = 3  # 文本处理超时时间（秒）
    RESPONSE_TIMEOUT_IMAGE: int = 10  # 图像处理超时时间（秒）
    MEMORY_SEARCH_K: int = 5  # 记忆搜索返回结果数

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/agent.log")

    # 工具配置
    ENABLE_WEB_SEARCH: bool = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
    ENABLE_CODE_EXECUTION: bool = os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"
    ENABLE_FILE_PROCESSING: bool = os.getenv("ENABLE_FILE_PROCESSING", "true").lower() == "true"

    @classmethod


    def validate_config(cls) -> bool:
        """验证配置是否有效"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True

    @classmethod


    def get_mcp_config(cls) -> Dict[str, Any]:
        """获取MCP配置"""
        return {
            "server_name": "context7",
            "server_args": ["--context-limit", str(cls.MCP_CONTEXT_LIMIT)],
            "protocol_version": cls.MCP_PROTOCOL_VERSION,
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": True
            }
        }
