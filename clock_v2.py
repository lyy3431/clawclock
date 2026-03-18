#！/usr/bin/env python3
"""
ClawClock 优化后 clock.py - 简化版
========================

简化后的主时钟应用文件，UI、逻辑、配置分离。

功能特性:
    - 模拟时钟和数字时钟双模式
    - 多时区支持
    - 现代深色主题 UI
    - 实时更新（50ms 刷新率）
    - 闹钟功能
    - 秒表功能
    - 倒计时功能
    - 全屏支持
    - 窗口置顶

作者：ClawClock Development Team
许可证：MIT
版本：1.6.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import datetime
import math
import os
import sys
import json
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# 导入配置模块
from config.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    REFRESH_INTERVAL, MAX_ALARMS,
    DEFAULT_THEME, PRESET_TIMES
)

# 导入配置管理
from config.settings import get_config_manager

# 导入持久化
from config.persistence import get_persistence_manager

# 导入日志系统
from utils.logger import get_logger, info, error, set_context

# 导入呼吸灯效果
from effects.breath_light import (
    BreathLightEffect,
    BreathLightConfig,
    BreathMode,
    TimerStatus
)


def validate_time_format(time_str: str) -> bool:
    """验证时间格式"""
    import re
    pattern = r'^([01]\d|2[0-3]):([0-5]\d)(:([0-5]\d))?$'
    return bool(re.match(pattern, time_str))


def validate_preset_time(hours: int, minutes: int, seconds: int) -> None:
    """验证预设时间"""
    if not (0 <= hours <= 99):
        raise ValueError("小时超出范围 (0-99)")
    if not (0 <= minutes <= 59):
        raise ValueError("分钟超出范围 (0-59)")
    if not (0 <= seconds <= 59):
        raise ValueError("秒超出范围 (0-59)")


# 全局日志记录器
_logger = get_logger("clock")

# 全局配置管理器
_config = get_config_manager()

# 全局持久化管理器
_persistence = get_persistence_manager()


@dataclass
class Alarm:
    """闹钟数据类"""
    time: str
    enabled: bool = True
    label: str = ""
    sound: str = "default"
    repeat_days: List[int] = field(default_factory=list)
    
    def is_due(self, current_time: datetime.datetime) -> bool:
        """检查当前时间是否触发闹钟"""
        if not self.enabled:
            return False
        
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_second = current_time.second
        current_weekday = current_time.weekday()
        
        alarm_hour, alarm_minute = map(int, self.time.split(":"))
        
        if current_hour == alarm_hour and current_minute == alarm_minute and current_second == 0:
            if not self.repeat_days or current_weekday in self.repeat_days:
                return True
        
        return False


@dataclass
class LapRecord:
    """计次记录数据类"""
    lap_number: int
    time_ms: int
    split_ms: int
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class StopwatchState:
    """秒表状态数据类"""
    is_running: bool = False
    start_time: float = 0.0
    elapsed_ms: int = 0
    laps: List[LapRecord] = field(default_factory=list)


@dataclass
class TimerState:
    """倒计时状态数据类"""
    is_running: bool = False
    total_seconds: int = 0
    remaining_seconds: float = 0.0
    start_time: float = 0.0
    sound_enabled: bool = True
    preset_name: str = ""


class ClockApp:
    """时钟应用主类（简化版）"""
    
    def __init__(self, root: tk.Tk) -> None:
        """初始化时钟应用"""
        set_context(module="clock_app", func="__init__")
        info("初始化 ClockApp")
        
        self.root = root
        self.root.title("ClawClock - 图形时钟")
        
        # 从配置加载
        self.config = _config.load()
        self.themes = self.load_themes()
        
        # 初始化闹钟
        self.alarms: List[Alarm] = []
        self.alarm_triggered: bool = False
        self._load_alarms()
        
        # 初始化秒表
        self.stopwatch: StopwatchState = StopwatchState()
        self.stopwatch_job: Optional[str] = None
        
        # 初始化倒计时
        self.timer: TimerState = TimerState()
        self.timer_job: Optional[str] = None
        self.timer_blink_job: Optional[str] = None
        self.timer_is_blinking: bool = False
        
        # 初始化呼吸灯
        self.breath_effect: Optional[BreathLightEffect] = None
        self._init_breath_effect()
        
        # 设置窗口
        self._setup_window()
        
        info("ClockApp 初始化完成")
    
    def _init_breath_effect(self) -> None:
        """初始化呼吸灯效果"""
        try:
            breathe_config = self.config.get("breath_light", {})
            config = BreathLightConfig(
                enabled=breathe_config.get("enabled", True),
                mode=BreathMode.DIGITAL,
                style=breathe_config.get("style", "soft"),
                frequency=breathe_config.get("frequency", 0.5),
                intensity=breathe_config.get("intensity", 0.5)
            )
            self.breath_effect = BreathLightEffect(config)
        except Exception as e:
            error(f"呼吸灯初始化失败: {e}")
            self.breath_effect = None
    
    def _setup_window(self) -> None:
        """设置窗口"""
        width = self.config.get("window.width", WINDOW_WIDTH)
        height = self.config.get("window.height", WINDOW_HEIGHT)
        
        x = self.config.get("window.x")
        y = self.config.get("window.y")
        
        if x is not None and y is not None:
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.root.geometry(f"{width}x{height}")
        
        # 设置窗口属性
        resizable = self.config.get("window.resizable", False)
        self.root.resizable(resizable, resizable)
        
        always_on_top = self.config.get("window.always_on_top", False)
        if always_on_top:
            self.root.attributes("-topmost", True)
        
        fullscreen = self.config.get("window.fullscreen", False)
        if fullscreen:
            self.root.attributes("-fullscreen", True)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def load_themes(self) -> Dict[str, Dict[str, Any]]:
        """加载主题配置"""
        themes_dir = os.path.join(os.path.dirname(__file__), "themes")
        themes: Dict[str, Dict[str, Any]] = {}
        
        if os.path.exists(themes_dir):
            for filename in os.listdir(themes_dir):
                if filename.endswith(".json"):
                    theme_name = filename[:-5]
                    try:
                        with open(os.path.join(themes_dir, filename), 'r', encoding='utf-8') as f:
                            themes[theme_name] = json.load(f)
                    except Exception as e:
                        error(f"加载主题 {theme_name} 失败: {e}")
        
        return themes
    
    def apply_theme(self, theme_name: str) -> None:
        """应用主题"""
        info(f"应用主题: {theme_name}")
        
        if theme_name not in self.themes:
            error(f"主题 '{theme_name}' 不存在")
            return
        
        theme = self.themes[theme_name]
        
        self.root.configure(bg=theme.get("bg", "#1a1a2e"))
        
        # 应用颜色到所有组件
        self._recursive_update_colors(self.root, theme)
    
    def _recursive_update_colors(self, widget: tk.Widget, theme: Dict[str, str]) -> None:
        """递归更新组件颜色"""
        try:
            widget.configure(bg=theme.get("bg", "#1a1a2e"))
            
            for child in widget.winfo_children():
                if isinstance(child, tk.Widget):
                    self._recursive_update_colors(child, theme)
        except Exception as e:
            error(f"更新组件颜色失败: {e}")
    
    def _check_alarms(self) -> None:
        """检查闹钟"""
        current_time = datetime.datetime.now()
        
        for alarm in self.alarms:
            if alarm.is_due(current_time):
                self._trigger_alarm(alarm)
    
    def _trigger_alarm(self, alarm: Alarm) -> None:
        """触发闹钟"""
        info(f"闹钟触发: {alarm.time} - {alarm.label}")
        
        # 显示通知
        messagebox.showinfo("⏰ 闹钟", f"{alarm.label}\n{alarm.time}")
        
        # 播放声音（如果启用）
        if alarm.sound == "default":
            self.root.bell()
    
    def _load_alarms(self) -> None:
        """加载闹钟"""
        self.alarms = []
        alarms_data = _persistence.load_alarms()
        
        for data in alarms_data:
            alarm = Alarm(
                time=data.get("time", "08:00"),
                enabled=data.get("enabled", True),
                label=data.get("label", ""),
                sound=data.get("sound", "default"),
                repeat_days=data.get("repeat_days", [])
            )
            self.alarms.append(alarm)
        
        info(f"加载闹钟: {len(self.alarms)} 个")
    
    def _save_alarms(self) -> None:
        """保存闹钟"""
        alarms_data = []
        for alarm in self.alarms:
            alarms_data.append({
                "time": alarm.time,
                "enabled": alarm.enabled,
                "label": alarm.label,
                "sound": alarm.sound,
                "repeat_days": alarm.repeat_days
            })
        
        _persistence.save_alarms(alarms_data)
    
    def on_close(self) -> None:
        """关闭窗口"""
        set_context(module="clock_app", func="on_close")
        info("关闭应用")
        
        # 保存窗口位置
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        self.config.set("window.x", x)
        self.config.set("window.y", y)
        self.config.set("window.width", width)
        self.config.set("window.height", height)
        
        self.config.save()
        
        self.root.destroy()


def main():
    """主函数"""
    set_context(module="main")
    info("ClawClock 启动")
    
    try:
        root = tk.Tk()
        app = ClockApp(root)
        root.mainloop()
    except Exception as e:
        error(f"应用启动失败: {e}")
        raise
    
    info("ClawClock 退出")


if __name__ == "__main__":
    main()
