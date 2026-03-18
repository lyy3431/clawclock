# 🤝 贡献指南 (Contributing Guide)

欢迎为 ClawClock 项目做出贡献！本指南将帮助你快速上手。

---

## 📑 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [代码风格规范](#代码风格规范)
- [提交 Issue](#提交-issue)
- [提交 Pull Request](#提交-pull-request)
- [代码审查流程](#代码审查流程)

---

## 📜 行为准则

本项目采用 [贡献者公约](https://www.contributor-covenant.org/) 作为行为准则。  
请尊重所有参与者，营造开放、友好的社区环境。

**核心价值观：**
- 尊重他人，包容多样
- 建设性反馈，对事不对人
- 乐于助人，分享知识
- 保持耐心，理解新手

---

## 🚀 如何贡献

### 你可以贡献什么？

- 🐛 报告 Bug
- 💡 提议新功能
- 📝 改进文档
- 🎨 设计 UI/主题
- 🔧 提交代码修复
- ⚡ 性能优化
- 🌍 翻译本地化
- 🧪 编写测试用例

### 贡献流程概览

```
1. Fork 项目
       ↓
2. 创建分支
       ↓
3. 进行修改
       ↓
4. 提交更改
       ↓
5. 推送分支
       ↓
6. 创建 Pull Request
       ↓
7. 代码审查
       ↓
8. 合并入主分支
```

---

## 💻 开发环境设置

### 前置要求

- Python 3.7+
- Git
- pip 或 pipenv

### 步骤 1: Fork 项目

在 GitHub 上点击 "Fork" 按钮，创建你自己的副本。

### 步骤 2: 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/clawclock.git
cd clawclock
```

### 步骤 3: 添加上游仓库

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/clawclock.git
git fetch upstream
```

### 步骤 4: 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（如有）
pip install -r requirements-dev.txt
```

### 步骤 5: 验证安装

```bash
# 运行应用
python3 clock.py

# 运行测试（如有）
python3 -m pytest tests/
```

---

## 📐 代码风格规范

### Python 代码规范

遵循 [PEP 8](https://pep8.org/) 编码规范。

**关键要点：**

1. **缩进**: 使用 4 个空格，不使用 Tab
2. **行宽**: 最大 100 字符
3. **导入顺序**:
   ```python
   # 标准库
   import os
   import sys
   
   # 第三方库
   import pytz
   import tkinter as tk
   
   # 本地导入
   from .utils import helper
   ```

4. **命名规范**:
   ```python
   # 类名 - 大驼峰
   class ClockDisplay:
       pass
   
   # 函数和变量 - 小写 + 下划线
   def update_clock():
       pass
   
   # 常量 - 全大写 + 下划线
   DEFAULT_REFRESH_RATE = 1000
   
   # 私有变量 - 单下划线前缀
   self._internal_state = None
   ```

5. **函数注释**:
   ```python
   def draw_digit(self, digit: int, x_offset: int) -> None:
       """
       绘制 7 段数码管数字
       
       Args:
           digit: 要绘制的数字 (0-9)
           x_offset: 数字左侧 X 坐标偏移量
       
       Returns:
           None
       
       Example:
           >>> self.draw_digit(5, 100)
       """
       pass
   ```

### 提交信息格式

遵循 [约定式提交](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**
```
feat(timezone): 添加悉尼时区支持

- 在时区列表中添加 Australia/Sydney
- 更新时区映射配置
- 添加相关测试用例

Closes #42
```

```
fix(display): 修复数字时钟高 DPI 模糊问题

调整 canvas 缩放因子以适配高分辨率屏幕

Fixes #38
```

---

## 🐛 提交 Issue

### Issue 模板

创建 Issue 时，请包含以下信息：

**Bug 报告：**
```markdown
### 问题描述
清晰简洁地描述问题是什么。

### 复现步骤
1. 运行 '...'
2. 点击 '...'
3. 观察到 '...'

### 预期行为
应该发生什么。

### 截图
如适用，添加截图帮助说明。

### 环境信息
- OS: [如 Ubuntu 22.04]
- Python 版本：[如 3.10.0]
- ClawClock 版本：[如 v1.1.0]

### 日志
```bash
# 附上相关错误日志
```

### 其他信息
任何你认为有帮助的额外信息。
```

**功能请求：**
```markdown
### 功能描述
清晰简洁地描述你想要的功能。

### 使用场景
为什么需要这个功能？能解决什么问题？

### 实现建议
如果有实现思路，请分享。

### 替代方案
考虑过哪些其他解决方案？

### 其他信息
任何你认为有帮助的额外信息。
```

### Issue 标签

- 🐛 `bug`: 错误修复
- ✨ `enhancement`: 功能改进
- 📚 `documentation`: 文档相关
- 🧪 `testing`: 测试相关
- 🎨 `design`: UI/UX 相关
- 🚀 `performance`: 性能优化
- ❓ `question`: 问题咨询
- 📌 `good first issue`: 适合新手

---

## 🔀 提交 Pull Request

### 步骤 1: 创建分支

从最新的主分支创建功能分支：

```bash
# 确保主分支最新
git checkout main
git pull upstream main

# 创建并切换到新分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/issue-42
```

**分支命名规范：**
- `feature/xxx`: 新功能
- `fix/xxx`: Bug 修复
- `docs/xxx`: 文档更新
- `refactor/xxx`: 重构
- `test/xxx`: 测试相关

### 步骤 2: 进行修改

- 保持更改聚焦，一个 PR 只做一件事
- 编写或更新测试
- 更新文档
- 确保代码通过所有检查

### 步骤 3: 运行检查

```bash
# 代码格式化
black clock.py

# 代码检查
flake8 clock.py

# 类型检查（如使用 mypy）
mypy clock.py

# 运行测试
python3 -m pytest tests/
```

### 步骤 4: 提交更改

```bash
# 添加更改
git add .

# 提交（使用规范的提交信息）
git commit -m "feat(timezone): 添加悉尼时区支持

- 在时区列表中添加 Australia/Sydney
- 更新时区映射配置

Closes #42"
```

### 步骤 5: 推送分支

```bash
git push origin feature/your-feature-name
```

### 步骤 6: 创建 Pull Request

1. 访问你的 Fork 仓库
2. 点击 "Compare & pull request"
3. 填写 PR 描述
4. 关联相关 Issue
5. 选择 Reviewers
6. 提交 PR

### PR 模板

```markdown
## 描述
简要描述此 PR 的目的。

## 相关 Issue
Closes #XX

## 更改类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 重构
- [ ] 性能优化
- [ ] 测试

## 测试
- [ ] 已添加/更新测试
- [ ] 所有测试通过
- [ ] 手动测试完成

## 截图
如适用，添加前后对比截图。

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 已更新文档
- [ ] 提交信息规范
- [ ] 无合并冲突
```

---

## 🔍 代码审查流程

### 审查标准

1. **功能正确性**: 代码是否按预期工作
2. **代码质量**: 是否遵循编码规范
3. **性能影响**: 是否有性能问题
4. **测试覆盖**: 是否有适当测试
5. **文档完整**: 是否更新相关文档

### 审查反馈

- 建设性意见，避免批评语气
- 指出问题的同时提供改进建议
- 区分 "必须修改" 和 "建议修改"
- 及时响应审查意见

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

感谢所有为 ClawClock 做出贡献的开发者！

每一位贡献者都让这个项目变得更好。❤️

---

*最后更新：2026-03-17*  
*ClawClock 版本：v1.1.0*
