# 📦 ClawClock 安装指南

本指南帮助您在 Linux 系统上快速安装和配置 ClawClock 时钟应用。

---

## 🎯 系统要求

| 要求 | 说明 |
|------|------|
| 操作系统 | Linux (Debian/Ubuntu/Arch/Fedora) |
| Python 版本 | 3.8+ |
| 图形环境 | X11 或 Wayland |
| 磁盘空间 | 10MB |

---

## 🚀 快速安装

### 方法一：一键安装脚本（推荐）

```bash
cd /home/lenovo/AItest/clawclock
chmod +x install.sh
./install.sh
```

安装脚本自动完成：
- ✅ 系统类型检测
- ✅ Python 和 tkinter 依赖安装
- ✅ 时区数据库安装
- ✅ 安装完整性验证

---

### 方法二：手动安装

#### 1. 安装依赖

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install python3 python3-tk python3-tz

# Arch Linux
sudo pacman -S tk python-tz

# Fedora
sudo dnf install python3-tkinter python3-dateutil
```

#### 2. 验证安装

```bash
python3 --version  # 应 >= 3.8
python3 -c "import tkinter; print('tkinter OK')"
```

---

## 📥 获取源代码

```bash
# Git 克隆
git clone https://github.com/yourusername/clawclock.git
cd clawclock

# 或下载 ZIP
wget https://github.com/yourusername/clawclock/archive/main.zip
unzip main.zip && cd clawclock-main
```

---

## 🔧 配置环境

### 配置文件

应用自动创建 `config.json`，位置：
- 项目目录：`/home/lenovo/AItest/clawclock/config.json`
- 用户目录：`~/.openclaw/workspace/clawclock/config.json`

### 默认配置

```json
{
  "timezone": "Asia/Shanghai",
  "display_mode": "analog",
  "window": { "width": 600, "height": 500 },
  "theme": { "name": "dark" }
}
```

编辑后重启应用生效。

---

## 🎨 自定义主题（可选）

```bash
# 复制示例主题
cp themes/dark.json themes/my-theme.json

# 编辑主题文件
nano themes/my-theme.json

# 在 config.json 中应用
# "theme": { "name": "my-theme" }
```

---

## ✅ 验证安装

```bash
# 运行测试
./run_tests.sh

# 启动应用
python3 clock.py
```

看到时钟窗口即表示安装成功！

---

## 🛠️ 故障排除

| 问题 | 解决方案 |
|------|----------|
| **tkinter 导入错误**<br>`No module named '_tkinter'` | `sudo apt install python3-tk`<br>`sudo pacman -S tk`<br>`sudo dnf install python3-tkinter` |
| **时区数据库缺失**<br>`No module named 'tz'` | `sudo apt install python3-tz`<br>`sudo pacman -S python-tz` |
| **图形界面无法显示**<br>`no $DISPLAY` | `echo $DISPLAY` 检查环境变量<br>SSH 连接使用 `ssh -X`<br>本地运行 `export DISPLAY=:0` |
| **权限不足**<br>`Permission denied` | `chmod +x install.sh run_tests.sh` |

---

## 📦 卸载

```bash
rm -rf /home/lenovo/AItest/clawclock
rm -rf ~/.openclaw/workspace/clawclock/
```

---

## 🆘 获取帮助

1. 查看日志：`./install.sh 2>&1 | tee install.log`
2. 阅读 [FAQ.md](FAQ.md)
3. 提交 GitHub Issue

---

## 📝 下一步

- 📖 [README.md](README.md) - 功能介绍
- 🎮 [TUTORIAL.md](TUTORIAL.md) - 使用教程
- ❓ [FAQ.md](FAQ.md) - 常见问题

---

*最后更新：2026-03-18 | ClawClock v1.5.1*
