# 🤝 贡献指南

欢迎为 ClawClock 项目做出贡献！

---

## 📑 目录

1. [行为准则](#-行为准则)
2. [贡献方式](#-贡献方式)
3. [开发环境](#-开发环境)
4. [代码规范](#-代码规范)
5. [提交 Issue](#-提交-issue)
6. [提交 PR](#-提交-pull-request)
7. [代码审查](#-代码审查)

---

## 📜 行为准则

本项目遵循 [贡献者公约](https://www.contributor-covenant.org/)，核心价值观：

| 价值观 | 说明 |
|--------|------|
| 尊重包容 | 尊重所有参与者，包容多样性 |
| 建设性 | 对事不对人，提供建设性反馈 |
| 分享 | 乐于助人，分享知识 |
| 耐心 | 理解新手，保持耐心 |

---

## 🚀 贡献方式

你可以贡献：

| 类型 | 说明 |
|------|------|
| 🐛 **Bug 报告** | 发现问题，提交 Issue |
| 💡 **功能建议** | 提议新功能 |
| 📝 **文档改进** | 修正错误、补充内容 |
| 🎨 **UI/主题** | 设计新主题或界面优化 |
| 🔧 **代码修复** | 提交代码修复 |
| ⚡ **性能优化** | 提升运行效率 |
| 🌍 **翻译** | 本地化翻译 |
| 🧪 **测试用例** | 编写或补充测试 |

### 贡献流程

```
Fork → 克隆 → 创建分支 → 修改 → 提交 → 推送 → PR → 审查 → 合并
```

---

## 💻 开发环境

### 前置要求

- Python 3.7+
- Git
- pip 或 pipenv

### 快速设置

```bash
# 1. Fork 后克隆
git clone https://github.com/YOUR_USERNAME/clawclock.git
cd clawclock

# 2. 添加上游仓库
git remote add upstream https://github.com/ORIGINAL_OWNER/clawclock.git
git fetch upstream

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt

# 4. 验证
python3 clock.py
```

---

## 📐 代码规范

### Python 规范 (PEP 8)

| 规范 | 要求 |
|------|------|
| 缩进 | 4 空格，不用 Tab |
| 行宽 | 最大 100 字符 |
| 类名 | 大驼峰 `ClockDisplay` |
| 函数/变量 | 小写 + 下划线 `update_clock` |
| 常量 | 全大写 `DEFAULT_REFRESH_RATE` |
| 私有 | 单下划线前缀 `_internal_state` |

### 导入顺序

```python
# 标准库
import os
import sys

# 第三方
import pytz
import tkinter as tk

# 本地
from .utils import helper
```

### 提交信息格式

遵循 [约定式提交](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型：**

| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式 |
| `refactor` | 重构 |
| `perf` | 性能优化 |
| `test` | 测试 |
| `chore` | 构建/工具 |

**示例：**
```
feat(timezone): 添加悉尼时区支持

- 在时区列表中添加 Australia/Sydney
- 更新时区映射配置

Closes #42
```

---

## 🐛 提交 Issue

### Bug 报告模板

```markdown
### 问题描述
清晰简洁地描述问题

### 复现步骤
1. 运行 '...'
2. 点击 '...'
3. 观察到 '...'

### 预期行为
应该发生什么

### 环境信息
- OS: Ubuntu 22.04
- Python: 3.10.0
- ClawClock: v1.1.0

### 日志
```

### 功能请求模板

```markdown
### 功能描述
你想要的功能

### 使用场景
为什么需要这个功能

### 实现建议（可选）
如果有思路请分享
```

### Issue 标签

| 标签 | 说明 |
|------|------|
| 🐛 `bug` | 错误修复 |
| ✨ `enhancement` | 功能改进 |
| 📚 `documentation` | 文档 |
| 🧪 `testing` | 测试 |
| 🎨 `design` | UI/UX |
| 🚀 `performance` | 性能 |
| ❓ `question` | 咨询 |
| 📌 `good first issue` | 新手友好 |

---

## 🔀 提交 Pull Request

### 步骤

```bash
# 1. 创建分支
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name

# 2. 修改后运行检查
black clock.py
flake8 clock.py
python3 -m pytest tests/

# 3. 提交
git add .
git commit -m "feat(timezone): 添加悉尼时区支持

- 更新时区列表
- 添加测试用例

Closes #42"

# 4. 推送
git push origin feature/your-feature-name
```

### 分支命名

| 前缀 | 用途 |
|------|------|
| `feature/` | 新功能 |
| `fix/` | Bug 修复 |
| `docs/` | 文档 |
| `refactor/` | 重构 |
| `test/` | 测试 |

### PR 模板

```markdown
## 描述
PR 目的

## 相关 Issue
Closes #XX

## 更改类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 重构
- [ ] 性能优化

## 测试
- [ ] 已添加/更新测试
- [ ] 所有测试通过

## 检查清单
- [ ] 代码遵循规范
- [ ] 已更新文档
- [ ] 提交信息规范
- [ ] 无合并冲突
```

---

## 🔍 代码审查

### 审查标准

| 标准 | 说明 |
|------|------|
| 功能正确性 | 代码是否按预期工作 |
| 代码质量 | 是否遵循规范 |
| 性能影响 | 是否有性能问题 |
| 测试覆盖 | 是否有适当测试 |
| 文档完整 | 是否更新文档 |

### 合并条件

- ✅ 至少 1 个维护者批准
- ✅ 所有 CI 检查通过
- ✅ 无合并冲突
- ✅ 代码审查完成

---

## 📞 获取帮助

- 💬 在 Issue 中提问
- 📧 联系维护者
- 💭 参与讨论区

---

## 🙏 致谢

感谢所有贡献者！每一位贡献者都让 ClawClock 变得更好。❤️

---

*最后更新：2026-03-19 | ClawClock v1.5.1*
