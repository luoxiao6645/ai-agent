"""
任务规划器
"""
import logging

from typing import Dict, Any, List, Optional
import json
import re

from langchain.llms.base import BaseLLM

from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)


class TaskPlanner:
    """任务规划器 - 使用ReAct框架进行复杂任务分解"""


    def __init__(self, llm: BaseLLM):
        """初始化任务规划器"""
        self.llm = llm
        self.planning_prompt = self._create_planning_prompt()

        logger.info("TaskPlanner initialized")


    def _create_planning_prompt(self) -> PromptTemplate:
        """创建任务规划提示模板"""
        template = """
你是一个智能任务规划器，需要分析用户的请求并制定执行计划。

用户请求: {user_input}

请分析这个请求并制定详细的执行计划。考虑以下因素：
1. 任务的复杂程度
2. 需要使用的工具
3. 执行步骤的顺序
4. 可能的风险和备选方案

可用的工具类型包括：
- web_search: 网络搜索
- document_parser: 文档解析
- code_executor: 代码执行
- data_analyzer: 数据分析
- image_processor: 图像处理
- audio_processor: 音频处理
- translator: 翻译工具
- calculator: 计算工具
- file_manager: 文件管理
- email_sender: 邮件发送
- calendar_manager: 日历管理
- api_caller: API调用

请以JSON格式返回执行计划：
{{
    "task_type": "simple|complex",
    "use_agent": true|false,
    "query": "处理后的查询文本",
    "steps": [
        {{
            "step": 1,
            "action": "工具名称或描述",
            "parameters": {{}},
            "expected_output": "预期输出描述"
        }}
    ],
    "estimated_time": "预估执行时间（秒）",
    "risk_level": "low|medium|high",
    "fallback_plan": "备选方案描述"
}}

执行计划:
"""
        return PromptTemplate(
            input_variables=["user_input"],
            template=template
        )

    async def plan_task(self, user_input: str) -> Dict[str, Any]:
        """
        制定任务执行计划

        Args:
            user_input: 用户输入

        Returns:
            任务执行计划
        """
        try:
            # 生成规划提示
            prompt = self.planning_prompt.format(user_input=user_input)

            # 调用LLM生成计划
            response = await self.llm.agenerate([prompt])
            plan_text = response.generations[0][0].text.strip()

            # 解析计划
            plan = self._parse_plan(plan_text)

            # 验证和优化计划
            plan = self._validate_and_optimize_plan(plan, user_input)

            logger.debug(f"Task plan generated: {plan['task_type']}")
            return plan

        except Exception as e:
            logger.error(f"Failed to plan task: {e}")
            # 返回默认计划
            return self._create_default_plan(user_input)


    def _parse_plan(self, plan_text: str) -> Dict[str, Any]:
        """解析LLM生成的计划文本"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                plan = json.loads(json_str)
                return plan
            else:
                raise ValueError("No JSON found in plan text")

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse plan JSON: {e}")
            # 尝试简单解析
            return self._simple_parse_plan(plan_text)


    def _simple_parse_plan(self, plan_text: str) -> Dict[str, Any]:
        """简单解析计划文本"""
        # 基于关键词的简单解析
        task_type = "simple"
        use_agent = True

        # 检测复杂任务关键词
        complex_keywords = ["步骤", "首先", "然后", "最后", "分析", "处理", "生成"]
        if any(keyword in plan_text for keyword in complex_keywords):
            task_type = "complex"

        # 检测工具使用
        tool_keywords = ["搜索", "计算", "翻译", "分析", "处理", "发送"]
        if any(keyword in plan_text for keyword in tool_keywords):
            use_agent = True

        return {
            "task_type": task_type,
            "use_agent": use_agent,
            "query": plan_text,
            "steps": [],
            "estimated_time": 5,
            "risk_level": "low",
            "fallback_plan": "使用默认Agent处理"
        }


    def _validate_and_optimize_plan(self, plan: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """验证和优化执行计划"""
        # 确保必要字段存在
        plan.setdefault("task_type", "simple")
        plan.setdefault("use_agent", True)
        plan.setdefault("query", user_input)
        plan.setdefault("steps", [])
        plan.setdefault("estimated_time", 5)
        plan.setdefault("risk_level", "low")
        plan.setdefault("fallback_plan", "使用默认Agent处理")

        # 优化查询文本
        if not plan["query"] or plan["query"] == user_input:
            plan["query"] = self._optimize_query(user_input)

        # 验证步骤
        if plan["steps"]:
            plan["steps"] = self._validate_steps(plan["steps"])

        return plan


    def _optimize_query(self, user_input: str) -> str:
        """优化查询文本"""
        # 简单的查询优化
        query = user_input.strip()

        # 添加上下文提示
        if len(query) < 10:
            query = f"请帮我处理以下请求：{query}"

        return query


    def _validate_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """验证执行步骤"""
        validated_steps = []

        for i, step in enumerate(steps):
            if isinstance(step, dict):
                validated_step = {
                    "step": step.get("step", i + 1),
                    "action": step.get("action", "处理请求"),
                    "parameters": step.get("parameters", {}),
                    "expected_output": step.get("expected_output", "处理结果")
                }
                validated_steps.append(validated_step)

        return validated_steps


    def _create_default_plan(self, user_input: str) -> Dict[str, Any]:
        """创建默认执行计划"""
        return {
            "task_type": "simple",
            "use_agent": True,
            "query": user_input,
            "steps": [
                {
                    "step": 1,
                    "action": "使用Agent处理请求",
                    "parameters": {"input": user_input},
                    "expected_output": "处理结果"
                }
            ],
            "estimated_time": 5,
            "risk_level": "low",
            "fallback_plan": "直接返回用户输入"
        }


    def estimate_complexity(self, user_input: str) -> str:
        """估算任务复杂度"""
        # 基于输入长度和关键词判断复杂度
        complex_indicators = [
            "分析", "比较", "生成", "创建", "设计", "计算",
            "搜索", "翻译", "处理", "转换", "整理", "总结"
        ]

        if len(user_input) > 100:
            return "complex"

        if any(indicator in user_input for indicator in complex_indicators):
            return "complex"

        return "simple"
