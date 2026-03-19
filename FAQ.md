# ❓ ClawClock 常见问题解答 (FAQ)

本文档收录了 ClawClock 使用过程中常见的问题及解决方案。

---

## ⏳ 零、倒计时功能问题

### 0.1 如何进入倒计时模式

**问题描述：**  
找不到倒计时功能在哪里。

**解决方案：**

1. 启动 ClawClock 应用
2. 在界面顶部模式选择区域，找到模式单选按钮
3. 点击"⏳ 倒计时"单选按钮
4. 界面自动切换至倒计时专用界面

**模式说明：**
- 🕐 Analog - 模拟时钟模式（指针式）
- 🔢 Digital - 数字时钟模式（7 段数码管）
- ⏱️ Stopwatch - 秒表计时模式
- ⏳ Timer - 倒计时模式

---

### 0.2 预设时间有哪些

**问题描述：**  
想知道有哪些预设时间可以使用。

**答案：**

ClawClock v1.4.0 提供 6 种内置预设时间：

| 预设名称 | 时长 | 使用场景 |
|----------|------|----------|
| 🍅 番茄钟 | 25 分钟 | 专注工作、深度学习 |
| ☕ 短休息 | 5 分钟 | 番茄钟间隔休息 |
| 🛌 长休息 | 15 分钟 | 长时间工作后恢复 |
| ⏱️ 5 分钟 | 5 分钟 | 快速任务、热身 |
| ⏱️ 10 分钟 | 10 分钟 | 中等任务、冥想 |
| ⏱️ 30 分钟 | 30 分钟 | 会议、练习、复习 |

**使用方法**：点击对应预设按钮即可快速设置

---

### 0.3 如何自定义倒计时时长

**问题描述：**  
预设时间不满足需求，想设置自定义时长。

**解决方案：**

**方法一：手动输入**
1. 在时间输入框中直接输入小时、分钟、秒
2. 或使用上下箭头调整数值
3. 点击"▶️ 开始"启动倒计时

**方法二：添加自定义预设（开发者）**
编辑 `timer.py` 文件，在 `PRESET_TIMES` 列表中添加：
```python
PresetTime("自定义 45 分钟", minutes=45)
```

---

### 0.4 倒计时能暂停吗

**问题描述：**  
倒计时开始后，是否可以暂停然后继续。

**答案：** **可以！**

**操作方法：**
1. 倒计时运行时点击"⏸️ 暂停"按钮
2. 倒计时停止，按钮变为"▶️ 继续"
3. 点击"▶️ 继续"按钮恢复倒计时
4. 倒计时从暂停时刻继续减少

**特点：**
- 暂停期间时间不减少
- 继续后无缝衔接
- 可多次暂停/继续循环

---

### 0.5 时间到有什么提醒

**问题描述：**  
倒计时结束时如何知道。

**答案：**

倒计时结束时提供**双重提醒**：

1. **视觉提醒**：
   - 时间显示区域红色闪烁
   - 显示"⏰ 时间到！"提示

2. **声音提醒**：
   - 播放系统提示音
   - 可通过"🔊 声音"按钮开关

**关闭提醒**：点击任意按钮或重置倒计时

---

### 0.6 如何添加自定义预设时间

**问题描述：**  
想添加自己常用的预设时间。

**解决方案：**

**开发者方式**：
1. 打开 `timer.py` 文件
2. 找到 `PRESET_TIMES` 列表
3. 添加新的预设时间：

```python
PRESET_TIMES = [
    PresetTime("🍅 番茄钟", minutes=25),
    PresetTime("☕ 短休息", minutes=5),
    # 添加你的自定义预设
    PresetTime("🎯 会议时间", minutes=60),
    PresetTime("🧘 冥想", minutes=10),
    PresetTime("📚 深度学习", minutes=45),
]
```

4. 保存文件并重启应用

**未来计划**：
- v1.5.0 计划添加 UI 界面自定义预设
- 支持保存用户自定义预设
- 预设导入/导出功能

---

### 0.7 倒计时能后台运行吗

**问题描述：**  
切换到其他应用时，倒计时是否继续。

**答案：** **可以！**

- 倒计时在 ClawClock 窗口内独立运行
- 切换窗口或最小化不影响倒计时
- 但请**不要关闭**ClawClock 窗口

**注意：**
- 关闭 ClawClock 窗口会停止倒计时
- 长时间倒计时请保持电脑不休眠
- 系统休眠/睡眠会暂停倒计时

---

### 0.8 如何使用番茄工作法

**问题描述：**  
想用 ClawClock 实践番茄工作法。

**操作步骤：**

1. **设置番茄钟**：点击"🍅 番茄钟"预设（25 分钟）
2. **开始工作**：点击"▶️ 开始"，专注工作 25 分钟
3. **时间到休息**：点击"☕ 短休息"（5 分钟）
4. **重复循环**：每 4 个番茄钟后，使用"🛌 长休息"（15 分钟）

**标准流程**：
```
番茄 1 (25 分钟) → 短休息 (5 分钟)
番茄 2 (25 分钟) → 短休息 (5 分钟)
番茄 3 (25 分钟) → 短休息 (5 分钟)
番茄 4 (25 分钟) → 长休息 (15-30 分钟)
```

**技巧**：
- 每个番茄钟专注单一任务
- 休息时间必须离开工作环境
- 记录完成的番茄钟数量

---

## ⏱️ 一、秒表功能问题

### 0.1 如何进入秒表模式

**问题描述：**  
找不到秒表功能在哪里。

**解决方案：**

1. 启动 ClawClock 应用
2. 在界面顶部模式选择区域，找到三个单选按钮
3. 点击"⏱️ 秒表"单选按钮
4. 界面自动切换至秒表专用界面

**模式说明：**
- 🕐 Analog - 模拟时钟模式（指针式）
- 🔢 Digital - 数字时钟模式（7 段数码管）
- ⏱️ Stopwatch - 秒表计时模式

---

### 0.2 秒表精度是多少

**问题描述：**  
想知道秒表的计时精度。

**答案：**

- **刷新率**：10ms（0.01 秒，100Hz）
- **显示精度**：百分之一秒（0.00-0.99）
- **时间格式**：`HH:MM:SS.ms`
  - `HH`：小时（00-99）
  - `MM`：分钟（00-59）
  - `SS`：秒钟（00-59）
  - `ms`：百分秒（00-99）

**示例**：`00:05:23.45` 表示 5 分 23 秒 45 百分秒

---

### 0.3 如何使用计圈功能

**问题描述：**  
想知道如何记录多圈时间。

**操作步骤：**

1. 启动秒表（点击"▶️ 开始"）
2. 在计时过程中，点击"📍 计圈"按钮
3. 每次点击记录一圈时间
4. 计圈记录显示在下方列表

**计圈数据显示：**
- **圈数**：第几圈（从 1 开始递增）
- **累计时间**：从开始到当前的总时间
- **单圈时间**：上一圈到当前圈的时间

**示例：**
```
圈 01 | 00:00:15.23 | 00:00:15.23  (第一圈，累计=单圈)
圈 02 | 00:00:31.45 | 00:00:16.22  (第二圈，单圈=31.45-15.23)
圈 03 | 00:00:46.89 | 00:00:15.44  (第三圈，单圈=46.89-31.45)
```

**注意：**
- 秒表暂停时也可以计圈
- 计圈记录无数量限制
- 复位后清空所有计圈记录

---

### 0.4 秒表暂停后能继续吗

**问题描述：**  
暂停秒表后，是否可以继续计时而不是重置。

**答案：** **可以！**

**操作方法：**
1. 秒表运行时点击"⏸️ 停止"按钮暂停
2. 按钮变为"▶️ 继续"
3. 点击"▶️ 继续"按钮恢复计时
4. 秒表从暂停时刻继续累加时间

**特点：**
- 暂停期间时间不累加
- 继续后无缝衔接
- 可多次暂停/继续循环

---

### 0.5 如何清空计圈记录

**问题描述：**  
想清除所有计圈记录，但不重置时间。

**答案：**

目前计圈记录只能通过**复位**功能清空：

1. 点击"🔄 复位"按钮
2. 时间和计圈记录全部清零
3. 秒表恢复初始状态

**注意：**
- 复位操作不可撤销
- 复位前请确保已记录需要的数据
- 可在复位前截图保存计圈记录

---

### 0.6 秒表能后台运行吗

**问题描述：**  
切换到其他应用时，秒表是否继续计时。

**答案：** **可以！**

- 秒表在 ClawClock 窗口内独立运行
- 切换窗口或最小化不影响计时
- 但请**不要关闭**ClawClock 窗口

**注意：**
- 关闭 ClawClock 窗口会停止秒表
- 长时间计时请保持电脑不休眠
- 系统休眠/睡眠会暂停计时

---

### 0.7 计圈记录能导出吗

**问题描述：**  
想保存或导出计圈记录数据。

**当前状态：**

v1.3.0 版本暂不支持导出功能，计圈记录仅显示在界面上。

**临时方案：**
1. 截图保存计圈列表
2. 手动记录重要数据
3. 使用屏幕录制软件记录全过程

**未来计划：**
- v1.4.0 计划添加导出功能（CSV/TXT）
- 支持复制计圈记录到剪贴板
- 添加计圈统计（最快圈、最慢圈、平均圈速）

---

## 📦 一、安装问题

### 1.1 依赖安装失败怎么办

**问题描述：**  
运行 `install.sh` 或手动安装依赖时出现错误，提示某些包无法安装。

**原因分析：**
- 系统软件源过期或不可用
- 网络连接问题
- 系统权限不足
- 包名称在不同发行版中不同

**解决方案：**

1. **更新软件源**
   ```bash
   sudo apt update  # Debian/Ubuntu
   sudo dnf check-update  # Fedora
   sudo pacman -Sy  # Arch
   ```

2. **检查网络连接**
   ```bash
   ping -c 4 github.com
   ```

3. **使用正确的包管理器**
   ```bash
   # Debian/Ubuntu
   sudo apt install python3 python3-pip python3-tk
   
   # Fedora
   sudo dnf install python3 python3-pip python3-tkinter
   
   # Arch Linux
   sudo pacman -S python python-pip tk
   ```

4. **使用 pip 安装 Python 依赖**
   ```bash
   pip3 install --user -r requirements.txt
   ```

**相关命令：**
```bash
# 验证 Python 安装
python3 --version

# 验证 pip 安装
pip3 --version

# 验证 tkinter 可用性
python3 -c "import tkinter; print('tkinter OK')"
```

---

### 1.2 Python 版本不兼容

**问题描述：**  
运行时提示 Python 版本过低或过高，某些语法不支持。

**原因分析：**
- ClawClock 需要 Python 3.7+
- 系统默认 Python 版本过旧
- 使用了 Python 2 而非 Python 3

**解决方案：**

1. **检查 Python 版本**
   ```bash
   python3 --version
   ```

2. **安装合适的 Python 版本**
   ```bash
   # Ubuntu/Debian - 使用 deadsnakes PPA
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   sudo apt install python3.10 python3.10-tk
   
   # 或使用 pyenv 管理多版本
   curl https://pyenv.run | bash
   pyenv install 3.10.0
   pyenv global 3.10.0
   ```

3. **指定 Python 版本运行**
   ```bash
   python3.10 clock.py
   ```

**相关命令：**
```bash
# 查看系统 Python 路径
which python3

# 查看可用的 Python 版本
ls /usr/bin/python*
```

---

### 1.3 tkinter 缺失问题

**问题描述：**  
运行时提示 `ModuleNotFoundError: No module named '_tkinter'`

**原因分析：**
- Python 编译时未启用 tkinter 支持
- 系统未安装 tkinter 包
- 虚拟环境中未正确安装

**解决方案：**

1. **安装系统级 tkinter 包**
   ```bash
   # Debian/Ubuntu
   sudo apt install python3-tk
   
   # Fedora
   sudo dnf install python3-tkinter
   
   # Arch Linux
   sudo pacman -S tk
   
   # macOS (使用 Homebrew)
   brew install python-tk
   ```

2. **验证安装**
   ```bash
   python3 -c "import tkinter; print('tkinter 版本:', tkinter.TkVersion)"
   ```

3. **重新创建虚拟环境**
   ```bash
   # 删除旧虚拟环境
   rm -rf venv/
   
   # 创建新虚拟环境
   python3 -m venv venv
   source venv/bin/activate
   
   # 重新安装依赖
   pip install -r requirements.txt
   ```

**相关命令：**
```bash
# 测试 tkinter 导入
python3 -c "import tkinter as tk; root = tk.Tk(); root.destroy(); print('Success!')"
```

---

## 🚀 二、运行问题

### 2.1 应用无法启动

**问题描述：**  
运行 `python3 clock.py` 后无任何反应，或立即退出。

**原因分析：**
- 缺少图形界面环境 (X11/Wayland)
- DISPLAY 环境变量未设置
- 代码存在语法错误
- 依赖文件缺失

**解决方案：**

1. **检查图形环境**
   ```bash
   echo $DISPLAY
   # 应输出 :0 或类似值
   ```

2. **SSH 远程运行时启用 X11 转发**
   ```bash
   ssh -X user@hostname
   # 或
   ssh -Y user@hostname  # 可信 X11 转发
   ```

3. **检查错误输出**
   ```bash
   python3 clock.py 2>&1 | tee debug.log
   ```

4. **验证文件完整性**
   ```bash
   ls -la clock.py config.json
   ```

**相关命令：**
```bash
# 检查 X11 连接
xdpyinfo | grep version

# 测试简单 tkinter 窗口
python3 -c "import tkinter as tk; tk.Tk().mainloop()"
```

---

### 2.2 显示异常/花屏

**问题描述：**  
时钟界面显示乱码、花屏、颜色异常或窗口闪烁。

**原因分析：**
- 显卡驱动问题
- 高 DPI 屏幕缩放问题
- 颜色配置错误
- 刷新率设置不当

**解决方案：**

1. **调整 DPI 缩放**
   ```bash
   # 设置 Tkinter 缩放因子
   export TK_SCALING=1.5
   python3 clock.py
   ```

2. **检查主题配置**
   ```bash
   # 查看当前主题
   cat config.json | grep theme
   
   # 重置为默认主题
   cp themes/default.json config.json
   ```

3. **更新显卡驱动**
   ```bash
   # Ubuntu/NVIDIA
   sudo ubuntu-drivers autoinstall
   
   # 通用更新
   sudo apt update && sudo apt upgrade
   ```

4. **降低刷新率测试**
   在 `config.json` 中修改：
   ```json
   {
     "refresh_rate": 500
   }
   ```

**相关命令：**
```bash
# 查看屏幕分辨率和 DPI
xdpyinfo | grep -E "dimensions|resolution"

# 查看显卡信息
lspci | grep VGA
```

---

### 2.3 时区切换无响应

**问题描述：**  
点击时区下拉菜单后无反应，或选择时区后时间不更新。

**原因分析：**
- 事件循环阻塞
- 时区数据加载失败
- 回调函数未正确绑定
- 配置文件损坏

**解决方案：**

1. **检查控制台错误**
   ```bash
   python3 clock.py 2>&1 | grep -i timezone
   ```

2. **重置配置文件**
   ```bash
   # 备份当前配置
   mv config.json config.json.bak
   
   # 创建默认配置
   echo '{"timezone": "UTC", "theme": "default", "refresh_rate": 1000}' > config.json
   ```

3. **重启应用**
   ```bash
   # 完全退出并重启
   pkill -f clock.py
   python3 clock.py
   ```

4. **检查时区数据**
   ```bash
   # 验证 Python 时区支持
   python3 -c "from datetime import datetime; import pytz; print(pytz.all_timezones[:5])"
   ```

**相关命令：**
```bash
# 查看系统时区
timedatectl

# 列出可用时区
python3 -c "import pytz; print(len(pytz.all_timezones))"
```

---

## ⚙️ 三、配置问题

### 3.1 配置文件位置

**问题描述：**  
不知道配置文件在哪里，或修改后不生效。

**原因分析：**
- 配置文件路径不清晰
- 存在多个配置文件
- 相对路径和绝对路径混淆

**解决方案：**

1. **查找配置文件**
   ```bash
   # 在项目目录查找
   find /home/lenovo/AItest/clawclock -name "config.json"
   
   # 或在用户主目录
   find ~/.config -name "clawclock*" 2>/dev/null
   ```

2. **配置文件优先级**
   - 当前目录：`./config.json` (最高优先级)
   - 用户配置：`~/.config/clawclock/config.json`
   - 系统配置：`/etc/clawclock/config.json` (最低优先级)

3. **查看当前使用的配置**
   ```bash
   # 启动时打印配置路径
   python3 clock.py --verbose 2>&1 | grep config
   ```

**配置文件示例：**
```json
{
  "timezone": "Asia/Shanghai",
  "theme": "default",
  "refresh_rate": 1000,
  "window_size": "800x600",
  "show_both_modes": false
}
```

**相关命令：**
```bash
# 查看当前目录
pwd

# 查看配置内容
cat config.json | python3 -m json.tool
```

---

### 3.2 如何重置配置

**问题描述：**  
配置混乱，想恢复到初始状态。

**原因分析：**
- 多次修改导致配置冲突
- 实验性配置未清理
- 需要排除配置问题

**解决方案：**

1. **备份当前配置**
   ```bash
   cp config.json config.json.backup.$(date +%Y%m%d)
   ```

2. **删除配置文件**
   ```bash
   rm config.json
   ```

3. **使用默认配置启动**
   ```bash
   # 应用会自动创建默认配置
   python3 clock.py
   ```

4. **或手动创建默认配置**
   ```bash
   cat > config.json << 'EOF'
   {
     "timezone": "UTC",
     "theme": "default",
     "refresh_rate": 1000,
     "window_size": "800x600",
     "show_both_modes": false,
     "font_size": 12
   }
   EOF
   ```

**相关命令：**
```bash
# 查看备份文件
ls -la config.json.backup.*

# 恢复备份
mv config.json.backup.20260317 config.json
```

---

### 3.3 自定义颜色主题

**问题描述：**  
想修改时钟颜色主题，但不知道如何操作。

**原因分析：**
- 主题配置结构不清晰
- 颜色格式不熟悉
- 不知道主题文件位置

**解决方案：**

1. **查看现有主题**
   ```bash
   ls themes/
   cat themes/default.json
   ```

2. **创建自定义主题**
   ```bash
   cp themes/default.json themes/mytheme.json
   ```

3. **编辑主题文件**
   ```json
   {
     "name": "My Custom Theme",
     "background": "#1a1a2e",
     "clock_face": "#16213e",
     "hour_hand": "#e94560",
     "minute_hand": "#0f3460",
     "second_hand": "#e94560",
     "digital_color": "#e94560",
     "text_color": "#ffffff"
   }
   ```

4. **应用新主题**
   在 `config.json` 中修改：
   ```json
   {
     "theme": "mytheme"
   }
   ```

**颜色格式：**
- 十六进制：`#RRGGBB` (如 `#ff0000` 红色)
- RGB 元组：`(255, 0, 0)`
- 颜色名称：`"red"`, `"blue"`, `"green"`

**相关命令：**
```bash
# 使用文本编辑器修改
nano themes/mytheme.json
# 或
code themes/mytheme.json
```

---

## 🔧 四、功能问题

### 4.1 如何添加新时区

**问题描述：**  
时区列表中没有想要的城市，想添加新时区。

**原因分析：**
- 时区列表是预定义的
- 需要修改源码或配置

**解决方案：**

1. **查看支持的时区**
   ```bash
   python3 -c "import pytz; tz = pytz.timezone('Asia/Shanghai'); print(tz)"
   ```

2. **在代码中添加时区映射**
   编辑 `clock.py`，找到时区列表部分：
   ```python
   TIMEZONES = [
       ("UTC+0 伦敦", "Europe/London"),
       ("UTC+1 巴黎", "Europe/Paris"),
       ("UTC+8 北京", "Asia/Shanghai"),
       ("UTC+9 东京", "Asia/Tokyo"),
       # 添加新时区
       ("UTC+10 悉尼", "Australia/Sydney"),
   ]
   ```

3. **查找标准时区名称**
   ```bash
   python3 << 'EOF'
   import pytz
   for tz in pytz.all_timezones:
       if 'sydney' in tz.lower():
           print(tz)
   EOF
   ```

4. **重启应用生效**
   ```bash
   pkill -f clock.py
   python3 clock.py
   ```

**相关命令：**
```bash
# 搜索特定时区
python3 -c "import pytz; print([t for t in pytz.all_timezones if 'America' in t][:10])"

# 查看时区当前时间
python3 -c "from datetime import datetime; import pytz; print(datetime.now(pytz.timezone('America/New_York')))"
```

---

### 4.2 如何修改刷新率

**问题描述：**  
时钟刷新太快耗电，或太慢显示卡顿，想调整刷新率。

**原因分析：**
- 刷新率控制动画流畅度
- 默认值可能不适合所有场景

**解决方案：**

1. **在配置文件中修改**
   编辑 `config.json`：
   ```json
   {
     "refresh_rate": 500  // 毫秒，数值越大刷新越慢
   }
   ```

2. **推荐刷新率设置**
   - 秒针平滑：`100-250ms` (最流畅，耗电高)
   - 标准秒针：`1000ms` (默认，每秒一跳)
   - 省电模式：`2000-5000ms` (适合后台运行)

3. **在代码中修改（高级）**
   编辑 `clock.py`，找到刷新设置：
   ```python
   REFRESH_RATE = 1000  # 毫秒
   self.root.after(REFRESH_RATE, self.update_clock)
   ```

4. **测试不同刷新率**
   ```bash
   # 创建测试配置
   echo '{"refresh_rate": 500}' > test_config.json
   python3 clock.py --config test_config.json
   ```

**相关命令：**
```bash
# 监控 CPU 使用率
top -p $(pgrep -f clock.py)

# 查看当前刷新率设置
cat config.json | grep refresh_rate
```

---

### 4.3 如何调整窗口大小

**问题描述：**  
时钟窗口太大或太小，想调整尺寸。

**原因分析：**
- 窗口大小在代码中硬编码
- 配置文件可能支持尺寸设置

**解决方案：**

1. **在配置文件中修改**
   编辑 `config.json`：
   ```json
   {
     "window_size": "1024x768"
   }
   ```

2. **在代码中修改**
   编辑 `clock.py`，找到窗口设置：
   ```python
   # 修改此行
   self.root.geometry("800x600")
   
   # 可选：设置最小/最大尺寸
   self.root.minsize(600, 400)
   self.root.maxsize(1920, 1080)
   ```

3. **启用窗口大小调整**
   如果窗口被锁定，修改代码：
   ```python
   # 注释或删除此行
   # self.root.resizable(False, False)
   
   # 或改为
   self.root.resizable(True, True)
   ```

4. **全屏模式**
   ```python
   # 在 clock.py 中添加
   self.root.attributes('-fullscreen', True)
   
   # 退出全屏按 Esc
   self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
   ```

**推荐尺寸：**
- 小窗口：`400x300`
- 标准：`800x600` (默认)
- 大窗口：`1024x768`
- 全屏：自动检测

**相关命令：**
```bash
# 查看当前屏幕分辨率
xrandr | grep "*"

# 测试不同尺寸
python3 -c "import tkinter as tk; r = tk.Tk(); r.geometry('1024x768'); r.mainloop()"
```

---

## 🏗️ 六、v1.6.0 模块化架构问题

### 6.1 什么是模块化架构

**问题描述：**  
看到 v1.6.0 提到了模块化重构，想知道这是什么意思。

**答案：**

v1.6.0 将原本集中在 `clock.py` 的功能拆分为独立的模块：

| 模块 | 职责 | 文件数 |
|------|------|--------|
| `config/` | 配置管理、持久化 | 4 个文件 |
| `effects/` | 呼吸灯、动画系统 | 2 个文件 |
| `utils/` | 错误处理、日志系统 | 2 个文件 |
| `main.py` | 主程序入口 | 1 个文件 |

**好处：**
- ✅ 代码更易维护和扩展
- ✅ 模块可独立测试
- ✅ 便于团队协作开发
- ✅ 降低代码耦合度

---

### 6.2 如何升级到我的项目

**问题描述：**  
想在 ClawClock 中使用 v1.6.0 的模块化架构。

**解决方案：**

**步骤 1：复制模块文件**
```bash
# 从 ClawClock 复制模块到你的项目
cp -r clawclock/config/ your_project/
cp -r clawclock/effects/ your_project/
cp -r clawclock/utils/ your_project/
cp clawclock/main.py your_project/
```

**步骤 2：导入模块**
```python
# 在你的代码中导入
from config.settings import get_config_manager
from effects.breath_light import BreathLightEffect
from utils.logger import info
```

**步骤 3：修改导入路径**
如果你的项目结构不同，调整导入路径：
```python
# 相对导入
from .config.settings import get_config_manager

# 或修改 sys.path
import sys
sys.path.insert(0, '/path/to/clawclock')
```

---

### 6.3 配置模块如何使用

**问题描述：**  
想了解 config 模块的具体用法。

**答案：**

**基本用法：**
```python
from config.settings import get_config_manager

# 获取配置管理器
config = get_config_manager()

# 读取配置
value = config.get("timezone")

# 设置配置
config.set("theme", "dark")

# 保存配置
config.save()
```

**嵌套配置：**
```python
# 使用点号访问嵌套配置
breath_freq = config.get("breath_light.frequency")
config.set("breath_light.enabled", True)
```

**默认配置：**
```python
# 获取配置，如果不存在则返回默认值
timezone = config.get("timezone", default="Asia/Shanghai")
```

---

### 6.4 如何使用呼吸灯模块

**问题描述：**  
想在自己的项目中复用呼吸灯效果。

**答案：**

**基础使用：**
```python
from effects.breath_light import BreathLightEffect, BreathStyle

# 创建效果实例
effect = BreathLightEffect()

# 设置风格
effect.set_style(BreathStyle.SOFT)

# 更新效果（传入经过的时间）
color = effect.update(elapsed_time=0.5)
print(color)  # 输出：#00d4aa (示例)
```

**自定义配置：**
```python
from effects.breath_light import BreathLightConfig, BreathLightEffect

# 创建自定义配置
config = BreathLightConfig(
    frequency=0.8,
    intensity=0.6,
    style="tech"
)

# 使用自定义配置创建效果
effect = BreathLightEffect(config)
```

**状态切换：**
```python
from effects.breath_light import TimerStatus

# 正常状态（绿色）
effect.set_status(TimerStatus.NORMAL)

# 警告状态（橙色，最后 10 秒）
effect.set_status(TimerStatus.WARNING)

# 完成状态（红色，时间到）
effect.set_status(TimerStatus.COMPLETED)
```

---

### 6.5 错误处理模块有哪些异常类

**问题描述：**  
想了解可用的异常类型。

**答案：**

**异常类层次结构：**
```
ClockError (基础异常)
├── ConfigError (配置错误)
├── ThemeError (主题错误)
├── AlarmError (闹钟错误)
├── TimerError (倒计时错误)
└── IOError (IO 错误)
```

**使用示例：**
```python
from utils.errors import TimerError, validate_time_format

try:
    validate_time_format("25:00")  # 无效时间
except TimerError as e:
    print(f"时间错误：{e}")
```

**验证函数：**
- `validate_time_format(time_str)` - 验证 HH:MM 格式
- `validate_preset_time(hours, minutes, seconds)` - 验证预设时间

---

### 6.6 日志系统如何使用

**问题描述：**  
想了解如何记录日志。

**答案：**

**快速使用：**
```python
from utils.logger import info, warning, error

info("应用启动")
warning("配置不存在，使用默认值")
error("文件读取失败")
```

**带上下文的日志：**
```python
from utils.logger import set_context, debug

set_context(module="clock", func="init", line=42)
debug("初始化完成")
```

**自定义日志记录器：**
```python
from utils.logger import ClockLogger

logger = ClockLogger(name="my_module")
logger.info("自定义日志")
```

**日志级别：**
- `debug()` - 调试信息（开发时使用）
- `info()` - 一般信息
- `warning()` - 警告信息
- `error()` - 错误信息
- `critical()` - 严重错误

---

### 6.7 测试覆盖率如何

**问题描述：**  
想知道 v1.6.0 的测试情况。

**答案：**

**测试统计：**
- ✅ **146 个测试用例**
- ✅ **100% 通过率**
- ✅ 覆盖配置、呼吸灯、动画、错误处理等模块

**运行测试：**
```bash
# 运行完整测试套件
bash run_tests.sh

# 运行特定模块测试
python3 -m unittest tests.test_breath_light -v
```

**测试报告：**
```
🕐 ClawClock 自动化测试
========================

📦 使用 unittest 运行测试...

..................................................................................................................................................
----------------------------------------------------------------------
Ran 146 tests in 2.996s

OK ✅ 所有测试通过！
```

---

### 6.8 向后兼容性如何

**问题描述：**  
升级 v1.6.0 后，旧代码还能用吗？

**答案：** **完全兼容！**

- ✅ `clock.py` 保持不变，可继续运行
- ✅ 配置文件格式完全兼容
- ✅ 所有 API 接口保持不变
- ✅ 旧版功能全部保留

**升级步骤：**
```bash
# 1. 备份配置
cp config.json config.json.bak

# 2. 拉取新代码
git pull origin main

# 3. 运行（命令不变）
python3 clock.py
```

---

### 6.9 性能有提升吗

**问题描述：**  
模块化后性能会不会变差。

**答案：** **性能略有提升！**

**优化措施：**
- ✅ 颜色缓存减少重复计算
- ✅ 配置加载优化
- ✅ 减少全局变量访问

**性能对比：**
| 指标 | v1.5.1 | v1.6.0 | 变化 |
|------|--------|--------|------|
| 启动时间 | ~0.5s | ~0.4s | -20% |
| 内存占用 | ~30MB | ~28MB | -7% |
| CPU 占用 | 低 | 低 | 持平 |
| 刷新率 | 50ms | 50ms | 不变 |

---

## 📞 七、获取帮助

如果以上方法都无法解决问题，可以通过以下方式获取帮助：

### 5.1 查看日志
```bash
# 运行并保存日志
python3 clock.py 2>&1 | tee clawclock.log
```

### 5.2 提交 Issue
访问项目仓库，创建新 Issue 并附上：
- 问题描述
- 错误信息
- 系统环境（OS、Python 版本）
- 已尝试的解决方案

### 5.3 社区支持
- 查看已有 Issues
- 参与讨论区
- 查阅 Wiki 文档

---

*最后更新：2026-03-19*  
*ClawClock 版本：v1.6.0*
