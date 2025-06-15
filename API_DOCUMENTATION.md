# 智能多模态AI Agent系统 - API文档

## 📋 API概述

### 基础信息
- **基础URL**: `http://localhost:8501/api/v1`
- **认证方式**: API Key (Header: `X-API-Key`)
- **数据格式**: JSON
- **字符编码**: UTF-8

### 响应格式
```json
{
    "success": true,
    "data": {},
    "message": "操作成功",
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid-string"
}
```

## 🚀 核心API接口

### 1. 智能对话接口

#### POST /chat
处理用户的多模态输入并返回AI响应

**请求参数:**
```json
{
    "input": {
        "type": "text|image|audio|file",
        "content": "用户输入内容或文件路径",
        "metadata": {
            "user_id": "用户ID",
            "session_id": "会话ID",
            "context": "额外上下文信息"
        }
    },
    "options": {
        "temperature": 0.7,
        "max_tokens": 4096,
        "stream": false,
        "tools": ["web_search", "document_parser"]
    }
}
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "response": "AI生成的回复内容",
        "processing_time": 2.5,
        "task_plan": {
            "steps": ["分析输入", "选择工具", "执行任务"],
            "tools_used": ["web_search"],
            "reasoning": "推理过程说明"
        },
        "metadata": {
            "tokens_used": 150,
            "model": "ep-20250506230532-w7rdw",
            "confidence": 0.95
        }
    },
    "message": "处理成功",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. 文件处理接口

#### POST /files/upload
上传并处理文件

**请求参数:**
```json
{
    "file": "multipart/form-data",
    "options": {
        "extract_text": true,
        "analyze_content": true,
        "generate_summary": false
    }
}
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "file_id": "file-uuid",
        "filename": "document.pdf",
        "size": 1024000,
        "type": "application/pdf",
        "extracted_text": "文档提取的文本内容...",
        "analysis": {
            "language": "zh-CN",
            "pages": 10,
            "word_count": 5000,
            "topics": ["AI", "技术", "发展"]
        }
    }
}
```

#### GET /files/{file_id}
获取文件信息和处理结果

**路径参数:**
- `file_id`: 文件唯一标识符

**响应示例:**
```json
{
    "success": true,
    "data": {
        "file_id": "file-uuid",
        "filename": "document.pdf",
        "status": "processed",
        "created_at": "2024-01-01T00:00:00Z",
        "processed_at": "2024-01-01T00:01:00Z",
        "results": {
            "text_content": "提取的文本...",
            "summary": "文档摘要...",
            "keywords": ["关键词1", "关键词2"]
        }
    }
}
```

### 3. 图像处理接口

#### POST /images/analyze
分析图像内容

**请求参数:**
```json
{
    "image": "base64编码的图像数据或图像URL",
    "tasks": ["describe", "ocr", "object_detection"],
    "options": {
        "language": "zh-CN",
        "detail_level": "high"
    }
}
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "description": "图像描述内容",
        "ocr_text": "图像中的文字内容",
        "objects": [
            {
                "name": "人物",
                "confidence": 0.95,
                "bbox": [100, 100, 200, 200]
            }
        ],
        "metadata": {
            "width": 1920,
            "height": 1080,
            "format": "JPEG"
        }
    }
}
```

### 4. 工具调用接口

#### POST /tools/execute
直接调用特定工具

**请求参数:**
```json
{
    "tool_name": "web_search",
    "parameters": {
        "query": "搜索关键词",
        "max_results": 5,
        "language": "zh-CN"
    },
    "options": {
        "timeout": 30,
        "cache": true
    }
}
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "tool_name": "web_search",
        "results": [
            {
                "title": "搜索结果标题",
                "url": "https://example.com",
                "snippet": "搜索结果摘要",
                "relevance": 0.9
            }
        ],
        "execution_time": 1.2,
        "cached": false
    }
}
```

#### GET /tools/list
获取可用工具列表

**响应示例:**
```json
{
    "success": true,
    "data": {
        "tools": [
            {
                "name": "web_search",
                "description": "网络搜索工具",
                "parameters": {
                    "query": "string",
                    "max_results": "integer"
                },
                "enabled": true
            },
            {
                "name": "document_parser",
                "description": "文档解析工具",
                "parameters": {
                    "file_path": "string",
                    "extract_images": "boolean"
                },
                "enabled": true
            }
        ]
    }
}
```

### 5. 记忆管理接口

#### POST /memory/search
搜索历史记忆

**请求参数:**
```json
{
    "query": "搜索查询",
    "user_id": "用户ID",
    "limit": 10,
    "filters": {
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-01-31"
        },
        "type": "conversation"
    }
}
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "results": [
            {
                "id": "memory-uuid",
                "content": "记忆内容",
                "timestamp": "2024-01-01T00:00:00Z",
                "relevance": 0.85,
                "type": "conversation",
                "metadata": {
                    "user_id": "user-123",
                    "session_id": "session-456"
                }
            }
        ],
        "total": 25,
        "page": 1,
        "per_page": 10
    }
}
```

#### DELETE /memory/{memory_id}
删除特定记忆

**路径参数:**
- `memory_id`: 记忆唯一标识符

**响应示例:**
```json
{
    "success": true,
    "message": "记忆已删除",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### 6. 系统状态接口

#### GET /health
系统健康检查

**响应示例:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": 86400,
        "components": {
            "database": "healthy",
            "llm_service": "healthy",
            "cache": "healthy",
            "tools": "healthy"
        },
        "metrics": {
            "requests_per_minute": 120,
            "average_response_time": 1.5,
            "error_rate": 0.01
        }
    }
}
```

#### GET /metrics
系统性能指标

**响应示例:**
```json
{
    "success": true,
    "data": {
        "performance": {
            "cpu_usage": 45.2,
            "memory_usage": 68.5,
            "disk_usage": 32.1,
            "network_io": {
                "bytes_sent": 1024000,
                "bytes_received": 2048000
            }
        },
        "business": {
            "total_requests": 10000,
            "successful_requests": 9950,
            "failed_requests": 50,
            "average_processing_time": 2.1
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```

## 🔒 认证和安全

### API Key认证
```bash
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8501/api/v1/chat \
     -d '{"input": {"type": "text", "content": "Hello"}}'
```

### 请求限制
- **频率限制**: 每分钟100次请求
- **文件大小**: 最大100MB
- **超时时间**: 30秒

### 安全头部
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

## 📊 错误码说明

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求格式和参数 |
| 401 | 认证失败 | 检查API Key |
| 403 | 权限不足 | 联系管理员 |
| 404 | 资源不存在 | 检查请求路径 |
| 429 | 请求过于频繁 | 降低请求频率 |
| 500 | 服务器内部错误 | 联系技术支持 |
| 503 | 服务不可用 | 稍后重试 |

## 🔧 SDK和示例

### Python SDK示例
```python
import requests

class AIAgentClient:
    def __init__(self, api_key, base_url="http://localhost:8501/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def chat(self, message, input_type="text"):
        data = {
            "input": {
                "type": input_type,
                "content": message
            }
        }
        response = requests.post(
            f"{self.base_url}/chat",
            json=data,
            headers=self.headers
        )
        return response.json()

# 使用示例
client = AIAgentClient("your-api-key")
result = client.chat("你好，请介绍一下AI的发展历程")
print(result["data"]["response"])
```

### JavaScript SDK示例
```javascript
class AIAgentClient {
    constructor(apiKey, baseUrl = 'http://localhost:8501/api/v1') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
    }
    
    async chat(message, inputType = 'text') {
        const response = await fetch(`${this.baseUrl}/chat`, {
            method: 'POST',
            headers: {
                'X-API-Key': this.apiKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                input: {
                    type: inputType,
                    content: message
                }
            })
        });
        
        return await response.json();
    }
}

// 使用示例
const client = new AIAgentClient('your-api-key');
client.chat('Hello, how are you?').then(result => {
    console.log(result.data.response);
});
```

---

*API文档版本: v1.0.0 | 最后更新: 2024-01-01*
