# ClawClock 常量配置
"""
统一管理项目中的常量，避免硬编码
"""

# 窗口配置
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
WINDOW_MIN_WIDTH = 400
WINDOW_MIN_HEIGHT = 350

# 时间配置
REFRESH_INTERVAL = 50  # 毫秒
SECONDARY_REFRESH_INTERVAL = 100  # 毫秒

# 闹钟配置
MAX_ALARMS = 10
DEFAULT_ALARM_LABEL = "闹钟"
SNOOZE_DURATION = 5 * 60  # 5分钟

# 秒表配置
MAX_LAPS = 100
LAP_FORMAT = "计圈 #{:d}: {:s}"

# 倒计时配置
MAX_DURATION_HOURS = 99
MAX_DURATION_MINUTES = 59
MAX_DURATION_SECONDS = 59

# 主题配置
DEFAULT_THEME = "dark"
THEME_TYPES = ["dark", "light", "green", "cyberpunk"]

# 呼吸灯配置
BREATH_DEFAULT_ENABLED = True
BREATH_DEFAULT_MODE = "digital"
BREATH_DEFAULT_STYLE = "soft"
BREATH_DEFAULT_FREQUENCY = 0.5  # Hz
BREATH_DEFAULT_INTENSITY = 0.5
BREATH_DEFAULT_ACCELERATE = True
BREATH_DEFAULT_SMOOTH = True

# 颜色配置
DEFAULT_COLORS = {
    "dark": {
        "bg": "#1a1a2e",
        "face": "#16213e",
        "hand": "#e94560",
        "text": "#ffffff"
    },
    "light": {
        "bg": "#f5f5f5",
        "face": "#ffffff",
        "hand": "#333333",
        "text": "#000000"
    },
    "green": {
        "bg": "#0f380f",
        "face": "#1a5c1a",
        "hand": "#4caf50",
        "text": "#ffffff"
    },
    "cyberpunk": {
        "bg": "#0a0a1a",
        "face": "#1a1a3a",
        "hand": "#ff00ff",
        "text": "#00ffff"
    }
}

# 时区配置
TIMEZONE_LIST = [
    "UTC-12", "UTC-11", "UTC-10", "UTC-9", "UTC-8",
    "UTC-7", "UTC-6", "UTC-5", "UTC-4", "UTC-3",
    "UTC-2", "UTC-1", "UTC+0", "UTC+1", "UTC+2",
    "UTC+3", "UTC+4", "UTC+5", "UTC+6", "UTC+7",
    "UTC+8", "UTC+9", "UTC+10", "UTC+11", "UTC+12"
]

# 预设时间
PRESET_TIMES = {
    "番茄钟": 25 * 60,      # 25分钟
    "短休息": 5 * 60,       # 5分钟
    "长休息": 15 * 60,      # 15分钟
    "90分钟": 90 * 60,      # 90分钟
    "2小时": 2 * 60 * 60    # 2小时
}

# 文件路径
CONFIG_FILE = "config.json"
ALARMS_FILE = "alarms.json"
THEMES_DIR = "themes"
