# 📦 ClawClock 安装指南

本指南将帮助您在 Linux 系统上安装和配置 ClawClock 时钟应用。

---

## 🎯 系统要求

- **操作系统**: Linux (Debian/Ubuntu/Arch/Fedora)
- **Python 版本**: Python 3.8+
- **图形环境**: X11 或 Wayland
- **磁盘空间**: 至少 10MB

---

## 🚀 快速安装

### 方法一：一键安装脚本（推荐）

```bash
# 进入项目目录
cd /home/lenovo/AItest/clawclock

# 赋予执行权限
chmod +x install.sh

# 运行安装脚本
./install.sh
```

安装脚本会自动：
- ✅ 检测系统类型
- ✅ 安装 Python 和 tkinter 依赖
- ✅ 安装时区数据库
- ✅ 验证安装完整性

---

### 方法二：手动安装

#### 1. 安装 Python 和依赖

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install python3 python3-tk python3-tz
```

**Arch Linux:**
```bash
sudo pacman -S tk python-tz
```

**Fedora:**
```bash
sudo dnf install python3-tkinter python3-dateutil
```

#### 2. 验证安装

```bash
# 检查 Python 版本
python3 --version  # 应 >= 3.8

# 检查 tkinter 可用性
python3 -c "import tkinter; print('tkinter 版本:', tkinter.TkVersion)"

# 检查时区支持
python3 -c "import datetime; print('时区支持 OK')"
```

---

## 📥 获取源代码

### 方式一：Git 克隆

```bash
git clone https://github.com/yourusername/clawclock.git
cd clawclock
```

### 方式二：下载 ZIP

```bash
wget https://github.com/yourusername/clawclock/archive/main.zip
unzip main.zip
cd clawclock-main
```

---

## 🔧 配置环境

### 1. 配置文件说明

应用会自动创建 `config.json` 配置文件，位置：
- **项目目录**: `/home/lenovo/AItest/clawclock/config.json`
- **用户目录**: `~/.openclaw/workspace/clawclock/config.json`

### 2. 默认配置

```json
{
  "timezone": "Asia/Shanghai",
  "display_mode": "analog",
  "window": {
    "width": 600,
    "height": 500,
    "resizable": false
  },
  "theme": {
    "name": "dark",
    "colors": {
      "background": "#1a1a2e",
      "face": "#16213e",
      "hand": "#e94560",
      "text": "#ffffff",
      "accent": "#0f3460",
      "segment_on": "#ff3333",
      "segment_off": "#331111"
    }
  }
}
```

### 3. 自定义配置

编辑 `config.json` 文件，修改参数后重启应用即可生效。

---

## 🎨 安装主题（可选）

### 1. 查看可用主题

```bash
ls themes/
```

### 2. 安装自定义主题

```bash
# 复制示例主题
cp themes/dark.json themes/my-theme.json

# 编辑主题文件
nano themes/my-theme.json
```

### 3. 应用主题

在 `config.json` 中修改：
```json
{
  "theme": {
    "name": "my-theme"
  }
}
```

---

## ✅ 验证安装

### 运行测试套件

```bash
# 运行测试脚本
./run_tests.sh

# 详细输出模式
./run_tests.sh -v
```

### 启动应用

```bash
python3 clock.py
```

如果看到时钟窗口正常显示，说明安装成功！

---

## 🛠️ 故障排除

### 问题 1: tkinter 导入错误

**错误信息**: `ModuleNotFoundError: No module named '_tkinter'`

**解决方案**:
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Arch Linux
sudo pacman -S tk

# Fedora
sudo dnf install python3-tkinter
```

### 问题 2: 时区数据库缺失

**错误信息**: `ModuleNotFoundError: No module named 'tz'`

**解决方案**:
```bash
# Debian/Ubuntu
sudo apt install python3-tz

# Arch Linux
sudo pacman -S python-tz

# Fedora
sudo dnf install python3-dateutil
```

### 问题 3: 图形界面无法显示

**错误信息**: `no display name and no $DISPLAY environment variable`

**解决方案**:
```bash
# 检查 DISPLAY 环境变量
echo $DISPLAY

# 如果是 SSH 连接，启用 X11 转发
ssh -X user@hostname

# 或在本地终端运行
export DISPLAY=:0
python3 clock.py
```

### 问题 4: 权限不足

**错误信息**: `Permission denied`

**解决方案**:
```bash
# 赋予执行权限
chmod +x install.sh run_tests.sh

# 或使用 sudo 运行安装
sudo ./install.sh
```

---

## 📦 卸载

如需卸载 ClawClock：

```bash
# 删除项目目录
rm -rf /home/lenovo/AItest/clawclock

# 删除用户配置
rm -rf ~/.openclaw/workspace/clawclock/

# 删除系统级安装（如果使用 sudo 安装）
sudo rm -rf /opt/clawclock/
```

---

## 🆘 获取帮助

如果安装过程中遇到问题：

1. **查看日志**: 运行 `./install.sh 2>&1 | tee install.log`
2. **检查 FAQ**: 阅读 `FAQ.md` 文档
3. **提交 Issue**: 在 GitHub 仓库创建 Issue
4. **联系支持**: 发送邮件至支持邮箱

---

## 📝 下一步

安装完成后，请查看：
- 📖 [README.md](README.md) - 使用说明和功能介绍
- 🎮 [TUTORIAL.md](TUTORIAL.md) - 详细教程
- ❓ [FAQ.md](FAQ.md) - 常见问题解答

---

*最后更新：2026-03-18*  
*ClawClock 版本：v1.3.0*

---

## 🆕 v1.3.0 新增功能

### ⏱️ 秒表功能

v1.3.0 版本新增专业级秒表功能，**无需额外安装依赖**！

**新增内容：**
- 秒表计时器（10ms 精度）
- 启动/停止/复位控制
- 计圈记录功能
- 7 段数码管显示

**使用说明：**
1. 按照本指南安装 ClawClock
2. 运行 `python3 clock.py` 启动应用
3. 点击"⏱️ 秒表"模式即可使用

**兼容性：**
- ✅ 与现有系统完全兼容
- ✅ 无需额外依赖包
- ✅ 旧配置文件兼容
- ✅ 升级后配置自动保留

**升级方法：**
```bash
# 进入项目目录
cd /home/lenovo/AItest/clawclock

# 拉取最新代码
git pull origin main

# 重启应用
python3 clock.py
```
