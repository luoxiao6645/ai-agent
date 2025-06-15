"""
工具管理器 - 增强版
支持智能工具选择、执行监控和性能优化
"""
import asyncio
import logging
import time

from typing import Dict, List, Optional, Any, Tuple

from datetime import datetime, timedelta

from collections import defaultdict, deque

from langchain.tools.base import BaseTool

from config import Config

from .web_search import WebSearchTool

from .document import DocumentParserTool

from .code_exec import CodeExecutorTool

from .data_analysis import DataAnalysisTool

from .image_processor import ImageProcessorTool

from .audio_processor import AudioProcessorTool

from .translator import TranslatorTool

from .calculator import CalculatorTool

from .file_manager import FileManagerTool

from .email_sender import EmailSenderTool

from .calendar_manager import CalendarManagerTool

from .api_caller import APICallerTool

logger = logging.getLogger(__name__)


class ToolManager:
    """
    工具管理器 - 增强版
    支持智能工具选择、执行监控、性能优化和负载均衡
    """


    def __init__(self):
        """初始化工具管理器"""
        self.config = Config()
        self.tools: Dict[str, BaseTool] = {}

        # 工具执行统计
        self.tool_stats = defaultdict(lambda: {
            "total_calls": 0,
            "success_calls": 0,
            "failed_calls": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "last_used": None,
            "error_history": deque(maxlen=10)
        })

        # 工具性能监控
        self.performance_monitor = {
            "recent_executions": deque(maxlen=100),
            "slow_tools": set(),
            "failed_tools": set(),
            "tool_priorities": {}
        }

        # 智能选择器
        self.tool_selector = ToolSelector()

        # 并发控制
        self.execution_semaphore = asyncio.Semaphore(10)  # 最大并发数
        self.tool_locks = defaultdict(asyncio.Lock)  # 工具级锁

        self._initialize_tools()
        self._initialize_tool_priorities()

        logger.info(f"Enhanced ToolManager initialized with {len(self.tools)} tools")


    def _initialize_tools(self):
        """初始化所有工具"""
        try:
            # 1. Web搜索工具
            if self.config.ENABLE_WEB_SEARCH:
                self.tools["web_search"] = WebSearchTool()

            # 2. 文档解析工具
            if self.config.ENABLE_FILE_PROCESSING:
                self.tools["document_parser"] = DocumentParserTool()

            # 3. 代码执行工具
            if self.config.ENABLE_CODE_EXECUTION:
                self.tools["code_executor"] = CodeExecutorTool()

            # 4. 数据分析工具
            self.tools["data_analyzer"] = DataAnalysisTool()

            # 5. 图像处理工具
            self.tools["image_processor"] = ImageProcessorTool()

            # 6. 音频处理工具
            self.tools["audio_processor"] = AudioProcessorTool()

            # 7. 翻译工具
            self.tools["translator"] = TranslatorTool()

            # 8. 计算工具
            self.tools["calculator"] = CalculatorTool()

            # 9. 文件管理工具
            if self.config.ENABLE_FILE_PROCESSING:
                self.tools["file_manager"] = FileManagerTool()

            # 10. 邮件工具
            self.tools["email_sender"] = EmailSenderTool()

            # 11. 日历工具
            self.tools["calendar_manager"] = CalendarManagerTool()

            # 12. API调用工具
            self.tools["api_caller"] = APICallerTool()

            logger.info("All tools initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            raise


    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取指定工具

        Args:
            tool_name: 工具名称

        Returns:
            工具实例或None
        """
        return self.tools.get(tool_name)


    def get_all_tools(self) -> List[BaseTool]:
        """获取所有可用工具"""
        return list(self.tools.values())


    def get_tool_names(self) -> List[str]:
        """获取所有工具名称"""
        return list(self.tools.keys())


    def is_tool_available(self, tool_name: str) -> bool:
        """检查工具是否可用"""
        return tool_name in self.tools


    def add_tool(self, tool_name: str, tool: BaseTool):
        """
        添加新工具

        Args:
            tool_name: 工具名称
            tool: 工具实例
        """
        self.tools[tool_name] = tool
        logger.info(f"Tool '{tool_name}' added")


    def remove_tool(self, tool_name: str) -> bool:
        """
        移除工具

        Args:
            tool_name: 工具名称

        Returns:
            是否成功移除
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Tool '{tool_name}' removed")
            return True
        return False


    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        获取工具信息

        Args:
            tool_name: 工具名称

        Returns:
            工具信息字典
        """
        tool = self.get_tool(tool_name)
        if tool:
            return {
                "name": tool.name,
                "description": tool.description,
                "args_schema": tool.args_schema.schema() if tool.args_schema else None
            }
        return None


    def get_all_tools_info(self) -> List[Dict[str, Any]]:
        """获取所有工具信息"""
        tools_info = []
        for tool_name in self.tools:
            info = self.get_tool_info(tool_name)
            if info:
                tools_info.append(info)
        return tools_info

    async def test_tool(self, tool_name: str, test_input: str = "test") -> Dict[str, Any]:
        """
        测试工具功能

        Args:
            tool_name: 工具名称
            test_input: 测试输入

        Returns:
            测试结果
        """
        try:
            tool = self.get_tool(tool_name)
            if not tool:
                return {"success": False, "error": f"Tool '{tool_name}' not found"}

            # 执行测试
            result = await tool.arun(test_input)

            return {
                "success": True,
                "tool_name": tool_name,
                "test_input": test_input,
                "result": result
            }

        except Exception as e:
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e)
            }

    async def test_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """测试所有工具"""
        results = {}

        for tool_name in self.tools:
            results[tool_name] = await self.test_tool(tool_name)

        return results


    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """
        按类别获取工具

        Args:
            category: 工具类别

        Returns:
            该类别的工具列表
        """
        category_mapping = {
            "search": ["web_search"],
            "processing": ["document_parser", "image_processor", "audio_processor"],
            "analysis": ["data_analyzer", "code_executor"],
            "communication": ["email_sender", "translator"],
            "utility": ["calculator", "file_manager", "calendar_manager", "api_caller"]
        }

        tool_names = category_mapping.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]


    def get_tool_statistics(self) -> Dict[str, Any]:
        """获取工具统计信息"""
        return {
            "total_tools": len(self.tools),
            "available_tools": list(self.tools.keys()),
            "categories": {
                "search": len(self.get_tools_by_category("search")),
                "processing": len(self.get_tools_by_category("processing")),
                "analysis": len(self.get_tools_by_category("analysis")),
                "communication": len(self.get_tools_by_category("communication")),
                "utility": len(self.get_tools_by_category("utility"))
            }
        }


    def _initialize_tool_priorities(self):
        """初始化工具优先级"""
        # 基于工具类型设置默认优先级
        default_priorities = {
            "web_search": 0.9,
            "document_parser": 0.8,
            "data_analyzer": 0.8,
            "calculator": 0.9,
            "translator": 0.7,
            "image_processor": 0.6,
            "audio_processor": 0.6,
            "code_executor": 0.5,  # 较低优先级，因为可能有安全风险
            "file_manager": 0.7,
            "email_sender": 0.4,
            "calendar_manager": 0.6,
            "api_caller": 0.5
        }

        for tool_name, priority in default_priorities.items():
            if tool_name in self.tools:
                self.performance_monitor["tool_priorities"][tool_name] = priority

    async def execute_tool_with_monitoring(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        带监控的工具执行

        Args:
            tool_name: 工具名称
            *args, **kwargs: 工具参数

        Returns:
            执行结果和统计信息
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "tool_name": tool_name
            }

        # 并发控制
        async with self.execution_semaphore:
            async with self.tool_locks[tool_name]:
                return await self._execute_tool_internal(tool_name, *args, **kwargs)

    async def _execute_tool_internal(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """内部工具执行方法"""
        tool = self.tools[tool_name]
        start_time = time.time()

        try:
            # 执行工具
            if asyncio.iscoroutinefunction(tool._arun):
                result = await tool._arun(*args, **kwargs)
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, tool._run, *args, **kwargs
                )

            execution_time = time.time() - start_time

            # 更新统计信息
            self._update_tool_stats(tool_name, True, execution_time)

            # 记录执行信息
            execution_info = {
                "tool_name": tool_name,
                "execution_time": execution_time,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            self.performance_monitor["recent_executions"].append(execution_info)

            return {
                "success": True,
                "result": result,
                "tool_name": tool_name,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)

            # 更新统计信息
            self._update_tool_stats(tool_name, False, execution_time, error_msg)

            # 记录执行信息
            execution_info = {
                "tool_name": tool_name,
                "execution_time": execution_time,
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
            self.performance_monitor["recent_executions"].append(execution_info)

            return {
                "success": False,
                "error": error_msg,
                "tool_name": tool_name,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }


    def _update_tool_stats(self, tool_name: str, success: bool, execution_time: float, error_msg: str = None):
        """更新工具统计信息"""
        stats = self.tool_stats[tool_name]

        stats["total_calls"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["total_calls"]
        stats["last_used"] = datetime.now().isoformat()

        if success:
            stats["success_calls"] += 1
        else:
            stats["failed_calls"] += 1
            if error_msg:
                stats["error_history"].append({
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                })

        # 更新性能监控
        self._update_performance_monitoring(tool_name, success, execution_time)


    def _update_performance_monitoring(self, tool_name: str, success: bool, execution_time: float):
        """更新性能监控"""
        # 标记慢工具（执行时间超过5秒）
        if execution_time > 5.0:
            self.performance_monitor["slow_tools"].add(tool_name)

        # 标记失败工具
        if not success:
            self.performance_monitor["failed_tools"].add(tool_name)
        else:
            # 如果成功，从失败工具中移除
            self.performance_monitor["failed_tools"].discard(tool_name)

        # 动态调整工具优先级
        self._adjust_tool_priority(tool_name, success, execution_time)


    def _adjust_tool_priority(self, tool_name: str, success: bool, execution_time: float):
        """动态调整工具优先级"""
        current_priority = self.performance_monitor["tool_priorities"].get(tool_name, 0.5)

        if success:
            # 成功执行，略微提高优先级
            if execution_time < 1.0:  # 快速执行
                new_priority = min(1.0, current_priority + 0.01)
            else:
                new_priority = min(1.0, current_priority + 0.005)
        else:
            # 执行失败，降低优先级
            new_priority = max(0.1, current_priority - 0.02)

        self.performance_monitor["tool_priorities"][tool_name] = new_priority

    async def suggest_tools_for_task(self, task_description: str, max_suggestions: int = 3) -> List[Dict[str, Any]]:
        """
        为任务建议最适合的工具

        Args:
            task_description: 任务描述
            max_suggestions: 最大建议数量

        Returns:
            建议的工具列表
        """
        return await self.tool_selector.suggest_tools(
            task_description,
            self.tools,
            self.tool_stats,
            self.performance_monitor["tool_priorities"],
            max_suggestions
        )

    async def execute_parallel_tools(self, tool_tasks: List[Tuple[str, tuple, dict]]) -> List[Dict[str, Any]]:
        """
        并行执行多个工具

        Args:
            tool_tasks: 工具任务列表，每个元素为(tool_name, args, kwargs)

        Returns:
            执行结果列表
        """
        tasks = []
        for tool_name, args, kwargs in tool_tasks:
            task = self.execute_tool_with_monitoring(tool_name, *args, **kwargs)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                tool_name = tool_tasks[i][0]
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "tool_name": tool_name
                })
            else:
                processed_results.append(result)

        return processed_results


    def get_tool_performance_report(self) -> Dict[str, Any]:
        """获取工具性能报告"""
        report = {
            "summary": {
                "total_tools": len(self.tools),
                "total_executions": sum(stats["total_calls"] for stats in self.tool_stats.values()),
                "slow_tools": list(self.performance_monitor["slow_tools"]),
                "failed_tools": list(self.performance_monitor["failed_tools"])
            },
            "tool_details": {},
            "recommendations": []
        }

        # 工具详细信息
        for tool_name, stats in self.tool_stats.items():
            if stats["total_calls"] > 0:
                success_rate = stats["success_calls"] / stats["total_calls"]
                report["tool_details"][tool_name] = {
                    "total_calls": stats["total_calls"],
                    "success_rate": success_rate,
                    "avg_execution_time": stats["avg_time"],
                    "last_used": stats["last_used"],
                    "priority": self.performance_monitor["tool_priorities"].get(tool_name, 0.5)
                }

        # 生成建议
        report["recommendations"] = self._generate_performance_recommendations()

        return report


    def _generate_performance_recommendations(self) -> List[str]:
        """生成性能优化建议"""
        recommendations = []

        # 检查慢工具
        if self.performance_monitor["slow_tools"]:
            recommendations.append(
                f"以下工具执行较慢，建议优化: {', '.join(self.performance_monitor['slow_tools'])}"
            )

        # 检查失败工具
        if self.performance_monitor["failed_tools"]:
            recommendations.append(
                f"以下工具经常失败，建议检查: {', '.join(self.performance_monitor['failed_tools'])}"
            )

        # 检查未使用的工具
        unused_tools = [name for name, stats in self.tool_stats.items() if stats["total_calls"] == 0]
        if unused_tools:
            recommendations.append(
                f"以下工具从未使用，考虑移除: {', '.join(unused_tools)}"
            )

        return recommendations


    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        total_calls = sum(stats["total_calls"] for stats in self.tool_stats.values())

        usage_stats = {
            "total_calls": total_calls,
            "tools_used": len([name for name, stats in self.tool_stats.items() if stats["total_calls"] > 0]),
            "most_used_tools": [],
            "least_used_tools": [],
            "average_success_rate": 0.0
        }

        if total_calls > 0:
            # 最常用工具
            sorted_by_usage = sorted(
                self.tool_stats.items(),
                key=lambda x: x[1]["total_calls"],
                reverse=True
            )
            usage_stats["most_used_tools"] = [
                {"name": name, "calls": stats["total_calls"]}
                for name, stats in sorted_by_usage[:5]
                if stats["total_calls"] > 0
            ]

            # 最少用工具
            usage_stats["least_used_tools"] = [
                {"name": name, "calls": stats["total_calls"]}
                for name, stats in sorted_by_usage[-5:]
                if stats["total_calls"] > 0
            ]

            # 平均成功率
            total_success = sum(stats["success_calls"] for stats in self.tool_stats.values())
            usage_stats["average_success_rate"] = total_success / total_calls if total_calls > 0 else 0.0

        return usage_stats


class ToolSelector:
    """智能工具选择器"""


    def __init__(self):
        # 任务关键词到工具的映射
        self.task_tool_mapping = {
            "搜索": ["web_search"],
            "查找": ["web_search"],
            "文档": ["document_parser", "file_manager"],
            "解析": ["document_parser"],
            "计算": ["calculator", "data_analyzer"],
            "数学": ["calculator"],
            "分析": ["data_analyzer"],
            "图像": ["image_processor"],
            "图片": ["image_processor"],
            "音频": ["audio_processor"],
            "声音": ["audio_processor"],
            "翻译": ["translator"],
            "邮件": ["email_sender"],
            "日历": ["calendar_manager"],
            "代码": ["code_executor"],
            "编程": ["code_executor"],
            "API": ["api_caller"],
            "文件": ["file_manager"]
        }

    async def suggest_tools(self, task_description: str, available_tools: Dict[str, BaseTool],
                          tool_stats: Dict, tool_priorities: Dict, max_suggestions: int = 3) -> List[Dict[str, Any]]:
        """建议适合的工具"""
        suggestions = []

        # 基于关键词匹配
        keyword_matches = self._match_keywords(task_description.lower())

        # 计算工具得分
        tool_scores = {}
        for tool_name in available_tools.keys():
            score = self._calculate_tool_score(
                tool_name, keyword_matches, tool_stats, tool_priorities
            )
            if score > 0:
                tool_scores[tool_name] = score

        # 排序并返回建议
        sorted_tools = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)

        for tool_name, score in sorted_tools[:max_suggestions]:
            tool = available_tools[tool_name]
            suggestions.append({
                "tool_name": tool_name,
                "description": tool.description,
                "confidence_score": score,
                "reason": self._generate_suggestion_reason(tool_name, keyword_matches, score)
            })

        return suggestions


    def _match_keywords(self, task_description: str) -> Dict[str, List[str]]:
        """匹配任务描述中的关键词"""
        matches = {}

        for keyword, tools in self.task_tool_mapping.items():
            if keyword in task_description:
                matches[keyword] = tools

        return matches


    def _calculate_tool_score(self, tool_name: str, keyword_matches: Dict,
                            tool_stats: Dict, tool_priorities: Dict) -> float:
        """计算工具得分"""
        score = 0.0

        # 基础优先级得分
        base_priority = tool_priorities.get(tool_name, 0.5)
        score += base_priority * 0.4

        # 关键词匹配得分
        for keyword, tools in keyword_matches.items():
            if tool_name in tools:
                score += 0.3

        # 历史性能得分
        stats = tool_stats.get(tool_name, {})
        if stats.get("total_calls", 0) > 0:
            success_rate = stats["success_calls"] / stats["total_calls"]
            score += success_rate * 0.2

            # 执行速度得分（越快得分越高）
            avg_time = stats.get("avg_time", 5.0)
            speed_score = max(0, 1 - (avg_time / 10.0))  # 10秒以上得分为0
            score += speed_score * 0.1

        return min(1.0, score)


    def _generate_suggestion_reason(self, tool_name: str, keyword_matches: Dict, score: float) -> str:
        """生成建议理由"""
        reasons = []

        # 关键词匹配理由
        for keyword, tools in keyword_matches.items():
            if tool_name in tools:
                reasons.append(f"匹配关键词'{keyword}'")

        # 得分理由
        if score > 0.8:
            reasons.append("高置信度推荐")
        elif score > 0.6:
            reasons.append("中等置信度推荐")
        else:
            reasons.append("低置信度推荐")

        return "，".join(reasons) if reasons else "基于综合评估推荐"
