"""
性能优化管理器
统一管理所有性能优化组件
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .performance_monitor import performance_monitor
from .cache_manager import cache_manager
from .database_optimizer import db_optimizer
from .async_optimizer import async_optimizer
from .memory_optimizer import memory_optimizer
from .api_optimizer import api_optimizer

logger = logging.getLogger(__name__)

class OptimizationManager:
    """性能优化管理器"""
    
    def __init__(self):
        self.components = {
            "performance_monitor": performance_monitor,
            "cache_manager": cache_manager,
            "database_optimizer": db_optimizer,
            "async_optimizer": async_optimizer,
            "memory_optimizer": memory_optimizer,
            "api_optimizer": api_optimizer
        }
        
        self.optimization_active = False
        self.optimization_config = {
            "auto_optimization": True,
            "optimization_interval": 300,  # 5分钟
            "performance_thresholds": {
                "response_time_ms": 2000,
                "memory_usage_percent": 80,
                "cpu_usage_percent": 80,
                "cache_hit_rate_percent": 70,
                "error_rate_percent": 5
            }
        }
        
        # 优化历史
        self.optimization_history = []
        
    async def start_optimization(self):
        """启动性能优化"""
        if self.optimization_active:
            return
        
        logger.info("Starting performance optimization...")
        
        try:
            # 启动各个组件
            performance_monitor.start_monitoring()
            await async_optimizer.start()
            memory_optimizer.start_optimization()
            
            self.optimization_active = True
            
            # 启动自动优化循环
            if self.optimization_config["auto_optimization"]:
                asyncio.create_task(self._optimization_loop())
            
            logger.info("Performance optimization started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start optimization: {e}")
            raise
    
    async def stop_optimization(self):
        """停止性能优化"""
        if not self.optimization_active:
            return
        
        logger.info("Stopping performance optimization...")
        
        try:
            self.optimization_active = False
            
            # 停止各个组件
            performance_monitor.stop_monitoring()
            await async_optimizer.stop()
            memory_optimizer.stop_optimization()
            
            logger.info("Performance optimization stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop optimization: {e}")
    
    async def _optimization_loop(self):
        """自动优化循环"""
        while self.optimization_active:
            try:
                await self.run_optimization_cycle()
                await asyncio.sleep(self.optimization_config["optimization_interval"])
            except Exception as e:
                logger.error(f"Optimization cycle failed: {e}")
                await asyncio.sleep(60)  # 出错时等待1分钟
    
    async def run_optimization_cycle(self):
        """运行一次优化周期"""
        logger.info("Running optimization cycle...")
        
        start_time = time.time()
        optimizations_applied = []
        
        try:
            # 获取当前性能指标
            current_metrics = await self.get_current_metrics()
            
            # 检查是否需要优化
            issues = self._analyze_performance_issues(current_metrics)
            
            if not issues:
                logger.info("No performance issues detected")
                return
            
            # 应用优化措施
            for issue in issues:
                optimization = await self._apply_optimization(issue)
                if optimization:
                    optimizations_applied.append(optimization)
            
            # 记录优化历史
            optimization_record = {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": time.time() - start_time,
                "issues_detected": len(issues),
                "optimizations_applied": len(optimizations_applied),
                "details": optimizations_applied
            }
            
            self.optimization_history.append(optimization_record)
            
            # 保持历史记录在合理范围内
            if len(self.optimization_history) > 100:
                self.optimization_history = self.optimization_history[-100:]
            
            logger.info(f"Optimization cycle completed: {len(optimizations_applied)} optimizations applied")
            
        except Exception as e:
            logger.error(f"Optimization cycle failed: {e}")
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前性能指标"""
        metrics = {}
        
        try:
            # 性能监控指标
            perf_summary = performance_monitor.get_performance_summary()
            metrics["performance"] = perf_summary
            
            # 缓存指标
            cache_stats = cache_manager.get_stats()
            metrics["cache"] = cache_stats
            
            # 数据库指标
            db_report = db_optimizer.get_optimization_report()
            metrics["database"] = db_report
            
            # 异步处理指标
            async_report = async_optimizer.get_optimization_report()
            metrics["async"] = async_report
            
            # 内存指标
            memory_report = memory_optimizer.get_optimization_report()
            metrics["memory"] = memory_report
            
            # API指标
            api_summary = api_optimizer.get_performance_summary()
            metrics["api"] = api_summary
            
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
        
        return metrics
    
    def _analyze_performance_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析性能问题"""
        issues = []
        thresholds = self.optimization_config["performance_thresholds"]
        
        try:
            # 检查响应时间
            api_stats = metrics.get("api", {}).get("request_stats", {})
            avg_response_time = api_stats.get("avg_response_time", 0) * 1000  # 转换为毫秒
            
            if avg_response_time > thresholds["response_time_ms"]:
                issues.append({
                    "type": "high_response_time",
                    "severity": "medium",
                    "current_value": avg_response_time,
                    "threshold": thresholds["response_time_ms"],
                    "description": f"平均响应时间 {avg_response_time:.1f}ms 超过阈值"
                })
            
            # 检查内存使用
            memory_stats = metrics.get("memory", {}).get("memory_analysis", {}).get("current_memory", {})
            memory_percent = memory_stats.get("memory_percent", 0)
            
            if memory_percent > thresholds["memory_usage_percent"]:
                issues.append({
                    "type": "high_memory_usage",
                    "severity": "high",
                    "current_value": memory_percent,
                    "threshold": thresholds["memory_usage_percent"],
                    "description": f"内存使用率 {memory_percent:.1f}% 超过阈值"
                })
            
            # 检查缓存命中率
            cache_stats = metrics.get("cache", {})
            hit_rate = cache_stats.get("hit_rate_percent", 0)
            
            if hit_rate < thresholds["cache_hit_rate_percent"]:
                issues.append({
                    "type": "low_cache_hit_rate",
                    "severity": "medium",
                    "current_value": hit_rate,
                    "threshold": thresholds["cache_hit_rate_percent"],
                    "description": f"缓存命中率 {hit_rate:.1f}% 低于阈值"
                })
            
            # 检查错误率
            error_rate = api_stats.get("error_rate_percent", 0)
            
            if error_rate > thresholds["error_rate_percent"]:
                issues.append({
                    "type": "high_error_rate",
                    "severity": "high",
                    "current_value": error_rate,
                    "threshold": thresholds["error_rate_percent"],
                    "description": f"错误率 {error_rate:.1f}% 超过阈值"
                })
            
        except Exception as e:
            logger.error(f"Failed to analyze performance issues: {e}")
        
        return issues
    
    async def _apply_optimization(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """应用优化措施"""
        issue_type = issue["type"]
        
        try:
            if issue_type == "high_memory_usage":
                # 执行内存优化
                result = memory_optimizer.optimize_memory()
                return {
                    "type": "memory_optimization",
                    "action": "garbage_collection",
                    "result": result
                }
            
            elif issue_type == "low_cache_hit_rate":
                # 清理过期缓存
                expired_count = cache_manager.cleanup_expired()
                return {
                    "type": "cache_optimization",
                    "action": "cleanup_expired",
                    "expired_entries": expired_count
                }
            
            elif issue_type == "high_response_time":
                # 可以实施更多优化措施
                return {
                    "type": "response_time_optimization",
                    "action": "analysis_logged",
                    "note": "需要进一步分析慢查询和端点"
                }
            
            elif issue_type == "high_error_rate":
                # 记录错误分析
                return {
                    "type": "error_rate_optimization",
                    "action": "analysis_logged",
                    "note": "需要检查错误日志和API稳定性"
                }
            
        except Exception as e:
            logger.error(f"Failed to apply optimization for {issue_type}: {e}")
        
        return None
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        current_metrics = await self.get_current_metrics()
        
        # 计算整体性能分数
        performance_score = self._calculate_performance_score(current_metrics)
        
        # 生成建议
        recommendations = self._generate_recommendations(current_metrics)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "optimization_active": self.optimization_active,
            "performance_score": performance_score,
            "current_metrics": current_metrics,
            "recent_optimizations": self.optimization_history[-10:],
            "recommendations": recommendations,
            "configuration": self.optimization_config
        }
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """计算性能分数（0-100）"""
        score = 100.0
        
        try:
            # 响应时间评分（30%权重）
            api_stats = metrics.get("api", {}).get("request_stats", {})
            avg_response_time = api_stats.get("avg_response_time", 0) * 1000
            if avg_response_time > 1000:
                score -= min(30, (avg_response_time - 1000) / 100 * 5)
            
            # 内存使用评分（25%权重）
            memory_stats = metrics.get("memory", {}).get("memory_analysis", {}).get("current_memory", {})
            memory_percent = memory_stats.get("memory_percent", 0)
            if memory_percent > 70:
                score -= min(25, (memory_percent - 70) / 30 * 25)
            
            # 缓存命中率评分（20%权重）
            cache_stats = metrics.get("cache", {})
            hit_rate = cache_stats.get("hit_rate_percent", 100)
            if hit_rate < 80:
                score -= min(20, (80 - hit_rate) / 80 * 20)
            
            # 错误率评分（25%权重）
            error_rate = api_stats.get("error_rate_percent", 0)
            if error_rate > 1:
                score -= min(25, error_rate * 5)
            
        except Exception as e:
            logger.error(f"Failed to calculate performance score: {e}")
            score = 50.0  # 默认分数
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        try:
            # 从各个组件获取建议
            api_summary = metrics.get("api", {})
            if "recommendations" in api_summary:
                recommendations.extend(api_summary["recommendations"])
            
            memory_analysis = metrics.get("memory", {}).get("memory_analysis", {})
            if "recommendations" in memory_analysis:
                recommendations.extend(memory_analysis["recommendations"])
            
            db_report = metrics.get("database", {})
            if "recommendations" in db_report:
                recommendations.extend(db_report["recommendations"])
            
            # 去重
            recommendations = list(set(recommendations))
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
        
        return recommendations
    
    def export_optimization_report(self, filename: str = None) -> str:
        """导出优化报告"""
        if filename is None:
            filename = f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            # 获取完整报告（同步版本）
            report = {
                "export_timestamp": datetime.now().isoformat(),
                "optimization_active": self.optimization_active,
                "configuration": self.optimization_config,
                "optimization_history": self.optimization_history,
                "component_status": {
                    name: "active" if hasattr(component, 'monitoring_active') and getattr(component, 'monitoring_active', False) else "inactive"
                    for name, component in self.components.items()
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Optimization report exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to export optimization report: {e}")
            return ""

# 全局优化管理器实例
optimization_manager = OptimizationManager()

async def start_performance_optimization():
    """启动性能优化（全局函数）"""
    await optimization_manager.start_optimization()

async def stop_performance_optimization():
    """停止性能优化（全局函数）"""
    await optimization_manager.stop_optimization()

async def get_optimization_report():
    """获取优化报告（全局函数）"""
    return await optimization_manager.get_optimization_report()

def export_optimization_report(filename: str = None):
    """导出优化报告（全局函数）"""
    return optimization_manager.export_optimization_report(filename)
