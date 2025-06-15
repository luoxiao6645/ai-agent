"""
API密钥和敏感信息安全处理系统
加强API密钥和其他敏感信息的安全处理
"""
import os
import re
import hashlib
import base64

from typing import Dict, List, Optional, Tuple, Any

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


class SecretsManager:
    """敏感信息管理器"""


    def __init__(self):
        """初始化敏感信息管理器"""
        self.crypto_available = CRYPTO_AVAILABLE

        if self.crypto_available:
            self.encryption_key = self._get_or_create_encryption_key()
            self.cipher_suite = Fernet(self.encryption_key)
        else:
            self.encryption_key = None
            self.cipher_suite = None

        # 敏感信息模式
        self.sensitive_patterns = [
            r'api[_-]?key',
            r'secret[_-]?key',
            r'access[_-]?token',
            r'refresh[_-]?token',
            r'private[_-]?key',
            r'password',
            r'passwd',
            r'auth[_-]?token',
            r'bearer[_-]?token',
            r'session[_-]?key',
            r'client[_-]?secret'
        ]

        # API密钥验证规则
        self.api_key_rules = {
            'min_length': 16,
            'max_length': 256,
            'required_entropy': 3.0,  # 最小熵值
            'forbidden_patterns': ['password', '123456', 'qwerty', 'admin']
        }

        # 密钥轮转配置
        self.key_rotation_config = {
            'rotation_interval_days': 90,
            'warning_days_before_expiry': 7,
            'max_key_age_days': 365
        }

        # 访问控制
        self.access_permissions = {}
        self.access_log = []


    def _get_or_create_encryption_key(self) -> bytes:
        """获取或创建加密密钥"""
        if not CRYPTO_AVAILABLE:
            return b"simple_key_no_crypto"

        # 尝试从环境变量获取
        env_key = os.getenv('SECRETS_ENCRYPTION_KEY')
        if env_key:
            return base64.urlsafe_b64decode(env_key)

        # 尝试从Streamlit secrets获取
        try:
            if hasattr(st, 'secrets') and 'SECRETS_ENCRYPTION_KEY' in st.secrets:
                return base64.urlsafe_b64decode(st.secrets['SECRETS_ENCRYPTION_KEY'])
        except:
            pass

        # 生成新密钥（开发环境）
        password = b"default_secrets_key_change_in_production"
        salt = b"secrets_salt_1234567890123456"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))


    def validate_api_key(self, api_key: str, key_type: str = "general") -> Tuple[bool, List[str]]:
        """
        验证API密钥

        Args:
            api_key: API密钥
            key_type: 密钥类型

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []

        if not api_key:
            errors.append("API密钥不能为空")
            return False, errors

        # 长度检查
        if len(api_key) < self.api_key_rules['min_length']:
            errors.append(f"API密钥长度不能少于{self.api_key_rules['min_length']}字符")

        if len(api_key) > self.api_key_rules['max_length']:
            errors.append(f"API密钥长度不能超过{self.api_key_rules['max_length']}字符")

        # 熵值检查
        entropy = self._calculate_entropy(api_key)
        if entropy < self.api_key_rules['required_entropy']:
            errors.append(f"API密钥复杂度不足（熵值: {entropy:.2f}，要求: {self.api_key_rules['required_entropy']}）")

        # 禁用模式检查
        for pattern in self.api_key_rules['forbidden_patterns']:
            if pattern.lower() in api_key.lower():
                errors.append(f"API密钥包含禁用模式: {pattern}")

        # 格式检查（根据密钥类型）
        if key_type == "openai" and not api_key.startswith("sk-"):
            errors.append("OpenAI API密钥应以'sk-'开头")

        return len(errors) == 0, errors


    def store_secret(self, key: str, value: str, description: str = "",
                    expiry_days: int = None) -> bool:
        """
        安全存储敏感信息

        Args:
            key: 密钥名称
            value: 密钥值
            description: 描述
            expiry_days: 过期天数

        Returns:
            是否存储成功
        """
        try:
            # 验证密钥值
            is_valid, errors = self.validate_api_key(value)
            if not is_valid:
                self._log_access("store_secret", key, False, f"Validation failed: {errors}")
                return False

            # 加密存储（如果可用）
            if self.crypto_available and self.cipher_suite:
                encrypted_value = self.cipher_suite.encrypt(value.encode())
                encrypted_data = base64.b64encode(encrypted_value).decode()
            else:
                # 简单编码（非加密）
                encrypted_data = base64.b64encode(value.encode()).decode()

            # 构建存储数据
            secret_data = {
                'encrypted_value': encrypted_data,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'last_accessed': None,
                'access_count': 0,
                'expiry_date': (datetime.now() + timedelta(days=expiry_days)).isoformat() if expiry_days else None,
                'key_hash': hashlib.sha256(value.encode()).hexdigest()[:16]  # 用于验证
            }

            # 存储到session state（加密）
            if 'encrypted_secrets' not in st.session_state:
                st.session_state.encrypted_secrets = {}

            st.session_state.encrypted_secrets[key] = secret_data

            self._log_access("store_secret", key, True, "Secret stored successfully")
            return True

        except Exception as e:
            self._log_access("store_secret", key, False, f"Storage failed: {str(e)}")
            return False


    def retrieve_secret(self, key: str, mask_in_logs: bool = True) -> Optional[str]:
        """
        检索敏感信息

        Args:
            key: 密钥名称
            mask_in_logs: 是否在日志中掩码

        Returns:
            解密后的密钥值
        """
        try:
            if 'encrypted_secrets' not in st.session_state:
                self._log_access("retrieve_secret", key, False, "No secrets storage found")
                return None

            if key not in st.session_state.encrypted_secrets:
                self._log_access("retrieve_secret", key, False, "Secret not found")
                return None

            secret_data = st.session_state.encrypted_secrets[key]

            # 检查是否过期
            if secret_data.get('expiry_date'):
                expiry_date = datetime.fromisoformat(secret_data['expiry_date'])
                if datetime.now() > expiry_date:
                    self._log_access("retrieve_secret", key, False, "Secret expired")
                    return None

            # 解密
            encrypted_value = base64.b64decode(secret_data['encrypted_value'])
            if self.crypto_available and self.cipher_suite:
                decrypted_value = self.cipher_suite.decrypt(encrypted_value).decode()
            else:
                # 简单解码（非解密）
                decrypted_value = encrypted_value.decode()

            # 更新访问信息
            secret_data['last_accessed'] = datetime.now().isoformat()
            secret_data['access_count'] = secret_data.get('access_count', 0) + 1

            log_value = "***MASKED***" if mask_in_logs else decrypted_value[:8] + "..."
            self._log_access("retrieve_secret", key, True, f"Secret retrieved: {log_value}")

            return decrypted_value

        except Exception as e:
            self._log_access("retrieve_secret", key, False, f"Retrieval failed: {str(e)}")
            return None


    def delete_secret(self, key: str) -> bool:
        """
        删除敏感信息

        Args:
            key: 密钥名称

        Returns:
            是否删除成功
        """
        try:
            if 'encrypted_secrets' not in st.session_state:
                return False

            if key in st.session_state.encrypted_secrets:
                del st.session_state.encrypted_secrets[key]
                self._log_access("delete_secret", key, True, "Secret deleted")
                return True

            return False

        except Exception as e:
            self._log_access("delete_secret", key, False, f"Deletion failed: {str(e)}")
            return False


    def list_secrets(self) -> List[Dict[str, Any]]:
        """列出所有存储的敏感信息（不包含值）"""
        if 'encrypted_secrets' not in st.session_state:
            return []

        secrets_info = []
        for key, secret_data in st.session_state.encrypted_secrets.items():
            info = {
                'key': key,
                'description': secret_data.get('description', ''),
                'created_at': secret_data.get('created_at'),
                'last_accessed': secret_data.get('last_accessed'),
                'access_count': secret_data.get('access_count', 0),
                'expiry_date': secret_data.get('expiry_date'),
                'is_expired': self._is_secret_expired(secret_data),
                'days_until_expiry': self._days_until_expiry(secret_data)
            }
            secrets_info.append(info)

        return secrets_info


    def check_secret_expiry(self) -> List[Dict[str, Any]]:
        """检查即将过期的密钥"""
        expiring_secrets = []
        warning_days = self.key_rotation_config['warning_days_before_expiry']

        for key, secret_data in st.session_state.get('encrypted_secrets', {}).items():
            if secret_data.get('expiry_date'):
                days_until_expiry = self._days_until_expiry(secret_data)
                if 0 <= days_until_expiry <= warning_days:
                    expiring_secrets.append({
                        'key': key,
                        'days_until_expiry': days_until_expiry,
                        'expiry_date': secret_data['expiry_date']
                    })

        return expiring_secrets


    def mask_sensitive_data(self, text: str) -> str:
        """掩码文本中的敏感信息"""
        masked_text = text

        for pattern in self.sensitive_patterns:
            # 查找敏感信息模式
            regex = re.compile(f'{pattern}[\\s]*[=:][\\s]*([\\w\\-_]+)', re.IGNORECASE)
            masked_text = regex.sub(lambda m: f"{m.group(0).split('=')[0]}=***MASKED***", masked_text)

        return masked_text


    def _calculate_entropy(self, text: str) -> float:
        """计算文本熵值"""
        if not text:
            return 0.0

        # 计算字符频率
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1

        # 计算熵
        import math

        entropy = 0.0
        text_length = len(text)

        for count in char_counts.values():
            probability = count / text_length
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy


    def _is_secret_expired(self, secret_data: Dict[str, Any]) -> bool:
        """检查密钥是否过期"""
        expiry_date = secret_data.get('expiry_date')
        if not expiry_date:
            return False

        return datetime.now() > datetime.fromisoformat(expiry_date)


    def _days_until_expiry(self, secret_data: Dict[str, Any]) -> Optional[int]:
        """计算距离过期的天数"""
        expiry_date = secret_data.get('expiry_date')
        if not expiry_date:
            return None

        expiry_datetime = datetime.fromisoformat(expiry_date)
        days_diff = (expiry_datetime - datetime.now()).days

        return max(0, days_diff)


    def _log_access(self, operation: str, key: str, success: bool, details: str):
        """记录访问日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'key': key,
            'success': success,
            'details': details,
            'session_id': st.session_state.get('session_id', 'unknown')
        }

        self.access_log.append(log_entry)

        # 保持日志大小
        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-500:]


    def get_access_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取访问日志"""
        return self.access_log[-limit:]


    def get_security_summary(self) -> Dict[str, Any]:
        """获取安全摘要"""
        secrets_count = len(st.session_state.get('encrypted_secrets', {}))
        expiring_secrets = self.check_secret_expiry()

        return {
            'total_secrets': secrets_count,
            'expiring_secrets_count': len(expiring_secrets),
            'total_access_attempts': len(self.access_log),
            'failed_access_attempts': sum(1 for log in self.access_log if not log['success']),
            'expiring_secrets': expiring_secrets
        }

# 全局实例
secrets_manager = SecretsManager()


def get_secrets_manager() -> SecretsManager:
    """获取敏感信息管理器实例"""
    return secrets_manager
