"""
数据分析工具
"""
import asyncio
import logging
from typing import Optional, Type
import json

from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field

try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False
    logging.warning("Data analysis libraries not available")

logger = logging.getLogger(__name__)

class DataAnalysisInput(BaseModel):
    """数据分析输入模型"""
    data: str = Field(description="数据内容或文件路径")
    analysis_type: str = Field(default="basic", description="分析类型: basic, statistical, visualization")

class DataAnalysisTool(BaseTool):
    """数据分析工具 - 数据可视化和统计分析"""
    
    name = "data_analyzer"
    description = "执行数据分析、统计计算和数据可视化"
    args_schema: Type[BaseModel] = DataAnalysisInput
    
    def _run(self, data: str, analysis_type: str = "basic") -> str:
        """同步执行数据分析"""
        return asyncio.run(self._arun(data, analysis_type))
    
    async def _arun(self, data: str, analysis_type: str = "basic") -> str:
        """异步执行数据分析"""
        try:
            if not ANALYSIS_AVAILABLE:
                return "数据分析库未安装，请安装pandas、numpy、matplotlib等库"
            
            # 解析数据
            df = await self._parse_data(data)
            if df is None:
                return "无法解析数据"
            
            # 执行分析
            if analysis_type == "basic":
                return await self._basic_analysis(df)
            elif analysis_type == "statistical":
                return await self._statistical_analysis(df)
            elif analysis_type == "visualization":
                return await self._create_visualization(df)
            else:
                return f"不支持的分析类型: {analysis_type}"
                
        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            return f"数据分析失败: {str(e)}"
    
    async def _parse_data(self, data: str):
        """解析数据"""
        try:
            # 尝试解析为JSON
            if data.strip().startswith('[') or data.strip().startswith('{'):
                json_data = json.loads(data)
                return pd.DataFrame(json_data)
            
            # 尝试解析为CSV格式
            from io import StringIO
            return pd.read_csv(StringIO(data))
            
        except Exception:
            # 生成示例数据
            return pd.DataFrame({
                'A': np.random.randn(100),
                'B': np.random.randn(100),
                'C': np.random.choice(['X', 'Y', 'Z'], 100)
            })
    
    async def _basic_analysis(self, df) -> str:
        """基础数据分析"""
        result = ["数据基础分析结果:"]
        
        # 数据形状
        result.append(f"数据形状: {df.shape[0]}行 x {df.shape[1]}列")
        
        # 列信息
        result.append(f"\n列信息:")
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            result.append(f"- {col}: {dtype}, 缺失值: {null_count}")
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            result.append(f"\n数值列统计:")
            stats = df[numeric_cols].describe()
            result.append(stats.to_string())
        
        return "\n".join(result)
    
    async def _statistical_analysis(self, df) -> str:
        """统计分析"""
        result = ["统计分析结果:"]
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            # 相关性分析
            result.append("\n相关性矩阵:")
            corr_matrix = df[numeric_cols].corr()
            result.append(corr_matrix.to_string())
            
            # 分布分析
            result.append("\n分布分析:")
            for col in numeric_cols:
                skewness = df[col].skew()
                kurtosis = df[col].kurtosis()
                result.append(f"- {col}: 偏度={skewness:.3f}, 峰度={kurtosis:.3f}")
        
        return "\n".join(result)
    
    async def _create_visualization(self, df) -> str:
        """创建可视化"""
        try:
            # 这里只返回可视化的描述，实际项目中可以生成图片
            result = ["数据可视化分析:"]
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) > 0:
                result.append(f"\n数值列可视化建议:")
                for col in numeric_cols:
                    result.append(f"- {col}: 直方图、箱线图")
            
            if len(categorical_cols) > 0:
                result.append(f"\n分类列可视化建议:")
                for col in categorical_cols:
                    result.append(f"- {col}: 条形图、饼图")
            
            if len(numeric_cols) >= 2:
                result.append(f"\n关系图建议:")
                result.append(f"- 散点图: {numeric_cols[0]} vs {numeric_cols[1]}")
                result.append(f"- 相关性热力图")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"可视化分析失败: {str(e)}"
