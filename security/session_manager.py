"""
会话状态管理系统
实现安全的会话状态管理和数据持久化
"""
import json
import hashlib
import base64
import os

from typing import Any, Dict, Optional, List

from datetime import datetime, timedelta
import streamlit as st

# 尝试导入加密模块
try:
    from cryptography.fernet import Fernet

    from cryptography.hazmat.primitives import hashes

    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class SessionManager:
    """会话管理器"""


    def __init__(self, session_timeout: int = 3600, encryption_key: str = None):
        """
        初始化会话管理器

        Args:
            session_timeout: 会话超时时间（秒）
            encryption_key: 加密密钥
        """
        self.session_timeout = session_timeout
        self.crypto_available = CRYPTO_AVAILABLE

        if self.crypto_available:
            self.encryption_key = encryption_key or self._generate_encryption_key()
            self.cipher_suite = self._setup_encryption()
        else:
            self.encryption_key = None
            self.cipher_suite = None

        # 会话存储
        self.active_sessions = {}
        self.session_data = {}

        # 敏感数据字段
        self.sensitive_fields = {
            'api_key', 'password', 'token', 'secret', 'private_key',
            'access_token', 'refresh_token', 'session_key'
        }


    def _generate_encryption_key(self) -> str:
        """生成加密密钥"""
        if not CRYPTO_AVAILABLE:
            return "simple_key_no_crypto"

        # 使用环境变量或生成新密钥
        key = os.getenv('SESSION_ENCRYPTION_KEY')
        if not key:
            # 生成新密钥（在生产环境中应该从安全存储中获取）
            password = b"default_session_key_change_in_production"
            salt = b"salt_1234567890123456"  # 在生产环境中应该是随机的
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))

        return key


    def _setup_encryption(self):
        """设置加密套件"""
        if not CRYPTO_AVAILABLE:
            return None

        if isinstance(self.encryption_key, str):
            key = self.encryption_key.encode()
        else:
            key = self.encryption_key

        return Fernet(key)


    def create_session(self, user_id: str = None) -> str:
        """
        创建新会话

        Args:
            user_id: 用户ID

        Returns:
            会话ID
        """
        session_id = self._generate_session_id()

        session_info = {
            'session_id': session_id,
            'user_id': user_id or 'anonymous',
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'ip_address': self._get_client_ip(),
            'user_agent': self._get_user_agent(),
            'is_active': True
        }

        self.active_sessions[session_id] = session_info
        self.session_data[session_id] = {}

        # 设置到Streamlit session state
        st.session_state.session_id = session_id
        st.session_state.session_created_at = session_info['created_at']

        return session_id


    def get_session_id(self) -> str:
        """获取当前会话ID"""
        if 'session_id' not in st.session_state:
            return self.create_session()

        session_id = st.session_state.session_id

        # 验证会话是否有效
        if not self.is_session_valid(session_id):
            return self.create_session()

        # 更新最后活动时间
        self._update_last_activity(session_id)

        return session_id


    def is_session_valid(self, session_id: str) -> bool:
        """检查会话是否有效"""
        if session_id not in self.active_sessions:
            return False

        session_info = self.active_sessions[session_id]

        # 检查会话是否过期
        last_activity = datetime.fromisoformat(session_info['last_activity'])
        if datetime.now() - last_activity > timedelta(seconds=self.session_timeout):
            self.invalidate_session(session_id)
            return False

        return session_info.get('is_active', False)


    def invalidate_session(self, session_id: str):
        """使会话失效"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['is_active'] = False
            self.active_sessions[session_id]['invalidated_at'] = datetime.now().isoformat()

        # 清理敏感数据
        if session_id in self.session_data:
            self._clear_sensitive_data(session_id)


    def store_data(self, key: str, value: Any, encrypt: bool = None) -> bool:
        """
        存储会话数据

        Args:
            key: 数据键
            value: 数据值
            encrypt: 是否加密（自动检测敏感数据）

        Returns:
            是否存储成功
        """
        session_id = self.get_session_id()

        if session_id not in self.session_data:
            self.session_data[session_id] = {}

        # 自动检测是否需要加密
        if encrypt is None:
            encrypt = self._is_sensitive_data(key, value)

        try:
            if encrypt and self.crypto_available and self.cipher_suite:
                # 加密存储
                serialized_value = json.dumps(value, ensure_ascii=False)
                encrypted_value = self.cipher_suite.encrypt(serialized_value.encode())
                self.session_data[session_id][key] = {
                    'encrypted': True,
                    'value': base64.b64encode(encrypted_value).decode()
                }
            else:
                # 明文存储（或加密不可用时的回退）
                self.session_data[session_id][key] = {
                    'encrypted': False,
                    'value': value
                }

            # 同时存储到Streamlit session state
            st.session_state[key] = value

            return True
        except Exception:
            return False


    def retrieve_data(self, key: str, default: Any = None) -> Any:
        """
        检索会话数据

        Args:
            key: 数据键
            default: 默认值

        Returns:
            数据值
        """
        session_id = self.get_session_id()

        if session_id not in self.session_data:
            return default

        if key not in self.session_data[session_id]:
            return default

        try:
            data_entry = self.session_data[session_id][key]

            if data_entry['encrypted'] and self.crypto_available and self.cipher_suite:
                # 解密数据
                encrypted_value = base64.b64decode(data_entry['value'])
                decrypted_value = self.cipher_suite.decrypt(encrypted_value)
                return json.loads(decrypted_value.decode())
            else:
                # 明文数据
                return data_entry['value']
        except Exception:
            return default


    def remove_data(self, key: str) -> bool:
        """
        移除会话数据

        Args:
            key: 数据键

        Returns:
            是否移除成功
        """
        session_id = self.get_session_id()

        if session_id in self.session_data and key in self.session_data[session_id]:
            del self.session_data[session_id][key]

            # 同时从Streamlit session state移除
            if key in st.session_state:
                del st.session_state[key]

            return True

        return False


    def get_session_info(self, session_id: str = None) -> Dict[str, Any]:
        """获取会话信息"""
        if session_id is None:
            session_id = self.get_session_id()

        if session_id not in self.active_sessions:
            return {}

        session_info = self.active_sessions[session_id].copy()

        # 添加数据统计
        data_count = len(self.session_data.get(session_id, {}))
        encrypted_count = sum(
            1 for item in self.session_data.get(session_id, {}).values()
            if item.get('encrypted', False)
        )

        session_info.update({
            'data_count': data_count,
            'encrypted_data_count': encrypted_count,
            'session_age_seconds': self._get_session_age(session_id)
        })

        return session_info


    def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        expired_sessions = []
        current_time = datetime.now()

        for session_id, session_info in self.active_sessions.items():
            last_activity = datetime.fromisoformat(session_info['last_activity'])
            if current_time - last_activity > timedelta(seconds=self.session_timeout):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            self.invalidate_session(session_id)
            if session_id in self.session_data:
                del self.session_data[session_id]

        return len(expired_sessions)


    def _generate_session_id(self) -> str:
        """生成会话ID"""
        timestamp = datetime.now().isoformat()
        random_data = os.urandom(16)
        session_data = f"{timestamp}_{random_data.hex()}"
        return hashlib.sha256(session_data.encode()).hexdigest()[:32]


    def _update_last_activity(self, session_id: str):
        """更新最后活动时间"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['last_activity'] = datetime.now().isoformat()


    def _is_sensitive_data(self, key: str, value: Any) -> bool:
        """检查是否为敏感数据"""
        key_lower = key.lower()

        # 检查键名
        for sensitive_field in self.sensitive_fields:
            if sensitive_field in key_lower:
                return True

        # 检查值内容（如果是字符串）
        if isinstance(value, str):
            value_lower = value.lower()
            for sensitive_field in self.sensitive_fields:
                if sensitive_field in value_lower:
                    return True

        return False


    def _clear_sensitive_data(self, session_id: str):
        """清理敏感数据"""
        if session_id not in self.session_data:
            return

        keys_to_remove = []
        for key, data_entry in self.session_data[session_id].items():
            if data_entry.get('encrypted', False) or self._is_sensitive_data(key, data_entry.get('value')):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.session_data[session_id][key]


    def _get_session_age(self, session_id: str) -> int:
        """获取会话年龄（秒）"""
        if session_id not in self.active_sessions:
            return 0

        created_at = datetime.fromisoformat(self.active_sessions[session_id]['created_at'])
        return int((datetime.now() - created_at).total_seconds())


    def _get_client_ip(self) -> str:
        """获取客户端IP（在Streamlit中可能无法获取真实IP）"""
        return "unknown"


    def _get_user_agent(self) -> str:
        """获取用户代理"""
        return "streamlit_app"

# 全局实例
session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """获取会话管理器实例"""
    return session_manager
