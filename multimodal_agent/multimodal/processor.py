"""
多模态处理器 - 增强版
支持文本、图像、音频、文件的智能融合处理
"""
import asyncio
import logging
import hashlib
import json

from typing import Dict, Any, Optional, List, Union

from datetime import datetime
import os

from .text_processor import TextProcessor

from .image_processor import ImageProcessor

from .audio_processor import AudioProcessor

from .file_processor import FileProcessor

logger = logging.getLogger(__name__)


class MultiModalProcessor:
    """
    多模态处理器 - 增强版
    支持多种模态的智能融合处理和跨模态理解
    """


    def __init__(self):
        """初始化多模态处理器"""
        self.text_processor = TextProcessor()
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.file_processor = FileProcessor()

        # 处理缓存
        self.processing_cache = {}

        # 支持的融合模式
        self.fusion_modes = {
            "sequential": self._sequential_fusion,
            "parallel": self._parallel_fusion,
            "hierarchical": self._hierarchical_fusion,
            "attention": self._attention_fusion
        }

        # 处理统计
        self.processing_stats = {
            "total_processed": 0,
            "by_type": {"text": 0, "image": 0, "audio": 0, "file": 0, "multimodal": 0},
            "cache_hits": 0,
            "processing_times": []
        }

        logger.info("Enhanced MultiModalProcessor initialized")

    async def process_input(self, input_data: Dict[str, Any]) -> str:
        """
        处理多模态输入

        Args:
            input_data: 输入数据，包含类型和内容

        Returns:
            处理后的文本
        """
        try:
            input_type = input_data.get("type", "text")
            content = input_data.get("content", "")

            if input_type == "text":
                return await self.process_text(content)
            elif input_type == "image":
                return await self.process_image(content)
            elif input_type == "audio":
                return await self.process_audio(content)
            elif input_type == "file":
                return await self.process_file(content)
            else:
                return f"不支持的输入类型: {input_type}"

        except Exception as e:
            logger.error(f"Multimodal processing failed: {e}")
            return f"多模态处理失败: {str(e)}"

    async def process_text(self, text: str) -> str:
        """处理文本输入"""
        return await self.text_processor.process(text)

    async def process_image(self, image_data: Any) -> str:
        """处理图像输入"""
        return await self.image_processor.process(image_data)

    async def process_audio(self, audio_data: Any) -> str:
        """处理音频输入"""
        return await self.audio_processor.process(audio_data)

    async def process_file(self, file_data: Any) -> str:
        """处理文件输入"""
        return await self.file_processor.process(file_data)


    def get_supported_types(self) -> list:
        """获取支持的输入类型"""
        return ["text", "image", "audio", "file"]

    async def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证输入数据"""
        result = {
            "valid": False,
            "type": None,
            "size": 0,
            "error": None
        }

        try:
            input_type = input_data.get("type", "text")
            content = input_data.get("content", "")

            result["type"] = input_type

            if input_type == "text":
                result["size"] = len(str(content))
                result["valid"] = True
            elif input_type in ["image", "audio", "file"]:
                # 检查文件是否存在
                if isinstance(content, str) and os.path.exists(content):
                    result["size"] = os.path.getsize(content)
                    result["valid"] = True
                else:
                    result["error"] = "文件不存在或路径无效"
            else:
                result["error"] = f"不支持的输入类型: {input_type}"

        except Exception as e:
            result["error"] = str(e)

        return result

    async def process_multimodal_fusion(self, input_data: Dict[str, Any], fusion_mode: str = "parallel") -> Dict[str, Any]:
        """
        处理多模态融合输入

        Args:
            input_data: 包含多种模态的输入数据
            fusion_mode: 融合模式 (sequential, parallel, hierarchical, attention)

        Returns:
            融合处理结果
        """
        try:
            start_time = datetime.now()

            # 验证融合模式
            if fusion_mode not in self.fusion_modes:
                fusion_mode = "parallel"

            # 提取各模态数据
            modalities = input_data.get("modalities", {})

            # 执行融合处理
            fusion_result = await self.fusion_modes[fusion_mode](modalities)

            # 更新统计信息
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats("multimodal", processing_time)

            return {
                "success": True,
                "fusion_mode": fusion_mode,
                "result": fusion_result,
                "processing_time": processing_time,
                "modalities_processed": list(modalities.keys())
            }

        except Exception as e:
            logger.error(f"Multimodal fusion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fusion_mode": fusion_mode
            }

    async def _sequential_fusion(self, modalities: Dict[str, Any]) -> str:
        """顺序融合处理"""
        results = []

        # 按优先级顺序处理
        priority_order = ["text", "image", "audio", "file"]

        for modality in priority_order:
            if modality in modalities:
                try:
                    if modality == "text":
                        result = await self.process_text(modalities[modality])
                    elif modality == "image":
                        result = await self.process_image(modalities[modality])
                    elif modality == "audio":
                        result = await self.process_audio(modalities[modality])
                    elif modality == "file":
                        result = await self.process_file(modalities[modality])

                    results.append(f"[{modality.upper()}] {result}")

                except Exception as e:
                    results.append(f"[{modality.upper()}] 处理失败: {str(e)}")

        return "\n\n".join(results)

    async def _parallel_fusion(self, modalities: Dict[str, Any]) -> str:
        """并行融合处理"""
        tasks = []

        for modality, data in modalities.items():
            if modality == "text":
                tasks.append(self._process_with_label(self.process_text(data), "TEXT"))
            elif modality == "image":
                tasks.append(self._process_with_label(self.process_image(data), "IMAGE"))
            elif modality == "audio":
                tasks.append(self._process_with_label(self.process_audio(data), "AUDIO"))
            elif modality == "file":
                tasks.append(self._process_with_label(self.process_file(data), "FILE"))

        # 并行执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(f"处理失败: {str(result)}")
            else:
                processed_results.append(result)

        return "\n\n".join(processed_results)

    async def _process_with_label(self, coro, label: str) -> str:
        """为处理结果添加标签"""
        try:
            result = await coro
            return f"[{label}] {result}"
        except Exception as e:
            return f"[{label}] 处理失败: {str(e)}"

    async def _hierarchical_fusion(self, modalities: Dict[str, Any]) -> str:
        """层次化融合处理"""
        # 第一层：基础模态处理
        base_results = {}

        for modality, data in modalities.items():
            try:
                if modality == "text":
                    base_results[modality] = await self.process_text(data)
                elif modality == "image":
                    base_results[modality] = await self.process_image(data)
                elif modality == "audio":
                    base_results[modality] = await self.process_audio(data)
                elif modality == "file":
                    base_results[modality] = await self.process_file(data)
            except Exception as e:
                base_results[modality] = f"处理失败: {str(e)}"

        # 第二层：跨模态关联分析
        cross_modal_insights = await self._analyze_cross_modal_relations(base_results)

        # 第三层：综合融合
        fusion_summary = await self._generate_fusion_summary(base_results, cross_modal_insights)

        return fusion_summary

    async def _attention_fusion(self, modalities: Dict[str, Any]) -> str:
        """注意力机制融合处理"""
        # 计算各模态的重要性权重
        weights = await self._calculate_attention_weights(modalities)

        # 根据权重处理各模态
        weighted_results = []

        for modality, data in modalities.items():
            weight = weights.get(modality, 1.0)

            try:
                if modality == "text":
                    result = await self.process_text(data)
                elif modality == "image":
                    result = await self.process_image(data)
                elif modality == "audio":
                    result = await self.process_audio(data)
                elif modality == "file":
                    result = await self.process_file(data)

                # 应用注意力权重
                weighted_result = f"[{modality.upper()} - 权重:{weight:.2f}] {result}"
                weighted_results.append((weight, weighted_result))

            except Exception as e:
                weighted_results.append((0.1, f"[{modality.upper()}] 处理失败: {str(e)}"))

        # 按权重排序
        weighted_results.sort(key=lambda x: x[0], reverse=True)

        return "\n\n".join([result for _, result in weighted_results])

    async def _analyze_cross_modal_relations(self, results: Dict[str, str]) -> str:
        """分析跨模态关联"""
        try:
            relations = []

            # 简单的关联分析
            if "text" in results and "image" in results:
                relations.append("文本与图像内容的关联分析")

            if "audio" in results and "text" in results:
                relations.append("音频与文本内容的一致性分析")

            if "file" in results:
                relations.append("文件内容与其他模态的补充关系")

            return "跨模态关联: " + ", ".join(relations) if relations else "无明显跨模态关联"

        except Exception as e:
            return f"跨模态分析失败: {str(e)}"

    async def _generate_fusion_summary(self, base_results: Dict[str, str], cross_modal: str) -> str:
        """生成融合摘要"""
        summary_parts = []

        # 添加各模态结果
        for modality, result in base_results.items():
            summary_parts.append(f"[{modality.upper()}] {result}")

        # 添加跨模态分析
        summary_parts.append(f"\n[跨模态分析] {cross_modal}")

        # 添加综合结论
        summary_parts.append(f"\n[综合结论] 基于{len(base_results)}种模态的综合分析结果")

        return "\n\n".join(summary_parts)

    async def _calculate_attention_weights(self, modalities: Dict[str, Any]) -> Dict[str, float]:
        """计算注意力权重"""
        weights = {}

        # 基于数据大小和类型计算权重
        for modality, data in modalities.items():
            if modality == "text":
                # 文本长度影响权重
                text_length = len(str(data))
                weights[modality] = min(1.0, text_length / 1000)
            elif modality == "image":
                # 图像默认高权重
                weights[modality] = 0.8
            elif modality == "audio":
                # 音频中等权重
                weights[modality] = 0.6
            elif modality == "file":
                # 文件权重取决于类型
                weights[modality] = 0.7
            else:
                weights[modality] = 0.5

        # 归一化权重
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}

        return weights


    def _generate_cache_key(self, input_data: Any) -> str:
        """生成缓存键"""
        try:
            # 将输入数据转换为字符串并生成哈希
            data_str = json.dumps(input_data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception:
            # 如果无法序列化，使用字符串表示
            return hashlib.md5(str(input_data).encode()).hexdigest()

    async def _get_cached_result(self, cache_key: str) -> Optional[str]:
        """获取缓存结果"""
        if cache_key in self.processing_cache:
            self.processing_stats["cache_hits"] += 1
            logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return self.processing_cache[cache_key]["result"]
        return None


    def _cache_result(self, cache_key: str, result: str):
        """缓存处理结果"""
        try:
            # 限制缓存大小
            if len(self.processing_cache) > 100:
                # 删除最旧的缓存项
                oldest_key = min(
                    self.processing_cache.keys(),
                    key=lambda k: self.processing_cache[k]["timestamp"]
                )
                del self.processing_cache[oldest_key]

            self.processing_cache[cache_key] = {
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")


    def _update_stats(self, input_type: str, processing_time: float):
        """更新处理统计"""
        self.processing_stats["total_processed"] += 1
        self.processing_stats["by_type"][input_type] += 1
        self.processing_stats["processing_times"].append(processing_time)

        # 保持处理时间列表大小
        if len(self.processing_stats["processing_times"]) > 1000:
            self.processing_stats["processing_times"] = self.processing_stats["processing_times"][-500:]


    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        processing_times = self.processing_stats["processing_times"]

        stats = {
            "total_processed": self.processing_stats["total_processed"],
            "by_type": self.processing_stats["by_type"].copy(),
            "cache_hits": self.processing_stats["cache_hits"],
            "cache_size": len(self.processing_cache)
        }

        if processing_times:
            stats["performance"] = {
                "avg_processing_time": sum(processing_times) / len(processing_times),
                "min_processing_time": min(processing_times),
                "max_processing_time": max(processing_times),
                "recent_avg": sum(processing_times[-10:]) / min(10, len(processing_times))
            }

        return stats


    def clear_cache(self):
        """清除处理缓存"""
        self.processing_cache.clear()
        logger.info("Processing cache cleared")


    def get_supported_fusion_modes(self) -> List[str]:
        """获取支持的融合模式"""
        return list(self.fusion_modes.keys())

    async def benchmark_processing(self, test_data: Dict[str, Any], iterations: int = 5) -> Dict[str, Any]:
        """性能基准测试"""
        try:
            results = {
                "iterations": iterations,
                "by_type": {},
                "fusion_modes": {}
            }

            # 测试各种输入类型
            for input_type in ["text", "image", "audio", "file"]:
                if input_type in test_data:
                    times = []
                    for _ in range(iterations):
                        start_time = datetime.now()

                        if input_type == "text":
                            await self.process_text(test_data[input_type])
                        elif input_type == "image":
                            await self.process_image(test_data[input_type])
                        elif input_type == "audio":
                            await self.process_audio(test_data[input_type])
                        elif input_type == "file":
                            await self.process_file(test_data[input_type])

                        processing_time = (datetime.now() - start_time).total_seconds()
                        times.append(processing_time)

                    results["by_type"][input_type] = {
                        "avg_time": sum(times) / len(times),
                        "min_time": min(times),
                        "max_time": max(times)
                    }

            # 测试融合模式
            if "multimodal" in test_data:
                for fusion_mode in self.fusion_modes.keys():
                    times = []
                    for _ in range(iterations):
                        start_time = datetime.now()
                        await self.process_multimodal_fusion(test_data["multimodal"], fusion_mode)
                        processing_time = (datetime.now() - start_time).total_seconds()
                        times.append(processing_time)

                    results["fusion_modes"][fusion_mode] = {
                        "avg_time": sum(times) / len(times),
                        "min_time": min(times),
                        "max_time": max(times)
                    }

            return results

        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return {"error": str(e)}
