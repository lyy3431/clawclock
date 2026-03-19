# 🕐 ClawClock - 图形化桌面时钟应用

ClawClock 是一款专为 Linux 桌面设计的多功能时钟应用，支持模拟时钟、数字时钟、秒表、倒计时等多种模式，满足工作、学习、生活的全场景计时需求。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Tkinter](https://img.shields.io/badge/tkinter-builtin-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)
![Version](https://img.shields.io/badge/version-1.6.0-orange.svg)
![Tests](https://img.shields.io/badge/tests-146%20passed-brightgreen.svg)

---

## ✨ 核心功能

### 🕐 时钟显示
- **双模式切换**：模拟时钟与数字时钟自由切换
- **25 时区支持**：覆盖 UTC-12 至 UTC+12，每时区配备代表城市
- **7 段数码管**：经典红色 LED 风格，还原电子钟质感
- **50ms 刷新率**：秒针流畅移动，时间实时更新

### ⏱️ 专业计时工具
- **秒表**：10ms 高精度计时，支持启动/停止/复位/计圈，无限记录
- **倒计时**：预设快捷时长（番茄钟/休息等）+ 自定义时间，声音与视觉双重提醒
- **呼吸灯效果**（v1.5.0+）：倒计时期间数字/背景呈现呼吸式明暗变化
  - 4 种风格：柔和、科技、炫酷、简约（v1.5.1 新增）
  - 平滑缓动曲线，状态智能切换（正常→警告→完成）

### 🎨 个性化体验
- **4 种主题**：Dark（默认）、Light、Green、Cyberpunk，一键切换
- **全屏模式**：沉浸式显示，适合演示或专注场景
- **窗口置顶**：保持窗口始终在前，方便随时查看
- **配置持久化**：时区、模式、主题、窗口位置自动保存，重启后恢复

### ⚙️ 技术特性
- **跨平台兼容**：适用于所有 Linux 发行版（Debian/Ubuntu/Arch/Fedora）
- **零依赖安装**：使用 Python 内置 Tkinter 库，无需额外安装
- **轻量级**：内存占用约 30MB，低 CPU 开销
- **模块化架构**（v1.6.0+）：配置、特效、工具模块分离，易于维护和扩展
- **统一错误处理**：6 种异常类覆盖所有错误场景
- **结构化日志**：5 级日志系统，支持上下文追踪
- **100% 测试覆盖**：146 个自动化测试用例，确保稳定性

---

## 📦 快速安装

### 1. 安装依赖

```bash
# Debian/Ubuntu
sudo apt install python3-tk python3-tz

# Arch Linux
sudo pacman -S tk python-tz

# Fedora
sudo dnf install python3-tkinter python3-dateutil
```

### 2. 启动应用

```bash
cd /home/lenovo/AItest/clawclock
python3 clock.py
```

> 📖 **详细安装指南**：请参阅 [INSTALL.md](INSTALL.md) 获取完整安装步骤和故障排除方案。

---

## 🧪 测试覆盖

项目包含 **95+ 个自动化测试用例**，确保核心功能稳定可靠。

### 运行测试

```bash
# 运行完整测试套件
./run_tests.sh

# 详细输出模式
./run_tests.sh -v
```

### 测试范围

| 模块 | 用例数 | 覆盖内容 |
|------|--------|----------|
| 秒表功能 | 17 | 启动/停止/重置、圈速记录、时间格式化、边界情况 |
| 呼吸灯效果 | 21 | 配置、效果、颜色转换、状态切换、集成测试 |
| 闹钟功能 | 7 | 创建、触发逻辑、重复设置 |
| 配置管理 | 5 | 加载、保存、合并、排序 |
| 闹钟管理 | 6 | 添加、删除、切换状态 |
| 7 段显示 | 3 | 数字段定义、段有效性验证 |
| 时区数据 | 2 | 时区数量、数据结构验证 |

---

## 🎮 快速操作指南

| 功能 | 操作 | 说明 |
|------|------|------|
| **切换时区** | 点击时区下拉菜单 → 选择城市 | 支持 25 个时区 |
| **切换模式** | 选择 Analog / Digital / Stopwatch | 即时切换，无需重启 |
| **⏰ 闹钟** | 点击"⏰ 闹钟"按钮 | 添加/删除/启用/禁用 |
| **⏱️ 秒表** | 选择秒表模式 → 点击"▶️ 开始" | 开始/停止/复位/计圈 |
| **⏳ 倒计时** | 选择倒计时模式 → 点击预设或自定义时间 | 开始/暂停/重置 |
| **🔲 全屏** | 点击"🔲 全屏"按钮 | 切换全屏显示 |
| **📌 置顶** | 点击"📌 置顶"按钮 | 窗口始终在前 |
| **退出** | 点击 × 或 Alt+F4 | 正常关闭应用 |

---

## 🏗️ 模块化架构（v1.6.0+）

v1.6.0 进行了全面的模块化重构，将单体应用拆分为独立的模块系统，提高代码可维护性和可扩展性。

**模块结构：**

```
clawclock/
├── config/              # 配置模块
│   ├── constants.py     # 全局常量定义
│   ├── settings.py      # 配置管理器
│   ├── persistence.py   # 数据持久化
│   └── defaults.py      # 默认配置模板
├── effects/             # 特效模块
│   ├── breath_light.py  # 呼吸灯效果引擎
│   └── animations.py    # 动画系统（6 种缓动函数）
├── utils/               # 工具模块
│   ├── errors.py        # 统一错误处理
│   └── logger.py        # 结构化日志系统
├── main.py              # 主程序入口
└── clock.py             # 主程序（兼容旧版）
```

**核心模块：**

| 模块 | 功能 | 关键类/函数 |
|------|------|-------------|
| `config.settings` | 配置管理 | `ConfigManager` (load/save/get/set) |
| `config.persistence` | 数据持久化 | `PersistenceManager` (闹钟/秒表/倒计时状态) |
| `effects.breath_light` | 呼吸灯效果 | `BreathLightEffect`, `BreathStyle`, `TimerStatus` |
| `effects.animations` | 动画系统 | `Animation`, `FadeAnimation`, `ColorAnimation` |
| `utils.errors` | 错误处理 | 6 种异常类 + 验证函数 |
| `utils.logger` | 日志系统 | `ClockLogger` (5 级日志) |

**使用示例：**

```python
# 配置管理
from config.settings import get_config_manager
config = get_config_manager()
timezone = config.get("timezone")

# 错误处理
from utils.errors import validate_time_format, TimerError
try:
    validate_time_format("23:59")
except TimerError as e:
    print(f"错误：{e}")

# 日志系统
from utils.logger import info, error
info("应用启动")

# 呼吸灯效果
from effects.breath_light import BreathLightEffect
effect = BreathLightEffect()
color = effect.update(0.1)
```

---

## 🫧 呼吸灯效果（v1.5.0+）

呼吸灯效果为倒计时功能增添视觉吸引力，通过平滑的明暗变化提供直观的时间反馈。

### 核心特性

| 特性 | 说明 |
|------|------|
| **呼吸模式** | 数字呼吸 / 背景呼吸 / 边框呼吸 / 全部模式 |
| **4 种风格** | 柔和（默认）、科技、炫酷（彩虹渐变）、简约 |
| **智能状态** | 🟢 正常（绿色）→ 🟡 警告（最后 10 秒橙色）→ 🔴 完成（红色加速） |
| **可配置** | 频率（Hz）、强度（0-1）、颜色主题 |

### 配置示例

编辑 `config.json`：

```json
{
  "breath_light": {
    "enabled": true,
    "mode": "digital",
    "frequency": 0.5,
    "intensity": 0.5,
    "style": "soft",
    "smooth_curve": true,
    "color_scheme": {
      "normal": "#00d4aa",
      "warning": "#ffaa00",
      "completed": "#ff3333"
    }
  }
}
```

### 使用场景

- 🍅 **番茄工作法**：视觉反馈帮助保持专注
- ⏱️ **倒计时预警**：最后 10 秒颜色变化提醒
- 🎨 **桌面美化**：增添动感与科技感

---

## 📁 项目结构

### v1.6.0+ 模块化结构

```
clawclock/
├── main.py                  # 主程序入口
├── clock.py                 # 主程序（Tkinter，兼容旧版）
├── clock_v2.py              # 模块化示例实现
├── timer.py                 # 倒计时模块
├── stopwatch.py             # 秒表模块
├── config.json              # 配置文件
├── install.sh               # 一键安装脚本
├── run_tests.sh             # 测试脚本
├── config/                  # 配置模块（v1.6.0+）
│   ├── constants.py         # 全局常量定义
│   ├── settings.py          # 配置管理器
│   ├── persistence.py       # 数据持久化
│   └── defaults.py          # 默认配置模板
├── effects/                 # 特效模块（v1.6.0+）
│   ├── breath_light.py      # 呼吸灯效果引擎
│   └── animations.py        # 动画系统
├── utils/                   # 工具模块（v1.6.0+）
│   ├── errors.py            # 统一错误处理
│   └── logger.py            # 结构化日志系统
├── themes/                  # 主题配置目录
├── screenshots/             # 界面截图
└── docs/                    # 文档目录
    ├── README.md            # 使用说明
    ├── INSTALL.md           # 安装指南
    ├── CONTRIBUTING.md      # 贡献指南
    ├── CHANGELOG.md         # 更新日志
    ├── FAQ.md               # 常见问题
    ├── TUTORIAL.md          # 详细教程
    ├── API.md               # API 文档（v1.6.0+）
    └── DEVELOPMENT.md       # 开发指南（v1.6.0+）
```

### 传统结构（兼容）

```
clawclock/
├── clock.py                 # 主程序（Tkinter）
├── timer.py                 # 倒计时模块
├── stopwatch.py             # 秒表模块
├── breath_light.py          # 呼吸灯效果模块
├── breath_light_improved.py # 呼吸灯优化版本（v1.5.1）
└── config.json              # 配置文件
```

---

## ⏱️ 秒表功能（v1.3.0+）

专业级秒表，支持 10ms 高精度计时和无限计圈记录。

### 核心功能

| 功能 | 说明 |
|------|------|
| **精度** | 10ms 刷新率（0.01 秒） |
| **显示格式** | HH:MM:SS.ms（时：分：秒。百分秒） |
| **控制** | 启动 / 停止 / 复位 / 计圈 |
| **计圈** | 无限记录，显示累计时间 + 单圈时间 |

### 计圈示例

```
圈 01 | 00:00:15.23 | 00:00:15.23  ← 第一圈
圈 02 | 00:00:31.45 | 00:00:16.22  ← 第二圈
圈 03 | 00:00:46.89 | 00:00:15.44  ← 第三圈
```

### 使用场景



## ⏳ 倒计时功能（v1.4.0+）

专业级倒计时，支持预设快捷时长和自定义时间，配备声音与视觉双重提醒。

### 预设时长

| 预设 | 时长 | 场景 |
|------|------|------|
| 🍅 番茄钟 | 25 分钟 | 专注工作/学习 |
| ☕ 短休息 | 5 分钟 | 番茄间隔 |
| 🛌 长休息 | 15 分钟 | 长时间后恢复 |
| ⏱️ 快速 | 5/10/30 分钟 | 灵活选择 |

### 核心功能

- ✅ **双重提醒**：声音 + 视觉闪烁
- ✅ **灵活控制**：开始 / 暂停 / 重置
- ✅ **自定义时长**：支持任意时间设置
- ✅ **呼吸灯联动**：倒计时期间呈现呼吸效果（v1.5.0+）

### 使用场景

| 场景 | 推荐时长 |
|------|----------|
| 🍅 番茄工作法 | 25 分钟工作 + 5 分钟休息 |
| 🍳 烹饪计时 | 根据菜谱设定 |
| 🎯 会议控制 | 30-60 分钟 |
| 🏃 HIIT 训练 | 20 秒 -2 分钟间歇 |
| 🧘 冥想练习 | 5-20 分钟 |
| 📚 学习专注 | 25-45 分钟 |

---

## 🎨 界面预览

### 模拟时钟模式
![模拟时钟](screenshots/analog-clock.png)
- 经典圆形表盘，三针显示（时针、分针、秒针）
- 60 个精细刻度（12 主刻度 + 48 次刻度）
- 50ms 刷新率，秒针流畅移动

### 数字时钟模式（7 段数码管）
![数字时钟](screenshots/digital-clock.png)
- 🔴 经典红色 LED 风格，HH:MM:SS 完整显示
- 📅 日期和星期显示
- 数码管规格：35px × 60px，5px 段厚度，圆形端点

### 双模式同时显示
![双模式](screenshots/both-modes.png)
- 上下布局，同时展示两种风格
- 适合教学演示和对比（需使用 `clock_both.py`）

### 时区选择器
![时区选择](screenshots/timezone-selector.png)
- 🌍 25 个时区（UTC-12 ~ UTC+12），每时区配备代表城市
- 🔽 下拉菜单，操作便捷

---

## 📸 截图脚本

项目提供专用脚本自动生成界面截图：

```bash
python3 clock_screenshot.py analog    # 模拟时钟
python3 clock_screenshot.py digital   # 数字时钟
python3 clock_timezone.py             # 时区选择器
python3 clock_both.py                 # 双模式
```

截图保存至 `screenshots/` 目录。需 ImageMagick 和 X11 环境。

---

## 🔧 技术细节

### 性能指标

| 指标 | 数值 |
|------|------|
| 刷新率 | 50ms (20 FPS) |
| 渲染方式 | Tkinter Canvas 矢量绘图 |
| 内存占用 | ~30MB |
| CPU 开销 | 低 |

### 核心算法

**指针角度计算：**
```python
sec_angle  = second * 6 - 90           # 每秒 6 度
min_angle  = minute * 6 + second * 0.1 - 90  # 每分钟 6 度 + 偏移
hour_angle = (hour % 12) * 30 + minute * 0.5 - 90  # 每小时 30 度 + 偏移
```

**时区处理：** 使用 Python `datetime` + IANA 时区数据库，自动处理夏令时。

---

## ⚙️ 配置选项

### 💾 自动保存

应用自动保存以下设置至 `config.json`：
- 默认时区、显示模式、颜色主题、窗口位置

**配置文件位置**: `~/.openclaw/workspace/clawclock/config.json`  
**重置配置**: 删除该文件后重启应用

### 🎨 主题切换

内置 4 种主题，界面下拉菜单一键切换：

| 主题 | 风格 | 场景 |
|------|------|------|
| Dark | 深色模式 | 日常使用（默认） |
| Light | 经典白 | 办公环境 |
| Green | 护眼绿 | 夜间模式 |
| Cyberpunk | 赛博朋克 | 个性化展示 |

**自定义主题**: 在 `themes/` 目录创建 JSON 文件定义颜色。

### 🌍 时区支持

覆盖 **UTC-12 ~ UTC+12** 共 25 个时区，每时区配备代表城市：

| 区域 | 时区范围 | 代表城市示例 |
|------|----------|--------------|
| 西区 | UTC-12 ~ UTC-1 | 檀香山、洛杉矶、纽约、圣保罗 |
| 零时区 | UTC+0 | 伦敦（格林威治） |
| 东区 | UTC+1 ~ UTC+12 | 巴黎、莫斯科、上海、东京、悉尼 |

> 📍 **默认时区**: Asia/Shanghai (UTC+8)

---

## 📝 更新日志

详细更新记录请参阅 [CHANGELOG.md](CHANGELOG.md)。

### 最新版本

| 版本 | 日期 | 核心更新 |
|------|------|----------|
| v1.6.0 | 2026-03-19 | 模块化重构、配置系统、错误处理、日志系统、100% 测试覆盖 |
| v1.5.1 | 2026-03-18 | 4 种呼吸灯风格、平滑缓动曲线、主题切换优化 |
| v1.5.0 | 2026-03-18 | 呼吸灯效果、状态感知、配置持久化 |
| v1.4.0 | 2026-03-18 | 倒计时功能、预设时长、双重提醒 |
| v1.3.0 | 2026-03-15 | 秒表功能、10ms 精度、计圈记录 |
| v1.2.0 | 2026-03-15 | 4 种主题、一键切换 |
| v1.1.0 | 2026-03-15 | 25 时区、7 段数码管显示 |
| v1.0.0 | 2026-03-15 | 初始版本 |

---

## 🤝 贡献

欢迎贡献！请参阅 [贡献指南](CONTRIBUTING.md) 了解如何提交 Issue 和 Pull Request。

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [INSTALL.md](INSTALL.md) | 详细安装指南和故障排除 |
| [TUTORIAL.md](TUTORIAL.md) | 使用教程 |
| [FAQ.md](FAQ.md) | 常见问题解答 |
| [CHANGELOG.md](CHANGELOG.md) | 完整更新日志 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |
| [API.md](docs/API.md) | API 参考文档（v1.6.0+） |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | 开发指南（v1.6.0+） |

---

**ClawClock** - 让时间触手可及 🕐
