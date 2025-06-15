# 🤝 贡献指南

感谢您对多模态AI Agent项目的关注！我们欢迎各种形式的贡献，包括但不限于代码、文档、测试、问题报告和功能建议。

## 📋 目录

- [贡献方式](#贡献方式)
- [开发环境搭建](#开发环境搭建)
- [贡献流程](#贡献流程)
- [代码规范](#代码规范)
- [测试要求](#测试要求)
- [文档贡献](#文档贡献)
- [问题报告](#问题报告)
- [功能建议](#功能建议)
- [代码审查](#代码审查)
- [社区准则](#社区准则)

## 🎯 贡献方式

### 代码贡献
- 🐛 修复Bug
- ✨ 新增功能
- ⚡ 性能优化
- 🔧 代码重构
- 🧪 增加测试

### 文档贡献
- 📚 改进文档
- 🌍 翻译文档
- 📝 编写教程
- 💡 添加示例

### 其他贡献
- 🐛 报告问题
- 💭 功能建议
- 🎨 UI/UX改进
- 📊 性能测试

## 🔧 开发环境搭建

### 前置要求

- Python 3.8+
- Git 2.0+
- Docker 20.0+ (可选)

### 快速开始

```bash
# 1. Fork项目到您的GitHub账户

# 2. 克隆您的Fork
git clone https://github.com/YOUR_USERNAME/ai-agent.git
cd ai-agent

# 3. 添加上游仓库
git remote add upstream https://github.com/luoxiao6645/ai-agent.git

# 4. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 5. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 6. 配置环境变量
cp .env.example .env
# 编辑 .env 文件设置必要的配置

# 7. 运行测试验证环境
python run_test_suite.py
```

### 开发工具配置

#### VS Code配置

创建 `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### Git钩子配置

```bash
# 安装pre-commit钩子
pip install pre-commit
pre-commit install

# 手动运行检查
pre-commit run --all-files
```

## 🔄 贡献流程

### 1. 准备工作

```bash
# 同步上游代码
git fetch upstream
git checkout main
git merge upstream/main

# 创建功能分支
git checkout -b feature/your-feature-name
```

### 2. 开发阶段

```bash
# 进行开发
# ... 编写代码 ...

# 运行测试
python run_test_suite.py

# 代码质量检查
python -m flake8 .
python -m black .
python -m isort .
python -m mypy .
```

### 3. 提交代码

```bash
# 添加更改
git add .

# 提交代码（遵循提交信息规范）
git commit -m "feat: add new multimodal processing feature

- Add support for video processing
- Improve image analysis accuracy
- Update API documentation

Closes #123"

# 推送到您的Fork
git push origin feature/your-feature-name
```

### 4. 创建Pull Request

1. 在GitHub上访问您的Fork
2. 点击 "Compare & pull request"
3. 填写PR模板
4. 等待代码审查

### 5. 响应反馈

- 及时回应审查意见
- 根据反馈修改代码
- 保持PR更新

## 📝 代码规范

### Python代码风格

我们遵循PEP 8规范，并使用以下工具：

- **Black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码检查
- **mypy**: 类型检查

### 代码示例

```python
"""
模块文档字符串
描述模块的功能和用途
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union

from external_library import SomeClass

logger = logging.getLogger(__name__)


class ExampleClass:
    """示例类，展示代码规范"""
    
    def __init__(self, name: str, config: Optional[Dict] = None) -> None:
        """
        初始化方法
        
        Args:
            name: 实例名称
            config: 可选配置字典
        """
        self.name = name
        self.config = config or {}
        self._private_var = "private"
    
    async def process_data(self, data: List[str]) -> Dict[str, str]:
        """
        处理数据的异步方法
        
        Args:
            data: 待处理的数据列表
            
        Returns:
            处理结果字典
            
        Raises:
            ValueError: 当数据格式不正确时
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        results = {}
        for item in data:
            try:
                processed_item = await self._process_single_item(item)
                results[item] = processed_item
            except Exception as e:
                logger.error(f"Failed to process item {item}: {e}")
                results[item] = "error"
        
        return results
    
    async def _process_single_item(self, item: str) -> str:
        """私有方法处理单个项目"""
        # 模拟异步处理
        await asyncio.sleep(0.01)
        return item.upper()
```

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### 类型说明

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化
- `ci`: CI/CD相关

#### 示例

```bash
# 新功能
git commit -m "feat(agent): add multimodal processing support"

# 修复bug
git commit -m "fix(api): resolve session timeout issue"

# 文档更新
git commit -m "docs: update API documentation"

# 破坏性变更
git commit -m "feat!: change API response format

BREAKING CHANGE: API response format has changed from array to object"
```

## 🧪 测试要求

### 测试覆盖率

- 新功能必须包含测试
- 测试覆盖率不低于80%
- 关键功能测试覆盖率应达到95%+

### 测试类型

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestNewFeature:
    """新功能测试类"""
    
    @pytest.fixture
    def mock_dependency(self):
        """测试夹具"""
        return Mock()
    
    @pytest.mark.asyncio
    async def test_async_function(self, mock_dependency):
        """测试异步函数"""
        # 准备
        mock_dependency.some_method.return_value = "expected_result"
        
        # 执行
        result = await your_async_function(mock_dependency)
        
        # 验证
        assert result == "expected_result"
        mock_dependency.some_method.assert_called_once()
    
    def test_edge_case(self):
        """测试边界情况"""
        with pytest.raises(ValueError, match="Invalid input"):
            your_function(invalid_input)
    
    @pytest.mark.parametrize("input_value,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
        ("test3", "result3"),
    ])
    def test_multiple_inputs(self, input_value, expected):
        """参数化测试"""
        result = your_function(input_value)
        assert result == expected
```

### 运行测试

```bash
# 运行所有测试
python run_test_suite.py

# 运行特定测试
python -m pytest tests/unit/test_your_feature.py -v

# 生成覆盖率报告
python -m pytest --cov=. --cov-report=html

# 性能测试
python -m pytest tests/performance/ -v
```

## 📚 文档贡献

### 文档类型

- **API文档**: 接口说明和示例
- **用户指南**: 使用教程和最佳实践
- **开发文档**: 架构设计和开发指南
- **部署文档**: 部署和运维指南

### 文档规范

```markdown
# 标题

简短的描述段落。

## 二级标题

### 代码示例

```python
# 代码示例应该完整且可运行
def example_function():
    return "Hello, World!"
```

### 注意事项

> **注意**: 重要信息使用引用块突出显示

### 链接和引用

- [内部链接](./other-doc.md)
- [外部链接](https://example.com)
```

## 🐛 问题报告

### 报告模板

使用GitHub Issues模板报告问题：

```markdown
## 问题描述
简要描述遇到的问题

## 重现步骤
1. 执行操作A
2. 执行操作B
3. 观察到错误

## 期望行为
描述期望的正确行为

## 实际行为
描述实际发生的行为

## 环境信息
- 操作系统: [e.g. Ubuntu 20.04]
- Python版本: [e.g. 3.9.0]
- 项目版本: [e.g. v1.1.0]

## 错误日志
```
粘贴相关的错误日志
```

## 附加信息
其他可能有用的信息
```

### 问题标签

- `bug`: 确认的bug
- `enhancement`: 功能增强
- `question`: 问题咨询
- `documentation`: 文档相关
- `good first issue`: 适合新贡献者
- `help wanted`: 需要帮助

## 💡 功能建议

### 建议模板

```markdown
## 功能描述
简要描述建议的功能

## 使用场景
描述什么情况下需要这个功能

## 详细设计
详细描述功能的实现方案

## 替代方案
是否考虑过其他实现方式

## 附加信息
其他相关信息
```

## 👀 代码审查

### 审查清单

#### 功能性
- [ ] 功能是否按预期工作
- [ ] 边界条件是否处理正确
- [ ] 错误处理是否完善

#### 代码质量
- [ ] 代码是否清晰易读
- [ ] 是否遵循项目规范
- [ ] 是否有适当的注释

#### 测试
- [ ] 是否包含足够的测试
- [ ] 测试是否覆盖主要场景
- [ ] 测试是否能正确运行

#### 性能
- [ ] 是否有性能问题
- [ ] 是否需要优化
- [ ] 是否影响现有性能

#### 安全
- [ ] 是否有安全漏洞
- [ ] 输入验证是否充分
- [ ] 敏感信息是否保护

### 审查礼仪

- 保持建设性和友好的语调
- 提供具体的改进建议
- 认可好的代码和想法
- 及时回应审查请求

## 🌟 社区准则

### 行为准则

我们致力于为所有人提供友好、安全和欢迎的环境，无论：

- 性别、性别认同和表达
- 性取向
- 残疾
- 外貌
- 身体大小
- 种族
- 年龄
- 宗教

### 期望行为

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不当行为

- 使用性化的语言或图像
- 人身攻击或政治攻击
- 公开或私下骚扰
- 未经明确许可发布他人的私人信息
- 其他在专业环境中不当的行为

## 📞 获取帮助

如果您在贡献过程中遇到问题，可以通过以下方式获取帮助：

- 💬 [GitHub Discussions](https://github.com/luoxiao6645/ai-agent/discussions)
- 🐛 [GitHub Issues](https://github.com/luoxiao6645/ai-agent/issues)
- 📧 邮件: contribute@ai-agent.com
- 📚 [开发指南](./docs/DEVELOPMENT_GUIDE.md)

## 🙏 致谢

感谢所有为项目做出贡献的开发者！您的贡献让这个项目变得更好。

---

*贡献指南版本: v1.1.0 | 最后更新: 2025-06-15*
