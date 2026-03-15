# 🕐 ClawClock - 图形化时钟应用

一个支持模拟和数字时间显示的 Linux 桌面时钟应用，提供 Python 和 C 两个版本。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![GTK](https://img.shields.io/badge/GTK-3.0+-green.svg)

---

## ✨ 功能特性

- 🕐 **双模式显示**：模拟时钟 + 数字时钟，可自由切换
- 🌍 **25 时区支持**：东西各 12 时区 + 零时区，每区指定代表城市
- 🔢 **7 段数码管显示**：经典电子钟风格，红色 LED 效果
- 🎨 **现代 UI**：深色主题，美观大方
- ⚡ **实时更新**：50ms 刷新率，流畅显示秒针
- 🖥️ **跨平台**：Python 版本支持所有 Linux 发行版

---

## 📦 安装依赖

### Python 版本

```bash
# Debian/Ubuntu
sudo apt install python3-tk python3-tz

# Arch Linux
sudo pacman -S tk python-tz

# Fedora
sudo dnf install python3-tkinter python3-dateutil
```

### C 版本 (GTK3)

```bash
# Debian/Ubuntu
sudo apt install libgtk-3-dev libcairo2-dev gcc

# Arch Linux
sudo pacman -S gtk3 cairo gcc

# Fedora
sudo dnf install gtk3-devel cairo-devel gcc
```

---

## 🚀 使用方法

### Python 版本

```bash
cd /home/lenovo/AItest/clawclock
python3 clock.py
```

### C 版本

```bash
# 编译
cd /home/lenovo/AItest/clawclock
gcc -o clock clock.c `pkg-config --cflags --libs gtk+-3.0` -lm

# 运行
./clock
```

---

## 🎮 操作说明

| 功能 | 操作方式 |
|------|----------|
| 切换时区 | 下拉菜单选择城市 |
| 切换模式 | Analog（模拟）/ Digital（数字）/ Both（两者） |
| 关闭窗口 | 点击窗口关闭按钮 |

---

## 📁 项目结构

```
clawclock/
├── clock.py          # Python 版本 (Tkinter)
├── clock.c           # C 版本 (GTK3)
├── README.md         # 说明文档
└── screenshots/      # 截图目录（可选）
```

---

## 🎨 界面预览

### 模拟时钟模式
- 经典圆形表盘
- 时针、分针、秒针
- 小时刻度和分钟刻度

### 数字时钟模式（7 段数码管）
- 🔴 **经典 LED 风格**：红色 7 段数码管显示
- 🕐 **HH:MM:SS 格式**：时、分、秒完整显示
- 📅 **日期和时区**：下方显示日期和当前时区
- ⚡ **流畅刷新**：50ms 更新率，秒秒精准

### 双模式同时显示
- 左侧模拟时钟
- 右侧 7 段数码管时钟
- 最佳视觉体验

---

## ⚙️ 配置选项

### 颜色主题

可在代码中修改以下颜色：

```python
bg_color = "#1a1a2e"      # 背景色
face_color = "#16213e"    # 表盘色
hand_color = "#e94560"    # 指针色
text_color = "#ffffff"    # 文字色
accent_color = "#0f3460"  # 强调色
```

### 时区列表

支持**东西各 12 时区**，共 25 个时区选项：

| 时区 | 代表城市 | 说明 |
|------|----------|------|
| **西区 (UTC-12 ~ UTC-1)** | | |
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
| **零时区** | | |
| UTC+0 | UTC | 协调世界时 |
| **东区 (UTC+1 ~ UTC+12)** | | |
| UTC+1 | Europe/London | 伦敦 |
| UTC+2 | Europe/Paris | 巴黎 |
| UTC+3 | Europe/Moscow | 莫斯科 |
| UTC+4 | Asia/Dubai | 迪拜 |
| UTC+5 | Asia/Karachi | 卡拉奇 |
| UTC+6 | Asia/Dhaka | 达卡 |
| UTC+7 | Asia/Bangkok | 曼谷 |
| UTC+8 | Asia/Shanghai | 上海（默认） |
| UTC+9 | Asia/Tokyo | 东京 |
| UTC+10 | Australia/Sydney | 悉尼 |
| UTC+11 | Pacific/Noumea | 努美阿 |
| UTC+12 | Pacific/Auckland | 奥克兰 |

---

## 🛠️ 开发说明

### Python 版本特点

- 使用 Tkinter 库，无需额外安装（Python 自带）
- 代码简洁，易于修改和扩展
- 适合快速原型开发

### C 版本特点

- 使用 GTK3，原生 Linux 应用
- 性能更优，资源占用更低
- 适合系统集成

---

## 📝 更新日志

### v1.1.0 (2026-03-15) - agent-2 & agent-3 协作更新
- ✅ **25 时区支持**：东西各 12 时区 + 零时区
- ✅ **7 段数码管显示**：经典 LED 风格数字显示
- ✅ **时区城市映射**：每时区指定代表城市
- ✅ **文档完善**：详细说明时区和数码管功能

### v1.0.0 (2026-03-15)
- ✅ 初始版本发布
- ✅ 模拟时钟显示
- ✅ 数字时钟显示
- ✅ 多时区支持
- ✅ 模式切换功能

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

## 👤 作者

ClawClock Development Team

---

## 📮 联系方式

- GitHub: [项目地址]
- Email: [联系邮箱]
