# ClawClock 版本管理

## 自动版本更新机制

### 方法 1：自动递增 patch 版本

```bash
cd D:\CStudy\AItest\clawclock
python update_version.py
```

输出示例：
```
当前版本：1.6.4
新版本：1.6.5
✅ 版本号已更新：1.6.5
✅ Git tag 已创建：v1.6.5
```

### 方法 2：指定版本号

```bash
python update_version.py 1.7.0
```

### 版本号规则

遵循语义化版本 (Semantic Versioning)：`主版本。次版本.patch 版本`

- **主版本**：不兼容的 API 修改
- **次版本**：向后兼容的功能新增
- **patch 版本**：向后兼容的问题修复

### 自动化流程

1. **修改代码** → 完成功能或修复
2. **运行更新脚本** → `python update_version.py`
3. **提交代码** → `git add . && git commit -m "..."`
4. **推送** → `git push origin main --tags`

### 窗口标题显示

启动应用后，窗口标题自动显示当前版本：
```
ClawClock v1.6.5 - 图形时钟
```

版本号来源（优先级从高到低）：
1. **Git tag**：如果有 tag，使用 `git describe` 获取
2. **硬编码版本**：`__version__` 常量作为 fallback

### 示例工作流

```bash
# 1. 完成修复
git add clock.py
git commit -m "🐛 修复主题切换问题"

# 2. 更新版本号（自动递增 patch）
python update_version.py

# 3. 提交版本更新
git add clock.py
git commit -m "📦 发布 v1.6.5"

# 4. 推送代码和 tag
git push origin main --tags
```

### 注意事项

- 每次发布前必须更新版本号
- 版本号与 git tag 保持一致
- 重大功能更新时手动指定次版本或主版本
