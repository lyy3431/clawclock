# 📚 ClawClock API 参考文档

本文档提供 ClawClock v1.6.0+ 模块化架构的完整 API 参考。

---

## 📑 目录

1. [配置模块 (config)](#1-配置模块-config)
   - [ConfigManager](#configmanager)
   - [PersistenceManager](#persistencemanager)
2. [特效模块 (effects)](#2-特效模块-effects)
   - [BreathLightEffect](#breathlighteffect)
   - [Animation](#animation)
   - [FadeAnimation](#fadeanimation)
   - [ColorAnimation](#coloranimation)
3. [工具模块 (utils)](#3-工具模块-utils)
   - [错误处理](#错误处理)
   - [日志系统](#日志系统)
4. [枚举类型](#4-枚举类型)
5. [工具函数](#5-工具函数)

---

## 1. 配置模块 (config)

### ConfigManager

配置管理器，负责加载、保存和管理应用配置。

**导入：**
```python
from config.settings import get_config_manager, ConfigManager
```

#### 构造函数

```python
ConfigManager(config_file: str = CONFIG_FILE)
```

**参数：**
- `config_file` (str): 配置文件路径，默认使用全局常量

#### 方法

##### load()

加载配置文件。

**签名：**
```python
def load(self) -> Dict[str, Any]
```

**返回值：**
- `Dict[str, Any]`: 配置字典

**示例：**
```python
config_manager = ConfigManager()
config = config_manager.load()
```

##### save()

保存配置文件。

**签名：**
```python
def save(config: Optional[Dict[str, Any]] = None) -> bool
```

**参数：**
- `config` (Optional[Dict]): 配置字典，None 则保存当前配置

**返回值：**
- `bool`: 是否保存成功

**示例：**
```python
success = config_manager.save()
```

##### get()

获取配置项。

**签名：**
```python
def get(key: str, default: Any = None) -> Any
```

**参数：**
- `key` (str): 配置键，支持点号分隔的嵌套键（如 `"breath_light.frequency"`）
- `default` (Any): 默认值，键不存在时返回

**返回值：**
- `Any`: 配置值

**示例：**
```python
timezone = config_manager.get("timezone")
frequency = config_manager.get("breath_light.frequency", default=0.5)
```

##### set()

设置配置项。

**签名：**
```python
def set(key: str, value: Any) -> bool
```

**参数：**
- `key` (str): 配置键
- `value` (Any): 配置值

**返回值：**
- `bool`: 是否设置成功

**示例：**
```python
config_manager.set("theme", "dark")
config_manager.set("breath_light.enabled", True)
```

##### reset()

重置为默认配置。

**签名：**
```python
def reset(self) -> bool
```

**返回值：**
- `bool`: 是否重置成功

**示例：**
```python
config_manager.reset()
```

#### 全局函数

```python
# 获取全局配置管理器实例
config = get_config_manager()

# 重新加载配置
config = reload_config()

# 保存配置
save_config()
```

---

### PersistenceManager

持久化管理器，负责应用数据的持久化存储。

**导入：**
```python
from config.persistence import get_persistence_manager, PersistenceManager
```

#### 构造函数

```python
PersistenceManager(data_dir: str = ".")
```

**参数：**
- `data_dir` (str): 数据目录路径

#### 方法

##### load_alarms()

加载闹钟数据。

**签名：**
```python
def load_alarms(self) -> List[Dict[str, Any]]
```

**返回值：**
- `List[Dict[str, Any]]`: 闹钟列表

**示例：**
```python
persistence = get_persistence_manager()
alarms = persistence.load_alarms()
```

##### save_alarms()

保存闹钟数据。

**签名：**
```python
def save_alarms(alarms: List[Dict[str, Any]]) -> bool
```

**参数：**
- `alarms` (List[Dict]): 闹钟列表

**返回值：**
- `bool`: 是否保存成功

##### add_alarm()

添加闹钟。

**签名：**
```python
def add_alarm(
    time_str: str,
    label: str = "",
    enabled: bool = True,
    repeat_days: List[int] = None,
    sound: str = "default"
) -> bool
```

**参数：**
- `time_str` (str): 时间（HH:MM 格式）
- `label` (str): 标签
- `enabled` (bool): 是否启用
- `repeat_days` (List[int]): 重复日期（0=周一，6=周日）
- `sound` (str): 铃声

**返回值：**
- `bool`: 是否添加成功

**示例：**
```python
persistence.add_alarm("07:00", label="起床", repeat_days=[0, 1, 2, 3, 4])
```

##### remove_alarm()

删除闹钟。

**签名：**
```python
def remove_alarm(index: int) -> bool
```

**参数：**
- `index` (int): 闹钟索引

**返回值：**
- `bool`: 是否删除成功

##### toggle_alarm()

切换闹钟启停状态。

**签名：**
```python
def toggle_alarm(index: int, enabled: bool = None) -> bool
```

**参数：**
- `index` (int): 闹钟索引
- `enabled` (bool): 目标状态，None 则切换

**返回值：**
- `bool`: 是否操作成功

##### clear_alarms()

清空所有闹钟。

**签名：**
```python
def clear_alarms(self) -> bool
```

**返回值：**
- `bool`: 是否清空成功

##### load_stopwatch_state() / save_stopwatch_state()

加载/保存秒表状态。

**签名：**
```python
def load_stopwatch_state(self) -> Optional[Dict[str, Any]]
def save_stopwatch_state(self, state: Dict[str, Any]) -> bool
```

##### load_timer_state() / save_timer_state()

加载/保存倒计时状态。

**签名：**
```python
def load_timer_state(self) -> Optional[Dict[str, Any]]
def save_timer_state(self, state: Dict[str, Any]) -> bool
```

---

## 2. 特效模块 (effects)

### BreathLightEffect

呼吸灯效果类，提供呼吸灯动画效果。

**导入：**
```python
from effects.breath_light import BreathLightEffect, BreathLightConfig
```

#### 构造函数

```python
BreathLightEffect(config: Optional[BreathLightConfig] = None)
```

**参数：**
- `config` (BreathLightConfig): 配置对象，None 则使用默认配置

**示例：**
```python
effect = BreathLightEffect()

# 自定义配置
config = BreathLightConfig(frequency=0.8, style="tech")
effect = BreathLightEffect(config)
```

#### 方法

##### start()

开始呼吸灯效果。

**签名：**
```python
def start(self, root, callback: Callable[[str], None]) -> None
```

**参数：**
- `root`: Tkinter 根窗口
- `callback`: 颜色更新回调函数

##### stop()

停止呼吸灯效果。

**签名：**
```python
def stop(self, root) -> None
```

**参数：**
- `root`: Tkinter 根窗口

##### set_status()

设置倒计时状态。

**签名：**
```python
def set_status(self, status: TimerStatus) -> None
```

**参数：**
- `status` (TimerStatus): 状态枚举

**示例：**
```python
effect.set_status(TimerStatus.NORMAL)
effect.set_status(TimerStatus.WARNING)
effect.set_status(TimerStatus.COMPLETED)
```

##### get_current_color()

获取当前颜色。

**签名：**
```python
def get_current_color(self) -> str
```

**返回值：**
- `str`: 十六进制颜色值（如 `"#00d4aa"`）

##### update()

更新呼吸灯效果。

**签名：**
```python
def update(self, elapsed_time: float) -> str
```

**参数：**
- `elapsed_time` (float): 经过的时间（秒）

**返回值：**
- `str`: 当前颜色

**示例：**
```python
color = effect.update(0.5)  # 更新 0.5 秒后的颜色
```

##### set_style()

设置呼吸灯风格。

**签名：**
```python
def set_style(self, style: BreathStyle) -> None
```

**参数：**
- `style` (BreathStyle): 风格枚举

**示例：**
```python
effect.set_style(BreathStyle.SOFT)
effect.set_style(BreathStyle.TECH)
effect.set_style(BreathStyle.COOL)
effect.set_style(BreathStyle.MINIMAL)
```

---

### Animation

基础动画类，提供通用动画功能。

**导入：**
```python
from effects.animations import Animation
```

#### 构造函数

```python
Animation(
    duration: float = 1.0,
    easing: str = "linear",
    on_complete: Optional[Callable[[], None]] = None
)
```

**参数：**
- `duration` (float): 动画持续时间（秒）
- `easing` (str): 缓动函数名称（linear/ease_in/ease_out/ease_in_out/bounce/elastic）
- `on_complete` (Callable): 完成回调

#### 方法

##### start()

开始动画。

```python
def start(self) -> None
```

##### stop()

停止动画。

```python
def stop(self) -> None
```

##### reset()

重置动画。

```python
def reset(self) -> None
```

##### update()

更新动画。

**签名：**
```python
def update(self, dt: float) -> float
```

**参数：**
- `dt` (float): 时间增量（秒）

**返回值：**
- `float`: 当前动画值（0-1）

**示例：**
```python
anim = Animation(duration=1.0, easing="ease_in_out")
anim.start()

# 在更新循环中
while anim._running:
    value = anim.update(0.016)  # 60 FPS
    print(f"动画进度：{value:.2f}")
```

---

### FadeAnimation

淡入淡出动画。

**导入：**
```python
from effects.animations import FadeAnimation
```

#### 构造函数

```python
FadeAnimation(
    start: float = 0.0,
    end: float = 1.0,
    duration: float = 1.0,
    easing: str = "ease_out"
)
```

**参数：**
- `start` (float): 起始透明度
- `end` (float): 结束透明度
- `duration` (float): 持续时间（秒）
- `easing` (str): 缓动函数

#### 方法

##### update()

更新动画。

**签名：**
```python
def update(self, dt: float) -> float
```

**返回值：**
- `float`: 当前透明度

**示例：**
```python
fade = FadeAnimation(start=0.0, end=1.0, duration=0.5)
fade.start()

alpha = fade.update(0.016)  # 获取当前透明度
```

---

### ColorAnimation

颜色渐变动画。

**导入：**
```python
from effects.animations import ColorAnimation
```

#### 构造函数

```python
ColorAnimation(
    start_color: str,
    end_color: str,
    duration: float = 1.0,
    easing: str = "linear"
)
```

**参数：**
- `start_color` (str): 起始颜色（十六进制）
- `end_color` (str): 结束颜色（十六进制）
- `duration` (float): 持续时间（秒）
- `easing` (str): 缓动函数

#### 方法

##### update()

更新动画。

**签名：**
```python
def update(self, dt: float) -> str
```

**返回值：**
- `str`: 当前颜色（十六进制）

**示例：**
```python
color_anim = ColorAnimation("#00ff88", "#ff0000", duration=1.0)
color_anim.start()

current_color = color_anim.update(0.016)  # 获取当前颜色
```

---

## 3. 工具模块 (utils)

### 错误处理

**导入：**
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
```

### 异常类

#### ClockError

基础异常类。

```python
class ClockError(Exception):
    pass
```

#### ConfigError

配置错误。

```python
class ConfigError(ClockError):
    def __init__(self, message: str, config_key: Optional[str] = None)
```

**参数：**
- `message` (str): 错误消息
- `config_key` (str): 配置键

#### ThemeError

主题错误。

```python
class ThemeError(ClockError):
    def __init__(self, message: str, theme_name: Optional[str] = None)
```

#### AlarmError

闹钟错误。

```python
class AlarmError(ClockError):
    def __init__(self, message: str, alarm_time: Optional[str] = None)
```

#### TimerError

倒计时错误。

```python
class TimerError(ClockError):
    def __init__(self, message: str, preset_name: Optional[str] = None)
```

#### IOError

IO 错误。

```python
class IOError(ClockError):
    def __init__(self, message: str, file_path: Optional[str] = None)
```

### 验证函数

#### validate_time_format()

验证时间格式。

**签名：**
```python
def validate_time_format(time_str: str) -> bool
```

**参数：**
- `time_str` (str): 时间字符串（HH:MM 或 HH:MM:SS）

**返回值：**
- `bool`: 是否有效

**示例：**
```python
validate_time_format("23:59")  # True
validate_time_format("25:00")  # False
```

#### validate_preset_time()

验证预设时间。

**签名：**
```python
def validate_preset_time(hours: int, minutes: int, seconds: int) -> None
```

**参数：**
- `hours` (int): 小时（0-99）
- `minutes` (int): 分钟（0-59）
- `seconds` (int): 秒（0-59）

**异常：**
- `TimerError`: 时间超出范围

**示例：**
```python
try:
    validate_preset_time(1, 30, 0)  # ✅
    validate_preset_time(100, 0, 0)  # ❌ 抛出 TimerError
except TimerError as e:
    print(f"错误：{e}")
```

### 工具函数

#### safe_execute()

安全执行函数。

**签名：**
```python
def safe_execute(
    func,
    *args,
    default=None,
    error_handler=None
)
```

**参数：**
- `func`: 待执行的函数
- `*args`: 函数参数
- `default`: 出错时的默认返回值
- `error_handler`: 错误处理函数

**返回值：**
- 函数返回值或默认值

**示例：**
```python
result = safe_execute(
    lambda: 10 / 0,
    default=0,
    error_handler=lambda e: print(f"错误：{e}")
)
```

### ErrorLogger

错误日志记录器。

```python
class ErrorLogger:
    def log(self, error: Exception, context: Optional[dict] = None) -> None
    def get_error_report(self) -> str
    def clear(self) -> None
```

**示例：**
```python
logger = ErrorLogger()
try:
    risky_operation()
except Exception as e:
    logger.log(e, context={"module": "clock", "action": "init"})
    print(logger.get_error_report())
```

---

### 日志系统

**导入：**
```python
from utils.logger import (
    ClockLogger,
    get_logger,
    debug,
    info,
    warning,
    error,
    critical,
    set_context
)
```

### ClockLogger

日志记录器类。

**导入：**
```python
from utils.logger import ClockLogger
```

#### 构造函数

```python
ClockLogger(name: str = "clawclock", level: int = logging.INFO)
```

**参数：**
- `name` (str): 日志名称
- `level` (int): 日志级别

#### 方法

##### set_context()

设置上下文。

```python
def set_context(self, **kwargs) -> None
```

##### clear_context()

清空上下文。

```python
def clear_context(self) -> None
```

##### debug() / info() / warning() / error() / critical()

各级别日志记录。

```python
def debug(self, message: str, **kwargs) -> None
def info(self, message: str, **kwargs) -> None
def warning(self, message: str, **kwargs) -> None
def error(self, message: str, **kwargs) -> None
def critical(self, message: str, **kwargs) -> None
```

**示例：**
```python
logger = ClockLogger("my_module")
logger.info("应用启动")
logger.error("配置加载失败")

# 带上下文
logger.set_context(module="clock", func="init")
logger.debug("初始化完成")
```

### 全局函数

```python
# 获取全局日志记录器
logger = get_logger()

# 快速日志记录
info("应用启动")
warning("配置不存在")
error("文件读取失败")

# 设置上下文
set_context(module="clock", func="init")
info("带上下文的日志")
```

---

## 4. 枚举类型

### BreathStyle

呼吸灯风格枚举。

```python
class BreathStyle(Enum):
    SOFT = "soft"        # 柔和模式
    TECH = "tech"        # 科技模式
    COOL = "cool"        # 炫酷模式
    MINIMAL = "minimal"  # 简约模式
```

### BreathMode

呼吸灯显示模式枚举。

```python
class BreathMode(Enum):
    DIGITAL = "digital"       # 数字显示
    BACKGROUND = "background" # 背景
    BORDER = "border"         # 边框
    ALL = "all"              # 全部
```

### TimerStatus

倒计时状态枚举。

```python
class TimerStatus(Enum):
    NORMAL = "normal"       # 正常（绿色）
    WARNING = "warning"     # 警告（橙色）
    COMPLETED = "completed" # 完成（红色）
```

---

## 5. 工具函数

### 颜色转换

#### hex_to_rgb()

十六进制颜色转 RGB。

**签名：**
```python
def hex_to_rgb(hex_color: str) -> tuple
```

**参数：**
- `hex_color` (str): 十六进制颜色（如 `"#00ff88"`）

**返回值：**
- `tuple`: RGB 元组 `(r, g, b)`

**示例：**
```python
rgb = hex_to_rgb("#00ff88")  # (0, 255, 136)
```

#### rgb_to_hex()

RGB 转十六进制颜色。

**签名：**
```python
def rgb_to_hex(r: int, g: int, b: int) -> str
```

**参数：**
- `r, g, b` (int): RGB 值（0-255）

**返回值：**
- `str`: 十六进制颜色

**示例：**
```python
hex_color = rgb_to_hex(0, 255, 136)  # "#00ff88"
```

#### interpolate_color()

颜色插值。

**签名：**
```python
def interpolate_color(color1: str, color2: str, factor: float) -> str
```

**参数：**
- `color1` (str): 起始颜色
- `color2` (str): 结束颜色
- `factor` (float): 插值因子（0-1）

**返回值：**
- `str`: 插值颜色

**示例：**
```python
mixed = interpolate_color("#00ff88", "#ff0000", 0.5)  # 中间色
```

### 缓动函数

#### ease_in_out_sine()

正弦缓动函数。

**签名：**
```python
def ease_in_out_sine(x: float) -> float
```

**参数：**
- `x` (float): 输入值（0-1）

**返回值：**
- `float`: 输出值（0-1）

---

## 📝 完整示例

### 配置管理示例

```python
from config.settings import get_config_manager

# 获取配置管理器
config = get_config_manager()

# 读取配置
timezone = config.get("timezone")
theme = config.get("theme")
breath_enabled = config.get("breath_light.enabled")

# 修改配置
config.set("theme", "dark")
config.set("breath_light.frequency", 0.8)

# 保存配置
config.save()

# 重置配置
config.reset()
```

### 呼吸灯效果示例

```python
from effects.breath_light import (
    BreathLightEffect,
    BreathStyle,
    TimerStatus
)

# 创建效果实例
effect = BreathLightEffect()

# 设置风格
effect.set_style(BreathStyle.SOFT)

# 设置状态
effect.set_status(TimerStatus.NORMAL)

# 更新效果
for i in range(100):
    color = effect.update(0.016)  # 60 FPS
    print(f"帧 {i}: {color}")
    
    # 状态切换
    if i == 50:
        effect.set_status(TimerStatus.WARNING)
    elif i == 80:
        effect.set_status(TimerStatus.COMPLETED)
```

### 动画系统示例

```python
from effects.animations import (
    Animation,
    FadeAnimation,
    ColorAnimation
)

# 基础动画
anim = Animation(duration=1.0, easing="ease_in_out")
anim.start()

while anim._running:
    value = anim.update(0.016)
    print(f"进度：{value:.2f}")

# 淡入淡出
fade = FadeAnimation(start=0.0, end=1.0, duration=0.5)
fade.start()

alpha = fade.update(0.016)

# 颜色渐变
color_anim = ColorAnimation("#00ff88", "#ff0000", duration=1.0)
color_anim.start()

current_color = color_anim.update(0.016)
```

### 错误处理示例

```python
from utils.errors import (
    TimerError,
    validate_time_format,
    validate_preset_time,
    safe_execute
)

# 时间格式验证
try:
    validate_time_format("23:59")
except TimerError as e:
    print(f"错误：{e}")

# 预设时间验证
try:
    validate_preset_time(1, 30, 0)
except TimerError as e:
    print(f"错误：{e}")

# 安全执行
result = safe_execute(
    lambda: 10 / 0,
    default=0,
    error_handler=lambda e: print(f"捕获错误：{e}")
)
```

### 日志系统示例

```python
from utils.logger import (
    info,
    warning,
    error,
    set_context,
    ClockLogger
)

# 快速日志
info("应用启动")
warning("配置不存在")
error("文件读取失败")

# 带上下文
set_context(module="clock", func="init")
info("初始化完成")

# 自定义日志记录器
logger = ClockLogger("my_module")
logger.info("自定义日志")
logger.error("自定义错误")
```

---

*API 版本：v1.6.0*  
*最后更新：2026-03-19*
