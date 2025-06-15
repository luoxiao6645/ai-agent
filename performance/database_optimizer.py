"""
数据库查询优化器
提供查询分析、索引建议、连接池管理等功能
"""

import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    """查询指标"""
    query_hash: str
    query_text: str
    execution_time: float
    rows_affected: int
    timestamp: str
    success: bool
    error_message: Optional[str] = None

@dataclass
class IndexSuggestion:
    """索引建议"""
    table_name: str
    columns: List[str]
    index_type: str
    estimated_improvement: float
    reason: str

class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self, max_query_history: int = 1000):
        self.max_query_history = max_query_history
        self.query_history = deque(maxlen=max_query_history)
        self.query_stats = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0,
            "error_count": 0,
            "last_executed": None
        })
        
        # 慢查询阈值（秒）
        self.slow_query_threshold = 1.0
        self.slow_queries = deque(maxlen=100)
        
        # 连接池统计
        self.connection_stats = {
            "active_connections": 0,
            "total_connections": 0,
            "connection_errors": 0,
            "avg_connection_time": 0.0
        }
        
        # 索引建议
        self.index_suggestions = []
        
    def record_query(self, query: str, execution_time: float, 
                    rows_affected: int = 0, success: bool = True, 
                    error_message: Optional[str] = None):
        """记录查询执行"""
        query_hash = self._hash_query(query)
        
        # 创建查询指标
        metrics = QueryMetrics(
            query_hash=query_hash,
            query_text=query,
            execution_time=execution_time,
            rows_affected=rows_affected,
            timestamp=datetime.now().isoformat(),
            success=success,
            error_message=error_message
        )
        
        # 添加到历史记录
        self.query_history.append(metrics)
        
        # 更新统计信息
        stats = self.query_stats[query_hash]
        stats["count"] += 1
        stats["last_executed"] = metrics.timestamp
        
        if success:
            stats["total_time"] += execution_time
            stats["avg_time"] = stats["total_time"] / stats["count"]
            stats["min_time"] = min(stats["min_time"], execution_time)
            stats["max_time"] = max(stats["max_time"], execution_time)
        else:
            stats["error_count"] += 1
        
        # 检查慢查询
        if execution_time > self.slow_query_threshold:
            self.slow_queries.append(metrics)
            logger.warning(f"Slow query detected: {execution_time:.3f}s - {query[:100]}...")
    
    def _hash_query(self, query: str) -> str:
        """生成查询哈希"""
        # 标准化查询（移除空格、转小写等）
        normalized = ' '.join(query.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def get_slow_queries(self, limit: int = 10) -> List[QueryMetrics]:
        """获取慢查询列表"""
        sorted_queries = sorted(
            self.slow_queries, 
            key=lambda q: q.execution_time, 
            reverse=True
        )
        return sorted_queries[:limit]
    
    def get_frequent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取频繁执行的查询"""
        sorted_stats = sorted(
            self.query_stats.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        result = []
        for query_hash, stats in sorted_stats[:limit]:
            # 找到对应的查询文本
            query_text = "Unknown"
            for metrics in reversed(self.query_history):
                if metrics.query_hash == query_hash:
                    query_text = metrics.query_text
                    break
            
            result.append({
                "query_hash": query_hash,
                "query_text": query_text[:200] + "..." if len(query_text) > 200 else query_text,
                "stats": stats
            })
        
        return result
    
    def analyze_query_patterns(self) -> Dict[str, Any]:
        """分析查询模式"""
        if not self.query_history:
            return {"error": "No query history available"}
        
        # 按时间分组统计
        hourly_stats = defaultdict(int)
        table_access = defaultdict(int)
        operation_types = defaultdict(int)
        
        for metrics in self.query_history:
            # 按小时统计
            hour = datetime.fromisoformat(metrics.timestamp).hour
            hourly_stats[hour] += 1
            
            # 分析查询类型
            query_lower = metrics.query_text.lower().strip()
            if query_lower.startswith('select'):
                operation_types['SELECT'] += 1
            elif query_lower.startswith('insert'):
                operation_types['INSERT'] += 1
            elif query_lower.startswith('update'):
                operation_types['UPDATE'] += 1
            elif query_lower.startswith('delete'):
                operation_types['DELETE'] += 1
            else:
                operation_types['OTHER'] += 1
            
            # 提取表名（简单实现）
            self._extract_table_names(metrics.query_text, table_access)
        
        # 计算平均执行时间
        successful_queries = [m for m in self.query_history if m.success]
        avg_execution_time = 0.0
        if successful_queries:
            avg_execution_time = sum(m.execution_time for m in successful_queries) / len(successful_queries)
        
        return {
            "total_queries": len(self.query_history),
            "successful_queries": len(successful_queries),
            "failed_queries": len(self.query_history) - len(successful_queries),
            "avg_execution_time": avg_execution_time,
            "slow_queries_count": len(self.slow_queries),
            "hourly_distribution": dict(hourly_stats),
            "operation_types": dict(operation_types),
            "most_accessed_tables": dict(sorted(table_access.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def _extract_table_names(self, query: str, table_access: Dict[str, int]):
        """提取查询中的表名（简单实现）"""
        query_lower = query.lower()
        
        # 简单的表名提取
        keywords = ['from', 'join', 'update', 'into']
        for keyword in keywords:
            if keyword in query_lower:
                parts = query_lower.split(keyword)
                if len(parts) > 1:
                    # 获取关键词后的第一个单词作为表名
                    table_part = parts[1].strip().split()[0]
                    # 清理表名
                    table_name = table_part.replace('`', '').replace('"', '').replace("'", '')
                    if table_name and not table_name in ['(', 'select', 'where']:
                        table_access[table_name] += 1
    
    def suggest_indexes(self) -> List[IndexSuggestion]:
        """生成索引建议"""
        suggestions = []
        
        # 分析慢查询
        for metrics in self.slow_queries:
            query_lower = metrics.query_text.lower()
            
            # 简单的WHERE子句分析
            if 'where' in query_lower:
                where_part = query_lower.split('where')[1].split('order by')[0].split('group by')[0]
                
                # 提取可能的索引列
                potential_columns = self._extract_where_columns(where_part)
                
                if potential_columns:
                    # 提取表名
                    table_name = self._extract_main_table(query_lower)
                    
                    if table_name:
                        suggestion = IndexSuggestion(
                            table_name=table_name,
                            columns=potential_columns,
                            index_type="BTREE",
                            estimated_improvement=metrics.execution_time * 0.5,  # 估算50%改进
                            reason=f"Slow query optimization (current: {metrics.execution_time:.3f}s)"
                        )
                        suggestions.append(suggestion)
        
        # 去重
        unique_suggestions = []
        seen = set()
        for suggestion in suggestions:
            key = (suggestion.table_name, tuple(suggestion.columns))
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        self.index_suggestions = unique_suggestions
        return unique_suggestions
    
    def _extract_where_columns(self, where_clause: str) -> List[str]:
        """从WHERE子句提取列名"""
        columns = []
        
        # 简单的列名提取
        import re
        
        # 查找 column = value 或 column IN (...) 等模式
        patterns = [
            r'(\w+)\s*=',
            r'(\w+)\s+in\s*\(',
            r'(\w+)\s*<',
            r'(\w+)\s*>',
            r'(\w+)\s+like'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, where_clause, re.IGNORECASE)
            columns.extend(matches)
        
        # 去重并过滤
        unique_columns = []
        for col in columns:
            if col not in ['and', 'or', 'not', 'null'] and col not in unique_columns:
                unique_columns.append(col)
        
        return unique_columns[:3]  # 最多3列的复合索引
    
    def _extract_main_table(self, query: str) -> Optional[str]:
        """提取主表名"""
        if 'from' in query:
            from_part = query.split('from')[1].strip()
            table_name = from_part.split()[0]
            return table_name.replace('`', '').replace('"', '').replace("'", '')
        return None
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """生成优化报告"""
        patterns = self.analyze_query_patterns()
        slow_queries = self.get_slow_queries()
        frequent_queries = self.get_frequent_queries()
        index_suggestions = self.suggest_indexes()
        
        # 计算优化潜力
        total_slow_time = sum(q.execution_time for q in slow_queries)
        estimated_savings = total_slow_time * 0.6  # 估算60%的时间节省
        
        return {
            "timestamp": datetime.now().isoformat(),
            "query_patterns": patterns,
            "performance_issues": {
                "slow_queries_count": len(slow_queries),
                "total_slow_time": total_slow_time,
                "estimated_time_savings": estimated_savings
            },
            "top_slow_queries": [asdict(q) for q in slow_queries[:5]],
            "frequent_queries": frequent_queries[:5],
            "index_suggestions": [asdict(s) for s in index_suggestions],
            "recommendations": self._generate_recommendations(patterns, slow_queries, index_suggestions)
        }
    
    def _generate_recommendations(self, patterns: Dict, slow_queries: List, 
                                index_suggestions: List) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if len(slow_queries) > 0:
            recommendations.append(f"发现 {len(slow_queries)} 个慢查询，建议优化")
        
        if len(index_suggestions) > 0:
            recommendations.append(f"建议添加 {len(index_suggestions)} 个索引以提升性能")
        
        if patterns.get("failed_queries", 0) > 0:
            recommendations.append(f"有 {patterns['failed_queries']} 个查询失败，需要检查")
        
        # 检查查询频率
        total_queries = patterns.get("total_queries", 0)
        if total_queries > 1000:
            recommendations.append("查询频率较高，考虑增加缓存或读写分离")
        
        # 检查操作类型分布
        operation_types = patterns.get("operation_types", {})
        select_ratio = operation_types.get("SELECT", 0) / total_queries if total_queries > 0 else 0
        
        if select_ratio < 0.7:
            recommendations.append("写操作比例较高，考虑优化写入性能")
        
        return recommendations

# 全局数据库优化器实例
db_optimizer = DatabaseOptimizer()

def record_database_query(query: str, execution_time: float, **kwargs):
    """记录数据库查询（全局函数）"""
    db_optimizer.record_query(query, execution_time, **kwargs)

def get_database_optimization_report():
    """获取数据库优化报告（全局函数）"""
    return db_optimizer.get_optimization_report()
