# 🛠️ ClawClock 开发指南

本文档提供 ClawClock v1.6.0+ 的开发环境搭建、代码规范、测试运行和提交流程指南。

---

## 📑 目录

1. [开发环境搭建](#1-开发环境搭建)
2. [代码规范](#2-代码规范)
3. [测试运行](#3-测试运行)
4. [提交流程](#4-提交流程)
5. [模块开发指南](#5-模块开发指南)
6. [常见问题](#6-常见问题)

---

## 1. 开发环境搭建

### 1.1 系统要求

| 组件 | 要求 | 说明 |
|------|------|------|
| 操作系统 | Linux | Debian/Ubuntu/Arch/Fedora |
| Python | 3.8+ | 推荐 3.10+ |
| Tkinter | 内置 | Python 内置 GUI 库 |
| Git | 最新 | 版本控制 |

### 1.2 安装依赖

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-tk python3-tz git

# Arch Linux
sudo pacman -S python tk python-tz git

# Fedora
sudo dnf install python3 python3-tkinter python3-dateutil git
```

### 1.3 克隆项目

```bash
# 克隆仓库
git clone https://github.com/lyy3431/clawclock.git
cd clawclock

# 查看项目结构
ls -la
```

### 1.4 验证安装

```bash
# 运行应用
python3 clock.py

# 运行测试
bash run_tests.sh
```

### 1.5 开发工具推荐

**代码编辑器：**
- VS Code（推荐）+ Python 扩展
- PyCharm
- Vim/Neovim + coc.nvim

**推荐的 VS Code 设置：**
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "files.encoding": "utf-8"
}
```

---

## 2. 代码规范

### 2.1 Python 代码风格

遵循 [PEP 8](https://pep8.org/) 规范，并采用以下约定：

#### 命名规范

```python
# 类名：大驼峰
class ClockApp:
    pass

class BreathLightEffect:
    pass

# 函数和变量：小写 + 下划线
def update_clock():
    pass

config_manager = ConfigManager()

# 常量：大写 + 下划线
WINDOW_WIDTH = 600
DEFAULT_THEME = "dark"

# 私有变量：单下划线前缀
_internal_state = None

# 私有方法：单下划线前缀
def _internal_method():
    pass
```

#### 类型注解

所有公共函数必须添加类型注解：

```python
from typing import Dict, List, Optional, Tuple, Any, Callable

def get_config(key: str, default: Any = None) -> Any:
    """获取配置项"""
    pass

def validate_time_format(time_str: str) -> bool:
    """验证时间格式"""
    pass

def process_alarms(alarms: List[Dict[str, Any]]) -> List[str]:
    """处理闹钟列表"""
    pass
```

#### 文档字符串

所有模块、类、公共函数必须有文档字符串：

```python
"""
模块说明
"""

class ConfigManager:
    """
    配置管理器
    
    负责加载、保存和管理应用配置。
    
    Attributes:
        config_file: 配置文件路径
        config: 配置字典
    """
    
    def load(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
            
        Raises:
            ConfigError: 配置文件加载失败
        """
        pass
```

### 2.2 代码组织

#### 导入顺序

```python
# 1. 标准库
import json
import os
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

# 2. 第三方库
import tkinter as tk
from tkinter import ttk

# 3. 本地模块
from config.settings import get_config_manager
from effects.breath_light import BreathLightEffect
from utils.logger import info, error
```

#### 文件结构

```python
#!/usr/bin/env python3
"""
模块说明文档
"""

# 导入语句

# 常量定义
CONSTANT = "value"

# 类定义
class MyClass:
    pass

# 函数定义
def my_function():
    pass

# 主程序入口
if __name__ == "__main__":
    main()
```

### 2.3 错误处理

使用统一的错误处理机制：

```python
from utils.errors import ClockError, ConfigError, safe_execute

# 方式 1：抛出异常
def load_config():
    if not os.path.exists(config_file):
        raise ConfigError("配置文件不存在", config_key="config_file")

# 方式 2：安全执行
result = safe_execute(
    lambda: risky_operation(),
    default=None,
    error_handler=lambda e: error(f"操作失败：{e}")
)

# 方式 3：try/except
try:
    config = json.load(f)
except json.JSONDecodeError as e:
    raise ConfigError(f"JSON 解析失败：{e}")
except IOError as e:
    raise ConfigError(f"文件读取失败：{e}", config_key="config_file")
```

### 2.4 日志记录

使用统一的日志系统：

```python
from utils.logger import info, warning, error, debug, set_context

# 设置上下文
set_context(module="clock", func="init")

# 记录日志
info("应用启动")
debug(f"配置加载：{config}")
warning("配置文件不存在，使用默认值")
error(f"初始化失败：{e}")
```

### 2.5 代码审查清单

提交前检查：

- [ ] 代码符合 PEP 8 规范
- [ ] 所有公共函数有类型注解
- [ ] 所有模块/类/函数有文档字符串
- [ ] 错误处理完善
- [ ] 日志记录适当
- [ ] 测试通过
- [ ] 无调试代码（print 等）
- [ ] 无未使用的导入

---

## 3. 测试运行

### 3.1 测试框架

ClawClock 使用 Python 内置的 `unittest` 框架。

### 3.2 运行测试

```bash
# 运行完整测试套件
bash run_tests.sh

# 详细输出模式
bash run_tests.sh -v

# 运行特定测试模块
python3 -m unittest tests.test_breath_light -v

# 运行特定测试用例
python3 -m unittest tests.test_breath_light.TestBreathLight.test_default_config -v
```

### 3.3 测试覆盖范围

| 模块 | 测试文件 | 用例数 | 说明 |
|------|----------|--------|------|
| 呼吸灯 | `test_breath_light.py` | 17 | 配置、效果、颜色转换 |
| 秒表 | `test_comprehensive.py` | 17 | 启动/停止/重置/计圈 |
| 倒计时 | `test_comprehensive.py` | 15 | 预设、自定义、状态 |
| 闹钟 | `test_comprehensive.py` | 7 | 创建、触发、重复 |
| 配置 | `test_comprehensive.py` | 5 | 加载、保存、合并 |
| 7 段显示 | `test_comprehensive.py` | 3 | 数字段定义 |
| 时区 | `test_comprehensive.py` | 2 | 数据结构验证 |
| **总计** | - | **146** | **100% 通过率** |

### 3.4 编写测试

#### 测试模板

```python
import unittest
from effects.breath_light import BreathLightEffect, BreathStyle


class TestBreathLight(unittest.TestCase):
    """呼吸灯效果测试"""
    
    def setUp(self):
        """测试前准备"""
        self.effect = BreathLightEffect()
    
    def tearDown(self):
        """测试后清理"""
        pass
    
    def test_default_config(self):
        """测试默认配置"""
        self.assertEqual(self.effect.config.frequency, 0.5)
        self.assertEqual(self.effect.config.intensity, 0.5)
        self.assertEqual(self.effect.config.style, BreathStyle.SOFT)
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = BreathLightConfig(frequency=1.0, intensity=0.8)
        effect = BreathLightEffect(config)
        self.assertEqual(effect.config.frequency, 1.0)
        self.assertEqual(effect.config.intensity, 0.8)


if __name__ == "__main__":
    unittest.main()
```

#### 测试命名规范

- 测试类：`Test<模块名>`，如 `TestBreathLight`
- 测试方法：`test_<功能>_<场景>`，如 `test_default_config`

#### 断言方法

```python
self.assertEqual(a, b)           # a == b
self.assertNotEqual(a, b)        # a != b
self.assertTrue(x)               # bool(x) is True
self.assertFalse(x)              # bool(x) is False
self.assertIs(a, b)              # a is b
self.assertIsNone(x)             # x is None
self.assertIn(a, b)              # a in b
self.assertIsInstance(a, b)      # isinstance(a, b)
self.assertRaises(Exception, f)  # f 抛出 Exception
```

### 3.5 测试最佳实践

1. **独立性**：每个测试用例独立，不依赖其他测试
2. **可重复**：测试结果可重复，无随机性
3. **快速**：单个测试用例运行时间 < 1 秒
4. **清晰**：测试名称清晰表达测试意图
5. **完整**：覆盖正常路径和异常路径

---

## 4. 提交流程

### 4.1 Git 工作流

采用 Feature Branch 工作流：

```bash
# 1. 创建功能分支
git checkout -b feature/your-feature-name

# 2. 开发和提交
git add .
git commit -m "feat: 添加新功能"

# 3. 推送到远程
git push origin feature/your-feature-name

# 4. 创建 Pull Request
# 在 GitHub 上创建 PR

# 5. 代码审查通过后合并
```

### 4.2 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

#### 类型（type）

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构（既不是新功能也不是修复）
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

#### 示例

```bash
# 新功能
git commit -m "feat: 添加呼吸灯效果模块"

# Bug 修复
git commit -m "fix: 修复主题切换后颜色不更新"

# 文档更新
git commit -m "docs: 更新 README 添加安装说明"

# 重构
git commit -m "refactor: 模块化重构配置管理"

# 测试
git commit -m "test: 添加呼吸灯效果单元测试"

# 带作用域
git commit -m "feat(breath_light): 添加 4 种呼吸灯风格"

# 带正文
git commit -m "fix: 修复倒计时暂停后继续异常

- 修复暂停状态未正确保存
- 修复继续后时间计算错误
- 添加相关测试用例

Closes #123"
```

### 4.3 分支命名

```
feature/xxx     # 新功能
fix/xxx         # Bug 修复
docs/xxx        # 文档更新
refactor/xxx    # 重构
test/xxx        # 测试
chore/xxx       # 杂项
hotfix/xxx      # 紧急修复
```

### 4.4 发布流程

```bash
# 1. 更新版本号
# 编辑相关文件更新版本号

# 2. 更新 CHANGELOG.md
# 添加新版本更新日志

# 3. 提交变更
git add .
git commit -m "chore: 发布 v1.6.0"

# 4. 打标签
git tag -a v1.6.0 -m "Release v1.6.0"

# 5. 推送标签
git push origin v1.6.0

# 6. 创建 GitHub Release
# 在 GitHub 上创建 Release，附上 CHANGELOG
```

---

## 5. 模块开发指南

### 5.1 创建新模块

#### 模块结构

```
clawclock/
└── your_module/
    ├── __init__.py      # 模块初始化
    ├── core.py          # 核心逻辑
    ├── config.py        # 配置
    └── utils.py         # 工具函数
```

#### __init__.py

```python
"""
你的模块说明
"""

from .core import YourClass
from .utils import helper_function

__all__ = ["YourClass", "helper_function"]
__version__ = "1.0.0"
```

### 5.2 扩展现有模块

#### 添加新配置项

```python
# config/settings.py
self.default_config = {
    # ... 现有配置
    "new_feature": {
        "enabled": True,
        "option": "default"
    }
}
```

#### 添加新异常类

```python
# utils/errors.py
class NewFeatureError(ClockError):
    """新功能错误"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(f"新功能错误：{message}")
        self.detail = detail
```

#### 添加新日志级别

```python
# utils/logger.py
def verbose(self, message: str, **kwargs) -> None:
    """详细日志"""
    self.logger.log(5, self._format_message(message))  # 5 < DEBUG
```

### 5.3 模块集成

#### 在主程序中使用模块

```python
# clock.py
from config.settings import get_config_manager
from effects.breath_light import BreathLightEffect
from utils.logger import info

class ClockApp:
    def __init__(self, root):
        # 获取配置
        self.config = get_config_manager()
        
        # 创建呼吸灯效果
        self.breath_effect = BreathLightEffect()
        
        # 记录日志
        info("应用初始化完成")
```

### 5.4 性能优化

#### 避免重复计算

```python
# ❌ 不好
def draw_frame(self):
    color = self.get_color()  # 每次都重新计算
    self.canvas.create_text(x, y, fill=color)

# ✅ 好
def draw_frame(self):
    if self._color_cache is None:
        self._color_cache = self.get_color()
    color = self._color_cache
    self.canvas.create_text(x, y, fill=color)
```

#### 使用缓存

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def hex_to_rgb(hex_color: str) -> tuple:
    """十六进制颜色转 RGB（带缓存）"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
```

#### 减少对象创建

```python
# ❌ 不好
for i in range(1000):
    result = SomeClass()  # 创建 1000 个对象

# ✅ 好
result = SomeClass()
for i in range(1000):
    result.update(i)  # 复用对象
```

---

## 6. 常见问题

### 6.1 开发环境问题

#### Q: tkinter 模块找不到

**A:** 安装 tkinter：
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Arch
sudo pacman -S tk

# Fedora
sudo dnf install python3-tkinter
```

#### Q: 时区数据库过时

**A:** 更新 tzdata：
```bash
sudo apt update && sudo apt install --reinstall tzdata
```

### 6.2 测试问题

#### Q: 测试失败

**A:** 检查：
1. 依赖是否安装完整
2. Python 版本是否符合要求
3. 测试文件是否有语法错误
4. 运行详细输出：`bash run_tests.sh -v`

#### Q: 如何添加新测试

**A:** 
1. 在 `tests/` 目录创建测试文件
2. 继承 `unittest.TestCase`
3. 方法名以 `test_` 开头
4. 在 `run_tests.sh` 中添加测试文件

### 6.3 提交问题

#### Q: 提交被拒绝

**A:** 检查：
1. 提交信息是否符合规范
2. 代码是否通过审查
3. 测试是否全部通过
4. 是否有冲突需要解决

#### Q: 如何修改最近提交

**A:**
```bash
# 修改最近提交信息
git commit --amend -m "新的提交信息"

# 添加遗漏的文件到最近提交
git add forgotten_file.py
git commit --amend --no-edit
```

### 6.4 性能问题

#### Q: 应用运行卡顿

**A:** 检查：
1. 刷新率是否过高（建议 50ms）
2. 是否有无限循环
3. 是否有内存泄漏
4. 使用 `time` 命令分析性能

#### Q: 内存占用过高

**A:** 检查：
1. 是否有未释放的资源
2. 是否有过大的缓存
3. 使用 `tracemalloc` 分析内存

---

## 📚 参考资源

- [Python 官方文档](https://docs.python.org/3/)
- [PEP 8 风格指南](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [unittest 文档](https://docs.python.org/3/library/unittest.html)
- [Tkinter 文档](https://docs.python.org/3/library/tkinter.html)

---

*开发指南版本：v1.6.0*  
*最后更新：2026-03-19*
