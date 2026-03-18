# ClawClock 优化执行计划

## 执行日期
2026-03-19

## 优化任务清单

### 🔥 P0 - 修复测试失败（4个）

- [ ] 修复 test_default_config 配置默认值
- [ ] 修复 test_apply_brightness_to_color 亮度计算
- [ ] 修复 test_get_current_color 默认颜色
- [ ] 修复 test_from_dict 字典加载

### 🔥 P0 - 重构大型函数

- [ ] 拆分 clock.py setup_ui() 205行 → 多个子函数
- [ ] 拆分 clock.py __init__() 115行 → 多个初始化方法
- [ ] 拆分 timer.py _create_segments() 91行
- [ ] 拆分 timer.py _show_custom_time_dialog() 77行

### 🟠 P1 - 模块化重组

- [ ] 创建 config/constants.py 常量类
- [ ] 创建 config/settings.py 配置管理
- [ ] 创建 config/persistence.py 持久化
- [ ] 提取 effects/breath_light.py 呼吸灯效果
- [ ] 提取 effects/animations.py 动画系统

### 🟡 P2 - 代码质量改进

- [ ] 统一错误处理（自定义异常）
- [ ] 添加类型提示完整性
- [ ] 添加日志系统（logging）

---

## 预期收益

| 优化项 | 收益 |
|--------|------|
| 测试覆盖率提升 | 97.3% → 100% |
| 代码可维护性 | 提升 50% |
| 模块复用性 | 提升 40% |
| 代码行数（单文件） | max 205行 → <100行 |
