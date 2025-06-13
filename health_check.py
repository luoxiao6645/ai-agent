"""
健康检查和监控端点

提供系统健康检查、监控数据API等功能
"""

from flask import Flask, jsonify, request
import threading
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
import os

# 导入性能监控模块
try:
    from performance import (
        get_cache_manager, get_connection_pool, get_async_processor,
        get_performance_monitor
    )
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

# 导入安全模块
try:
    from security import (
        get_input_validator, get_security_logger, get_session_manager,
        get_security_auditor
    )
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

app = Flask(__name__)

class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.last_check_time = 0
        self.health_status = "unknown"
        self.health_details = {}
    
    def check_system_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "uptime_human": self._format_uptime(uptime),
            "checks": {}
        }
        
        # 基础系统检查
        health_data["checks"]["basic"] = self._check_basic_system()
        
        # 性能组件检查
        if PERFORMANCE_AVAILABLE:
            health_data["checks"]["performance"] = self._check_performance_components()
        
        # 安全组件检查
        if SECURITY_AVAILABLE:
            health_data["checks"]["security"] = self._check_security_components()
        
        # 确定整体健康状态
        overall_status = self._determine_overall_status(health_data["checks"])
        health_data["status"] = overall_status
        
        # 缓存结果
        self.last_check_time = current_time
        self.health_status = overall_status
        self.health_details = health_data
        
        return health_data
    
    def _check_basic_system(self) -> Dict[str, Any]:
        """检查基础系统"""
        try:
            import psutil
            
            # CPU检查
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_status = "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
            
            # 内存检查
            memory = psutil.virtual_memory()
            memory_status = "healthy" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
            
            # 磁盘检查
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_status = "healthy" if disk_percent < 85 else "warning" if disk_percent < 95 else "critical"
            
            return {
                "status": max([cpu_status, memory_status, disk_status], key=lambda x: ["healthy", "warning", "critical"].index(x)),
                "cpu": {"percent": cpu_percent, "status": cpu_status},
                "memory": {"percent": memory.percent, "status": memory_status},
                "disk": {"percent": disk_percent, "status": disk_status}
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _check_performance_components(self) -> Dict[str, Any]:
        """检查性能组件"""
        try:
            performance_monitor = get_performance_monitor()
            cache_manager = get_cache_manager()
            connection_pool = get_connection_pool()
            async_processor = get_async_processor()
            
            # 性能监控检查
            monitor_stats = performance_monitor.get_monitoring_stats()
            monitor_status = "healthy" if monitor_stats.get("is_running", False) else "critical"
            
            # 缓存检查
            cache_stats = cache_manager.get_stats()
            cache_hit_rate = cache_stats.get("hit_rate_percent", 0)
            cache_status = "healthy" if cache_hit_rate > 50 else "warning" if cache_hit_rate > 20 else "degraded"
            
            # 连接池检查
            pool_health = connection_pool.health_check()
            pool_status = pool_health.get("status", "unknown")
            
            # 异步处理器检查
            async_stats = async_processor.get_stats()
            async_success_rate = async_stats.get("success_rate", 0)
            async_status = "healthy" if async_success_rate > 90 else "warning" if async_success_rate > 70 else "critical"
            
            overall_status = max([monitor_status, cache_status, pool_status, async_status], 
                               key=lambda x: ["healthy", "warning", "degraded", "critical"].index(x) if x in ["healthy", "warning", "degraded", "critical"] else 0)
            
            return {
                "status": overall_status,
                "monitor": {"status": monitor_status, "running": monitor_stats.get("is_running", False)},
                "cache": {"status": cache_status, "hit_rate": cache_hit_rate},
                "connection_pool": {"status": pool_status},
                "async_processor": {"status": async_status, "success_rate": async_success_rate}
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _check_security_components(self) -> Dict[str, Any]:
        """检查安全组件"""
        try:
            input_validator = get_input_validator()
            security_logger = get_security_logger()
            session_manager = get_session_manager()
            security_auditor = get_security_auditor()
            
            # 输入验证检查
            validation_stats = input_validator.get_validation_stats()
            block_rate = validation_stats.get("block_rate", 0)
            validation_status = "healthy" if block_rate < 10 else "warning" if block_rate < 30 else "critical"
            
            # 安全审计检查
            security_summary = security_auditor.get_security_summary()
            total_events = security_summary.get("total_events", 0)
            critical_events = security_summary.get("severity_counts", {}).get("CRITICAL", 0)
            audit_status = "healthy" if critical_events == 0 else "warning" if critical_events < 5 else "critical"
            
            overall_status = max([validation_status, audit_status], 
                               key=lambda x: ["healthy", "warning", "critical"].index(x))
            
            return {
                "status": overall_status,
                "validation": {"status": validation_status, "block_rate": block_rate},
                "audit": {"status": audit_status, "total_events": total_events, "critical_events": critical_events}
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _determine_overall_status(self, checks: Dict[str, Any]) -> str:
        """确定整体健康状态"""
        statuses = []
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict) and "status" in check_data:
                statuses.append(check_data["status"])
        
        if not statuses:
            return "unknown"
        
        # 按严重程度排序
        severity_order = ["healthy", "warning", "degraded", "critical", "error"]
        return max(statuses, key=lambda x: severity_order.index(x) if x in severity_order else 0)
    
    def _format_uptime(self, uptime_seconds: float) -> str:
        """格式化运行时间"""
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

# 全局健康检查器实例
health_checker = HealthChecker()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        health_data = health_checker.check_system_health()
        status_code = 200 if health_data["status"] in ["healthy", "warning"] else 503
        return jsonify(health_data), status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/health/quick', methods=['GET'])
def quick_health_check():
    """快速健康检查"""
    try:
        current_time = time.time()
        uptime = current_time - health_checker.start_time
        
        return jsonify({
            "status": "healthy",
            "uptime_seconds": uptime,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """获取系统指标"""
    try:
        metrics = {}
        
        if PERFORMANCE_AVAILABLE:
            performance_monitor = get_performance_monitor()
            cache_manager = get_cache_manager()
            connection_pool = get_connection_pool()
            async_processor = get_async_processor()
            
            metrics["performance"] = {
                "system": performance_monitor.get_current_system_status(),
                "cache": cache_manager.get_stats(),
                "connection_pool": connection_pool.get_all_stats(),
                "async_processor": async_processor.get_stats()
            }
        
        if SECURITY_AVAILABLE:
            input_validator = get_input_validator()
            security_auditor = get_security_auditor()
            
            metrics["security"] = {
                "validation": input_validator.get_validation_stats(),
                "audit": security_auditor.get_security_summary()
            }
        
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """获取系统状态摘要"""
    try:
        uptime = time.time() - health_checker.start_time
        
        status_data = {
            "service": "multimodal-ai-agent",
            "version": "1.0.0",
            "status": health_checker.health_status,
            "uptime_seconds": uptime,
            "uptime_human": health_checker._format_uptime(uptime),
            "timestamp": datetime.now().isoformat(),
            "features": {
                "performance_monitoring": PERFORMANCE_AVAILABLE,
                "security_hardening": SECURITY_AVAILABLE
            }
        }
        
        return jsonify(status_data), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/ready', methods=['GET'])
def readiness_check():
    """就绪检查"""
    try:
        # 检查关键组件是否就绪
        ready = True
        components = {}
        
        if PERFORMANCE_AVAILABLE:
            try:
                performance_monitor = get_performance_monitor()
                monitor_stats = performance_monitor.get_monitoring_stats()
                components["performance_monitor"] = monitor_stats.get("is_running", False)
                if not components["performance_monitor"]:
                    ready = False
            except:
                components["performance_monitor"] = False
                ready = False
        
        return jsonify({
            "ready": ready,
            "components": components,
            "timestamp": datetime.now().isoformat()
        }), 200 if ready else 503
    except Exception as e:
        return jsonify({
            "ready": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def run_health_server(host='0.0.0.0', port=8080):
    """运行健康检查服务器"""
    app.run(host=host, port=port, debug=False, threaded=True)

def start_health_server_thread(host='0.0.0.0', port=8080):
    """在后台线程启动健康检查服务器"""
    server_thread = threading.Thread(
        target=run_health_server,
        args=(host, port),
        daemon=True,
        name="HealthCheckServer"
    )
    server_thread.start()
    return server_thread

if __name__ == "__main__":
    run_health_server()
