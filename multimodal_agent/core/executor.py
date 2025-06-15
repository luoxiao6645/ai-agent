"""
任务执行器
"""
import asyncio
import logging

from typing import Dict, Any, List, Optional

from datetime import datetime

logger = logging.getLogger(__name__)


class TaskExecutor:
    """任务执行器 - 执行规划好的任务步骤"""


    def __init__(self, tool_manager):
        """初始化任务执行器"""
        self.tool_manager = tool_manager
        self.execution_history = []

        logger.info("TaskExecutor initialized")

    async def execute_plan(self, plan: Dict[str, Any]) -> str:
        """
        执行任务计划

        Args:
            plan: 任务执行计划

        Returns:
            执行结果
        """
        try:
            start_time = datetime.now()

            # 记录执行开始
            execution_id = self._generate_execution_id()
            self._log_execution_start(execution_id, plan)

            # 执行步骤
            if plan.get("steps"):
                result = await self._execute_steps(plan["steps"])
            else:
                result = await self._execute_simple_task(plan)

            # 记录执行完成
            execution_time = (datetime.now() - start_time).total_seconds()
            self._log_execution_complete(execution_id, result, execution_time)

            return result

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            # 尝试执行备选方案
            if plan.get("fallback_plan"):
                return await self._execute_fallback(plan["fallback_plan"])
            else:
                return f"任务执行失败: {str(e)}"

    async def _execute_steps(self, steps: List[Dict[str, Any]]) -> str:
        """执行多个步骤"""
        results = []
        context = {}

        for step in steps:
            try:
                step_result = await self._execute_single_step(step, context)
                results.append(f"步骤{step['step']}: {step_result}")

                # 更新上下文
                context[f"step_{step['step']}_result"] = step_result

            except Exception as e:
                error_msg = f"步骤{step['step']}执行失败: {str(e)}"
                results.append(error_msg)
                logger.error(error_msg)

        return "\n".join(results)

    async def _execute_single_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> str:
        """执行单个步骤"""
        action = step.get("action", "")
        parameters = step.get("parameters", {})

        # 替换参数中的上下文变量
        parameters = self._resolve_parameters(parameters, context)

        # 根据动作类型执行
        if action.startswith("web_search"):
            return await self._execute_web_search(parameters)
        elif action.startswith("code_executor"):
            return await self._execute_code(parameters)
        elif action.startswith("data_analyzer"):
            return await self._execute_data_analysis(parameters)
        elif action.startswith("image_processor"):
            return await self._execute_image_processing(parameters)
        elif action.startswith("file_manager"):
            return await self._execute_file_operation(parameters)
        else:
            # 通用工具执行
            return await self._execute_generic_tool(action, parameters)

    async def _execute_simple_task(self, plan: Dict[str, Any]) -> str:
        """执行简单任务"""
        query = plan.get("query", "")

        # 简单任务直接返回查询结果
        return f"已处理请求: {query}"

    async def _execute_web_search(self, parameters: Dict[str, Any]) -> str:
        """执行网络搜索"""
        try:
            search_tool = self.tool_manager.get_tool("web_search")
            if search_tool:
                query = parameters.get("query", "")
                result = await search_tool.arun(query)
                return f"搜索结果: {result}"
            else:
                return "网络搜索工具不可用"
        except Exception as e:
            return f"搜索失败: {str(e)}"

    async def _execute_code(self, parameters: Dict[str, Any]) -> str:
        """执行代码"""
        try:
            code_tool = self.tool_manager.get_tool("code_executor")
            if code_tool:
                code = parameters.get("code", "")
                result = await code_tool.arun(code)
                return f"代码执行结果: {result}"
            else:
                return "代码执行工具不可用"
        except Exception as e:
            return f"代码执行失败: {str(e)}"

    async def _execute_data_analysis(self, parameters: Dict[str, Any]) -> str:
        """执行数据分析"""
        try:
            analysis_tool = self.tool_manager.get_tool("data_analyzer")
            if analysis_tool:
                data = parameters.get("data", "")
                analysis_type = parameters.get("type", "basic")
                result = await analysis_tool.arun(f"{analysis_type}: {data}")
                return f"数据分析结果: {result}"
            else:
                return "数据分析工具不可用"
        except Exception as e:
            return f"数据分析失败: {str(e)}"

    async def _execute_image_processing(self, parameters: Dict[str, Any]) -> str:
        """执行图像处理"""
        try:
            image_tool = self.tool_manager.get_tool("image_processor")
            if image_tool:
                image_path = parameters.get("image_path", "")
                operation = parameters.get("operation", "analyze")
                result = await image_tool.arun(f"{operation}: {image_path}")
                return f"图像处理结果: {result}"
            else:
                return "图像处理工具不可用"
        except Exception as e:
            return f"图像处理失败: {str(e)}"

    async def _execute_file_operation(self, parameters: Dict[str, Any]) -> str:
        """执行文件操作"""
        try:
            file_tool = self.tool_manager.get_tool("file_manager")
            if file_tool:
                operation = parameters.get("operation", "read")
                file_path = parameters.get("file_path", "")
                result = await file_tool.arun(f"{operation}: {file_path}")
                return f"文件操作结果: {result}"
            else:
                return "文件管理工具不可用"
        except Exception as e:
            return f"文件操作失败: {str(e)}"

    async def _execute_generic_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """执行通用工具"""
        try:
            tool = self.tool_manager.get_tool(tool_name)
            if tool:
                # 构建工具输入
                tool_input = parameters.get("input", str(parameters))
                result = await tool.arun(tool_input)
                return f"{tool_name}执行结果: {result}"
            else:
                return f"工具 {tool_name} 不可用"
        except Exception as e:
            return f"工具执行失败: {str(e)}"


    def _resolve_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """解析参数中的上下文变量"""
        resolved = {}

        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # 解析上下文变量
                var_name = value[2:-1]
                resolved[key] = context.get(var_name, value)
            else:
                resolved[key] = value

        return resolved

    async def _execute_fallback(self, fallback_plan: str) -> str:
        """执行备选方案"""
        logger.info(f"Executing fallback plan: {fallback_plan}")
        return f"执行备选方案: {fallback_plan}"


    def _generate_execution_id(self) -> str:
        """生成执行ID"""
        return f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"


    def _log_execution_start(self, execution_id: str, plan: Dict[str, Any]):
        """记录执行开始"""
        log_entry = {
            "execution_id": execution_id,
            "start_time": datetime.now().isoformat(),
            "plan": plan,
            "status": "started"
        }
        self.execution_history.append(log_entry)
        logger.info(f"Task execution started: {execution_id}")


    def _log_execution_complete(self, execution_id: str, result: str, execution_time: float):
        """记录执行完成"""
        # 更新执行历史
        for entry in self.execution_history:
            if entry["execution_id"] == execution_id:
                entry.update({
                    "end_time": datetime.now().isoformat(),
                    "result": result,
                    "execution_time": execution_time,
                    "status": "completed"
                })
                break

        logger.info(f"Task execution completed: {execution_id}, time: {execution_time:.2f}s")


    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history[-limit:]


    def clear_execution_history(self):
        """清除执行历史"""
        self.execution_history.clear()
        logger.info("Execution history cleared")
