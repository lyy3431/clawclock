# 📘 ClawClock 使用教程

欢迎使用 ClawClock！本教程将帮助你快速上手并充分利用所有功能。

---

## 🚀 快速开始指南（5 分钟上手）

### 步骤 1：安装依赖

```bash
# Debian/Ubuntu 系统
sudo apt install python3-tk python3-tz imagemagick
```

### 步骤 2：克隆或进入项目目录

```bash
cd /home/lenovo/AItest/clawclock
```

### 步骤 3：运行时钟

```bash
python3 clock.py
```

### 步骤 4：基本操作

- **切换时区**：点击顶部的时区下拉菜单，选择你需要的城市
- **切换模式**：选择 `Analog`（模拟）或 `Digital`（数字）单选按钮
- **关闭窗口**：点击窗口右上角的 × 按钮

**完成！** 🎉 你现在已经可以使用 ClawClock 了！

---

## 📖 详细功能说明

### 1. 时区切换功能

ClawClock 支持全球 25 个时区，覆盖东西各 12 时区 + 零时区。

#### 操作步骤：

1. 点击窗口顶部的时区下拉菜单
2. 浏览列表找到你需要的时区
3. 点击选择，时钟会立即更新为该时区时间

#### 时区列表：

| 时区偏移 | 代表城市 | 地区 |
|----------|----------|------|
| UTC-12 | Pacific/Kwajalein | 国际日期变更线西 |
| UTC-11 | Pacific/Pago_Pago | 帕果帕果 |
| UTC-10 | Pacific/Honolulu | 檀香山 |
| UTC-9 | America/Anchorage | 安克雷奇 |
| UTC-8 | America/Los_Angeles | 洛杉矶 |
| UTC-7 | America/Denver | 丹佛 |
| UTC-6 | America/Chicago | 芝加哥 |
| UTC-5 | America/New_York | 纽约 |
| UTC-4 | America/Halifax | 哈利法克斯 |
| UTC-3 | America/Sao_Paulo | 圣保罗 |
| UTC-2 | Atlantic/South_Georgia | 南乔治亚 |
| UTC-1 | Atlantic/Azores | 亚速尔群岛 |
| **UTC+0** | **UTC** | **协调世界时** |
| UTC+1 | Europe/London | 伦敦 |
| UTC+2 | Europe/Paris | 巴黎 |
| UTC+3 | Europe/Moscow | 莫斯科 |
| UTC+4 | Asia/Dubai | 迪拜 |
| UTC+5 | Asia/Karachi | 卡拉奇 |
| UTC+6 | Asia/Dhaka | 达卡 |
| UTC+7 | Asia/Bangkok | 曼谷 |
| **UTC+8** | **Asia/Shanghai** | **上海（默认）** |
| UTC+9 | Asia/Tokyo | 东京 |
| UTC+10 | Australia/Sydney | 悉尼 |
| UTC+11 | Pacific/Noumea | 努美阿 |
| UTC+12 | Pacific/Auckland | 奥克兰 |

#### 使用场景：

- 🌍 **跨国团队协作**：同时查看多个时区时间
- ✈️ **旅行规划**：提前适应目的地时区
- 📞 **国际通话**：确认对方时区的合适通话时间

---

### 2. 模式切换功能

ClawClock 提供两种显示模式，可根据喜好自由切换。

#### 模拟时钟模式 (Analog)

**特点：**
- 经典圆形表盘设计
- 三针显示（时针、分针、秒针）
- 60 个精细刻度（12 主刻度 + 48 次刻度）
- 适合传统时钟爱好者

**切换方法：**
1. 选择 `Analog` 单选按钮
2. 时钟立即切换为模拟表盘样式

#### 数字时钟模式 (Digital)

**特点：**
- 🔴 经典红色 LED 风格
- 🕐 HH:MM:SS 完整时间显示
- 📅 日期和星期显示
- ⚡ 50ms 实时更新

**数码管规格：**
- 单个数字尺寸：35px × 60px
- 段厚度：5px 圆形端点
- 点亮颜色：#ff3333（亮红色）
- 未点亮颜色：#331111（暗红色）

**切换方法：**
1. 选择 `Digital` 单选按钮
2. 时钟立即切换为 7 段数码管样式

#### 双模式同时显示

如需同时查看两种模式：

```bash
python3 clock_both.py
```

这会打开一个新窗口，上下同时显示模拟和数字两种模式，适合：
- 教学演示
- 对比展示
- 个人偏好不确定时的试用

---

### 3. 配置自定义

ClawClock 支持个性化配置，满足你的定制需求。

#### 颜色主题配置

编辑 `clock.py` 文件中的颜色变量：

```python
# 在文件开头部分找到以下变量
bg_color = "#1a1a2e"      # 背景色（深蓝黑色）
face_color = "#16213e"    # 表盘色（深蓝色）
hand_color = "#e94560"    # 指针色（粉红色）
text_color = "#ffffff"    # 文字色（白色）
accent_color = "#0f3460"  # 强调色（深蓝色）
```

**推荐配色方案：**

| 风格 | 背景色 | 指针色 | 文字色 |
|------|--------|--------|--------|
| 经典深色 | #1a1a2e | #e94560 | #ffffff |
| 简约白色 | #f5f5f5 | #333333 | #000000 |
| 夜间模式 | #000000 | #00ff00 | #00ff00 |
| 海洋蓝 | #001f3f | #0074D9 | #ffffff |

#### 窗口大小配置

默认窗口大小为 600×500 像素，可在代码中修改：

```python
# 找到窗口创建部分
window.geometry("600x500")  # 宽×高
```

#### 刷新率配置

默认刷新率为 50ms（20 FPS），如需调整：

```python
# 找到 update_clock 函数的调用
root.after(50, update_clock)  # 50 毫秒
```

**建议：**
- 50ms：流畅且资源占用低（推荐）
- 30ms：更流畅但占用稍高
- 100ms：省电模式

---

## ❓ 常见问题解答

### Q1: 时钟无法启动，提示找不到 tkinter 模块

**解决方案：**
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Arch Linux
sudo pacman -S tk

# Fedora
sudo dnf install python3-tkinter
```

### Q2: 时区时间不准确

**可能原因：**
1. 系统时间本身不准确
2. 时区数据库过时

**解决方案：**
```bash
# 更新系统时间
sudo timedatectl set-ntp true

# 更新 tzdata 包
sudo apt update && sudo apt install --reinstall tzdata
```

### Q3: 数字时钟显示模糊

**解决方案：**
- 确保在原生分辨率下运行
- 检查显示器缩放设置（建议 100%）
- 如使用 HiDPI 屏幕，可能需要调整窗口大小

### Q4: 如何设置开机自启动？

**方法 1：添加到启动应用（推荐）**

```bash
# 创建桌面启动文件
cat > ~/.config/autostart/clawclock.desktop << EOF
[Desktop Entry]
Type=Application
Name=ClawClock
Exec=python3 /home/lenovo/AItest/clawclock/clock.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

**方法 2：添加到 ~/.bashrc**

```bash
# 在 ~/.bashrc 末尾添加
python3 /home/lenovo/AItest/clawclock/clock.py &
```

### Q5: 能否同时显示多个时区？

当前版本一次只显示一个时区，但你可以：

1. 运行多个实例（每个实例设置不同时区）
2. 使用 `clock_both.py` 同时查看模拟和数字模式

**运行多实例：**
```bash
# 终端 1：本地时间
python3 clock.py

# 终端 2：纽约时间（需手动修改代码中的默认时区）
python3 clock.py
```

### Q6: 截图脚本无法运行

**依赖检查：**
```bash
# 确保安装了 ImageMagick
sudo apt install imagemagick

# 确保有 X11 显示环境
echo $DISPLAY  # 应显示 :0 或类似
```

---

## 💡 技巧与提示

### 技巧 1：快速切换常用时区

如果你经常在两个时区之间切换：

1. 记住两个时区在列表中的位置
2. 使用键盘方向键快速选择
3. 或者修改代码中的默认时区

### 技巧 2：制作桌面时钟

将 ClawClock 设置为始终在顶部：

```bash
# 使用 wmctrl 工具
sudo apt install wmctrl

# 运行时钟后，在另一个终端执行
wmctrl -r "ClawClock" -b toggle,above
```

### 技巧 3：截图分享

使用内置截图脚本快速生成精美截图：

```bash
# 生成所有截图
python3 clock_screenshot.py analog
python3 clock_screenshot.py digital

# 截图自动保存到 screenshots/ 目录
```

### 技巧 4：性能优化

如在低配置设备上运行：

1. 降低刷新率（修改为 100ms）
2. 关闭不必要的后台应用
3. 使用 C 版本（`clock.c`）代替 Python 版本

### 技巧 5：自定义时区列表

如需添加或修改时区：

```python
# 编辑 clock.py 中的 TIMEZONES 列表
TIMEZONES = [
    ("UTC+8 - 上海", "Asia/Shanghai"),
    ("UTC+9 - 东京", "Asia/Tokyo"),
    # 添加你的自定义时区
    ("UTC+8 - 北京", "Asia/Beijing"),
]
```

### 技巧 6：演示模式

进行演示时，使用双模式显示效果更佳：

```bash
python3 clock_both.py
```

配合全屏模式（F11 或窗口管理器快捷键）可获得最佳展示效果。

### 技巧 7：代码学习

ClawClock 是学习 Python GUI 编程的优秀示例：

- 学习 Tkinter 基础：查看 `clock.py`
- 学习 7 段数码管实现：查看 `draw_digit_segment()` 函数
- 学习时区处理：查看 `get_timezone_time()` 函数

---

## 🏗️ v1.6.0 模块化架构指南

v1.6.0 引入了全新的模块化架构，将应用拆分为独立的模块系统。本章节介绍如何使用这些新模块。

### 1. 配置管理模块

**使用场景**：读取或修改应用配置

```python
from config.settings import get_config_manager

# 获取配置管理器实例
config = get_config_manager()

# 读取配置
timezone = config.get("timezone")
theme = config.get("theme")
breath_enabled = config.get("breath_light.enabled")

# 修改配置
config.set("theme", "light")
config.set("breath_light.frequency", 0.8)

# 保存配置
config.save()
```

**配置文件位置**：`~/.openclaw/workspace/clawclock/config.json`

### 2. 数据持久化模块

**使用场景**：保存和加载闹钟、秒表、倒计时状态

```python
from config.persistence import get_persistence_manager

# 获取持久化管理器
persistence = get_persistence_manager()

# 闹钟管理
alarms = persistence.load_alarms()
persistence.save_alarms(alarms)
persistence.add_alarm(alarm)
persistence.remove_alarm(alarm_id)
persistence.toggle_alarm(alarm_id)

# 秒表状态
state = persistence.load_stopwatch_state()
persistence.save_stopwatch_state(state)

# 倒计时状态
timer_state = persistence.load_timer_state()
persistence.save_timer_state(timer_state)
```

### 3. 呼吸灯效果模块

**使用场景**：自定义呼吸灯效果或集成到其他功能

```python
from effects.breath_light import (
    BreathLightEffect,
    BreathStyle,
    BreathMode,
    TimerStatus,
    hex_to_rgb,
    rgb_to_hex,
    interpolate_color
)

# 创建呼吸灯效果实例
effect = BreathLightEffect()

# 设置风格
effect.set_style(BreathStyle.SOFT)  # 柔和模式
effect.set_style(BreathStyle.TECH)  # 科技模式
effect.set_style(BreathStyle.COOL)  # 炫酷模式
effect.set_style(BreathStyle.MINIMAL)  # 简约模式

# 设置状态
effect.set_status(TimerStatus.NORMAL)     # 正常（绿色）
effect.set_status(TimerStatus.WARNING)    # 警告（橙色）
effect.set_status(TimerStatus.COMPLETED)  # 完成（红色）

# 更新效果（返回当前颜色）
current_color = effect.update(elapsed_time=0.5)

# 颜色工具
rgb = hex_to_rgb("#00ff88")  # (0, 255, 136)
hex_color = rgb_to_hex(0, 255, 136)  # "#00ff88"
mixed = interpolate_color("#00ff88", "#ff0000", 0.5)  # 中间色
```

### 4. 动画系统模块

**使用场景**：创建自定义动画效果

```python
from effects.animations import (
    Animation,
    FadeAnimation,
    ColorAnimation,
    ease_in_out,
    bounce,
    elastic
)

# 创建基础动画
anim = Animation(
    duration=1.0,  # 1 秒
    easing=ease_in_out
)

# 淡入淡出动画
fade = FadeAnimation(
    start_alpha=0.0,
    end_alpha=1.0,
    duration=0.5
)
alpha = fade.update(0.25)  # 更新到 50%

# 颜色渐变动画
color_anim = ColorAnimation(
    start_color="#00ff88",
    end_color="#ff0000",
    duration=1.0
)
current_color = color_anim.update(0.5)  # 更新到 50%
```

### 5. 错误处理模块

**使用场景**：统一错误处理和验证

```python
from utils.errors import (
    ClockError,
    ConfigError,
    ThemeError,
    AlarmError,
    TimerError,
    IOError,
    validate_time_format,
    validate_preset_time,
    safe_execute,
    ErrorLogger
)

# 时间格式验证
try:
    validate_time_format("23:59")  # ✅ 有效
    validate_time_format("25:00")  # ❌ 抛出 TimerError
except TimerError as e:
    print(f"时间格式错误：{e}")

# 预设时间验证
try:
    validate_preset_time(hours=1, minutes=30, seconds=0)
except TimerError as e:
    print(f"预设时间错误：{e}")

# 安全执行包装器
result = safe_execute(
    func=lambda: 10 / 0,
    default=0,
    error_handler=lambda e: print(f"错误：{e}")
)

# 错误日志记录器
logger = ErrorLogger()
logger.log_error("测试错误", {"key": "value"})
```

### 6. 日志系统模块

**使用场景**：记录应用日志，便于调试和追踪

```python
from utils.logger import (
    ClockLogger,
    debug,
    info,
    warning,
    error,
    critical,
    set_context
)

# 直接使用全局函数
info("应用启动")
debug("调试信息")
warning("警告信息")
error("错误信息")
critical("严重错误")

# 设置上下文
set_context(module="clock", func="init", line=42)
info("带上下文的日志")

# 创建自定义日志记录器
logger = ClockLogger(name="my_module")
logger.info("自定义日志记录器")
```

### 7. 使用 main.py 启动应用

v1.6.0 引入了独立的入口文件：

```bash
# 传统方式（仍然支持）
python3 clock.py

# 新方式（推荐）
python3 main.py
```

### 8. 参考 clock_v2.py 示例

`clock_v2.py` 是模块化架构的完整示例实现，展示了如何：

- 使用配置管理器
- 集成呼吸灯效果
- 处理错误和日志
- 组织代码结构

**学习路径：**
1. 阅读 `clock_v2.py` 源码
2. 理解模块间的依赖关系
3. 尝试修改配置和效果
4. 创建自己的模块扩展

---

## 📚 进阶资源

- **GitHub 仓库**：查看最新代码和更新
- **DEVELOPMENT.md**：开发者文档
- **README.md**：项目总览
- **源码注释**：代码中包含详细注释

---

## 🆘 需要帮助？

如遇到本教程未涵盖的问题：

1. 查看 `README.md` 中的故障排除章节
2. 查阅 `DEVELOPMENT.md` 开发文档
3. 提交 Issue 到 GitHub 仓库
4. 查看项目更新日志了解最新功能

---

*教程版本：v1.6.0*
*最后更新：2026-03-19*
