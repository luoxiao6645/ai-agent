"""
代码执行工具
"""
import asyncio
import logging
import sys
import io
import contextlib
from typing import Optional, Type, Dict, Any
import subprocess
import tempfile
import os

from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class CodeExecutorInput(BaseModel):
    """代码执行输入模型"""
    code: str = Field(description="要执行的代码")
    language: str = Field(default="python", description="编程语言: python, javascript, bash")
    timeout: int = Field(default=30, description="执行超时时间（秒）")

class CodeExecutorTool(BaseTool):
    """代码执行工具 - 安全的代码执行环境"""
    
    name = "code_executor"
    description = "在安全环境中执行Python、JavaScript或Bash代码"
    args_schema: Type[BaseModel] = CodeExecutorInput
    
    def __init__(self):
        super().__init__()
        self.allowed_languages = ["python", "javascript", "bash"]
        self.restricted_imports = [
            "os", "subprocess", "sys", "shutil", "glob",
            "socket", "urllib", "requests", "http"
        ]
    
    def _run(self, code: str, language: str = "python", timeout: int = 30) -> str:
        """同步执行代码"""
        return asyncio.run(self._arun(code, language, timeout))
    
    async def _arun(self, code: str, language: str = "python", timeout: int = 30) -> str:
        """异步执行代码"""
        try:
            # 验证语言支持
            if language not in self.allowed_languages:
                return f"不支持的编程语言: {language}"
            
            # 安全检查
            if not self._is_code_safe(code, language):
                return "代码包含不安全的操作，执行被拒绝"
            
            # 根据语言执行代码
            if language == "python":
                return await self._execute_python(code, timeout)
            elif language == "javascript":
                return await self._execute_javascript(code, timeout)
            elif language == "bash":
                return await self._execute_bash(code, timeout)
            else:
                return f"语言 {language} 的执行器未实现"
                
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return f"代码执行失败: {str(e)}"
    
    def _is_code_safe(self, code: str, language: str) -> bool:
        """检查代码安全性"""
        if language == "python":
            # 检查危险的导入和操作
            dangerous_patterns = [
                "import os", "from os", "__import__",
                "exec(", "eval(", "compile(",
                "open(", "file(", "input(",
                "subprocess", "system(", "popen(",
                "socket", "urllib", "requests",
                "shutil", "glob", "sys.exit"
            ]
            
            code_lower = code.lower()
            for pattern in dangerous_patterns:
                if pattern in code_lower:
                    logger.warning(f"Dangerous pattern detected: {pattern}")
                    return False
        
        elif language == "bash":
            # Bash命令安全检查
            dangerous_commands = [
                "rm ", "del ", "format", "fdisk",
                "sudo", "su ", "chmod", "chown",
                "wget", "curl", "nc ", "netcat",
                ">/", ">>/"
            ]
            
            code_lower = code.lower()
            for cmd in dangerous_commands:
                if cmd in code_lower:
                    logger.warning(f"Dangerous command detected: {cmd}")
                    return False
        
        return True
    
    async def _execute_python(self, code: str, timeout: int) -> str:
        """执行Python代码"""
        try:
            # 创建受限的执行环境
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'reversed': reversed
                },
                'math': __import__('math'),
                'random': __import__('random'),
                'datetime': __import__('datetime'),
                'json': __import__('json')
            }
            
            # 捕获输出
            output_buffer = io.StringIO()
            
            with contextlib.redirect_stdout(output_buffer):
                with contextlib.redirect_stderr(output_buffer):
                    # 执行代码
                    exec(code, restricted_globals)
            
            result = output_buffer.getvalue()
            
            if not result.strip():
                result = "代码执行完成，无输出"
            
            return f"Python代码执行结果:\n{result}"
            
        except Exception as e:
            return f"Python代码执行错误: {str(e)}"
    
    async def _execute_javascript(self, code: str, timeout: int) -> str:
        """执行JavaScript代码"""
        try:
            # 检查是否安装了Node.js
            try:
                subprocess.run(["node", "--version"], 
                             capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return "JavaScript执行需要安装Node.js"
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # 执行JavaScript代码
                result = subprocess.run(
                    ["node", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                if result.returncode == 0:
                    output = result.stdout
                    if not output.strip():
                        output = "代码执行完成，无输出"
                    return f"JavaScript代码执行结果:\n{output}"
                else:
                    return f"JavaScript代码执行错误:\n{result.stderr}"
                    
            finally:
                # 清理临时文件
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return f"JavaScript代码执行超时（{timeout}秒）"
        except Exception as e:
            return f"JavaScript代码执行失败: {str(e)}"
    
    async def _execute_bash(self, code: str, timeout: int) -> str:
        """执行Bash命令"""
        try:
            # 执行bash命令
            result = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                output = result.stdout
                if not output.strip():
                    output = "命令执行完成，无输出"
                return f"Bash命令执行结果:\n{output}"
            else:
                return f"Bash命令执行错误:\n{result.stderr}"
                
        except subprocess.TimeoutExpired:
            return f"Bash命令执行超时（{timeout}秒）"
        except Exception as e:
            return f"Bash命令执行失败: {str(e)}"
    
    def get_supported_languages(self) -> list:
        """获取支持的编程语言"""
        return self.allowed_languages.copy()
    
    async def test_environment(self) -> Dict[str, Any]:
        """测试执行环境"""
        results = {}
        
        # 测试Python
        python_code = "print('Python环境正常')"
        python_result = await self._execute_python(python_code, 10)
        results["python"] = {
            "available": "Python环境正常" in python_result,
            "result": python_result
        }
        
        # 测试JavaScript
        js_code = "console.log('JavaScript环境正常');"
        js_result = await self._execute_javascript(js_code, 10)
        results["javascript"] = {
            "available": "JavaScript环境正常" in js_result,
            "result": js_result
        }
        
        # 测试Bash
        bash_code = "echo 'Bash环境正常'"
        bash_result = await self._execute_bash(bash_code, 10)
        results["bash"] = {
            "available": "Bash环境正常" in bash_result,
            "result": bash_result
        }
        
        return results
