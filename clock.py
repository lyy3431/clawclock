#!/usr/bin/env python3
"""
ClawClock - 图形化时钟应用
========================

一个支持模拟和数字时间显示的 Linux 桌面时钟应用。

功能特性:
    - 模拟时钟和数字时钟双模式
    - 多时区支持
    - 现代深色主题 UI
    - 实时更新（50ms 刷新率）
    - 闹钟功能
    - 秒表功能
    - 倒计时功能（番茄钟、休息时间）
    - 全屏支持
    - 窗口置顶

使用方法:
    python3 clock.py

依赖:
    - Python 3.8+
    - tkinter

作者：ClawClock Development Team
许可证：MIT
版本：1.6.1
"""

# ==================== 版本常量 ====================
__version__ = "1.6.4"
__version_info__ = (1, 6, 1)  # (major, minor, patch)

import tkinter as tk
from tkinter import ttk, messagebox
import time
import datetime
import math
import os
import sys
import json
import threading
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class Alarm:
    """闹钟数据类
    
    Attributes:
        time: 闹钟时间 (HH:MM 格式)
        enabled: 是否启用
        label: 闹钟标签
        sound: 铃声类型
        repeat_days: 重复日期列表 (0=Monday, 6=Sunday)
        snooze_minutes: 小睡时长 (分钟)
    """
    time: str  # HH:MM 格式
    enabled: bool = True
    label: str = ""
    sound: str = "default"
    repeat_days: List[int] = field(default_factory=list)  # 0=Monday, 6=Sunday
    snooze_minutes: int = 5  # 小睡时长
    
    def is_due(self, current_time: datetime.datetime) -> bool:
        """
        检查当前时间是否触发闹钟
        
        Args:
            current_time: 当前时间
            
        Returns:
            bool: 是否触发闹钟
        """
        if not self.enabled:
            return False
        
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_second = current_time.second
        current_weekday = current_time.weekday()
        
        alarm_hour, alarm_minute = map(int, self.time.split(":"))
        
        # 检查时间匹配（在秒数为 0 时触发）
        if current_hour == alarm_hour and current_minute == alarm_minute and current_second == 0:
            # 检查重复设置
            if not self.repeat_days or current_weekday in self.repeat_days:
                return True
        
        return False


@dataclass
class LapRecord:
    """计次记录数据类"""
    lap_number: int
    time_ms: int  # 累计时间 (毫秒)
    split_ms: int  # 单圈时间 (毫秒)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class StopwatchState:
    """秒表状态数据类"""
    is_running: bool = False
    start_time: float = 0.0  # time.time() 时间戳
    elapsed_ms: int = 0  # 累计经过的时间 (毫秒)
    laps: List[LapRecord] = field(default_factory=list)


@dataclass
class TimerState:
    """倒计时状态数据类"""
    is_running: bool = False
    total_seconds: int = 0  # 总时长（秒）
    remaining_seconds: float = 0.0  # 剩余时间（秒）
    start_time: float = 0.0  # 开始时间戳
    sound_enabled: bool = True
    preset_name: str = ""


class ClockApp:
    """
    时钟应用主类
    
    Attributes:
        root: Tkinter 主窗口
        timezone: 当前时区设置
        bg_color: 背景颜色
        face_color: 表盘颜色
        hand_color: 指针颜色
        text_color: 文字颜色
        alarms: 闹钟列表
    """
    
    def __init__(self, root: tk.Tk) -> None:
        """初始化时钟应用"""
        self.root = root
        self.root.title(f"ClawClock v{__version__} - 图形时钟")
        
        # 加载配置文件
        self.config: Dict[str, Any] = self.load_config()
        
        # 加载主题
        self.themes: Dict[str, Dict[str, Any]] = self.load_themes()
        
        # 初始化闹钟列表
        self.alarms: List[Alarm] = []
        self.alarm_triggered: bool = False
        self._load_alarms()
        
        # 初始化秒表状态
        self.stopwatch: StopwatchState = StopwatchState()
        self.stopwatch_job: Optional[str] = None  # 用于取消定时器
        
        # 初始化倒计时状态
        self.timer: TimerState = TimerState()
        self.timer_job: Optional[str] = None  # 用于取消定时器
        self.timer_blink_job: Optional[str] = None  # 闪烁提醒
        self.timer_is_blinking: bool = False
        
        # 应用窗口配置
        window_config: Dict[str, Any] = self.config.get("window", {})
        width: int = window_config.get("width", 600)
        height: int = window_config.get("height", 500)
        # 确保 resizable 是布尔值（兼容旧配置）
        resizable_raw: Any = window_config.get("resizable", True)
        resizable: bool = bool(resizable_raw) if not isinstance(resizable_raw, bool) else resizable_raw
        x: Optional[int] = self.config.get("window", {}).get("x", None)
        y: Optional[int] = self.config.get("window", {}).get("y", None)
        always_on_top: bool = self.config.get("window", {}).get("always_on_top", False)
        fullscreen: bool = self.config.get("window", {}).get("fullscreen", False)
        
        # 设置窗口几何信息（包括位置，如果有）
        if x is not None and y is not None:
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.root.geometry(f"{width}x{height}")
        
        # 设置窗口是否可调整大小（Tkinter 需要两个参数：width, height）
        self.root.resizable(resizable, resizable)
        
        # 窗口置顶
        if always_on_top:
            self.root.attributes("-topmost", True)
        
        # 全屏模式
        if fullscreen:
            self.root.attributes("-fullscreen", True)
        
        # 注册窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconname("ClawClock")
        except Exception:
            pass
        
        # 默认时区（从配置加载）
        self.timezone: str = self.config.get("timezone", "Asia/Shanghai")
        
        # 时区配置：东西各 12 时区，每区指定代表城市
        self.timezones: List[Tuple[str, str, str]] = [
            # 西区 (UTC-12 到 UTC-1)
            ("UTC-12", "Pacific/Kwajalein", "国际日期变更线西"),
            ("UTC-11", "Pacific/Pago_Pago", "帕果帕果"),
            ("UTC-10", "Pacific/Honolulu", "檀香山"),
            ("UTC-9", "America/Anchorage", "安克雷奇"),
            ("UTC-8", "America/Los_Angeles", "洛杉矶"),
            ("UTC-7", "America/Denver", "丹佛"),
            ("UTC-6", "America/Chicago", "芝加哥"),
            ("UTC-5", "America/New_York", "纽约"),
            ("UTC-4", "America/Halifax", "哈利法克斯"),
            ("UTC-3", "America/Sao_Paulo", "圣保罗"),
            ("UTC-2", "Atlantic/South_Georgia", "南乔治亚"),
            ("UTC-1", "Atlantic/Azores", "亚速尔群岛"),
            # 零时区
            ("UTC+0", "UTC", "协调世界时"),
            # 东区 (UTC+1 到 UTC+12)
            ("UTC+1", "Europe/London", "伦敦"),
            ("UTC+2", "Europe/Paris", "巴黎"),
            ("UTC+3", "Europe/Moscow", "莫斯科"),
            ("UTC+4", "Asia/Dubai", "迪拜"),
            ("UTC+5", "Asia/Karachi", "卡拉奇"),
            ("UTC+6", "Asia/Dhaka", "达卡"),
            ("UTC+7", "Asia/Bangkok", "曼谷"),
            ("UTC+8", "Asia/Shanghai", "上海"),
            ("UTC+9", "Asia/Tokyo", "东京"),
            ("UTC+10", "Australia/Sydney", "悉尼"),
            ("UTC+11", "Pacific/Noumea", "努美阿"),
            ("UTC+12", "Pacific/Auckland", "奥克兰"),
        ]
        
        # 从配置加载主题名
        theme_name: str = self.config.get("theme", {}).get("name", "dark")
        
        # 显示模式（从配置加载）
        self.display_mode: str = self.config.get("display_mode", "digital")  # 默认数字钟模式
        
        # 应用主题（会设置所有颜色）
        self.apply_theme(theme_name)
        
        # Setup UI
        self.setup_ui()
        
        # 加载倒计时配置
        self.load_timer_config()
        
        # Start clock update
        self.update_clock()
        
        # 启动闹钟检查线程
        self._check_alarms()
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            dict: 配置字典，如果配置文件不存在则返回默认配置
        """
        config_file: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        default_config: Dict[str, Any] = {
            "timezone": "Asia/Shanghai",
            "display_mode": "digital",  # 默认数字钟模式
            "window": {
                "width": 600,
                "height": 500,
                "resizable": True,  # 默认允许调整窗口大小
                "always_on_top": False,
                "fullscreen": False
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
            },
            "alarms": [],
            "stopwatch": {
                "laps": []
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config: Dict[str, Any] = json.load(f)
                # 合并配置，确保所有键都存在
                return self.merge_config(default_config, config)
            else:
                # 配置文件不存在，创建默认配置
                self.save_config(default_config, config_file)
                return default_config
        except Exception as e:
            print(f"⚠️  加载配置文件失败：{e}")
            print("   使用默认配置")
            return default_config
    
    def merge_config(self, default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并配置字典"""
        result: Dict[str, Any] = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config: Optional[Dict[str, Any]] = None, config_file: Optional[str] = None) -> bool:
        """
        保存配置文件
        
        Args:
            config: 配置字典，默认为 self.config
            config_file: 配置文件路径，默认为 config.json
        
        Returns:
            bool: 保存是否成功
        """
        if config is None:
            config = self.config
        if config_file is None:
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        
        try:
            # 对配置进行排序，保持美观
            sorted_config: Dict[str, Any] = self.sort_config(config)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(sorted_config, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已保存：{config_file}")
            return True
        except Exception as e:
            print(f"⚠️  保存配置文件失败：{e}")
            return False
    
    def sort_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        递归排序配置字典，保持键的顺序一致
        
        Args:
            config: 配置字典
        
        Returns:
            dict: 排序后的配置字典
        """
        sorted_config: Dict[str, Any] = {}
        for key in sorted(config.keys()):
            value = config[key]
            if isinstance(value, dict):
                sorted_config[key] = self.sort_config(value)
            else:
                sorted_config[key] = value
        return sorted_config
    
    def _load_alarms(self) -> None:
        """从配置加载闹钟"""
        alarms_data = self.config.get("alarms", [])
        self.alarms = []
        for alarm_data in alarms_data:
            alarm = Alarm(
                time=alarm_data.get("time", "00:00"),
                enabled=alarm_data.get("enabled", True),
                label=alarm_data.get("label", ""),
                sound=alarm_data.get("sound", "default"),
                repeat_days=alarm_data.get("repeat_days", []),
                snooze_minutes=alarm_data.get("snooze_minutes", 5)
            )
            self.alarms.append(alarm)
    
    def _save_alarms(self) -> None:
        """保存闹钟到配置"""
        self.config["alarms"] = [
            {
                "time": alarm.time,
                "enabled": alarm.enabled,
                "label": alarm.label,
                "sound": alarm.sound,
                "repeat_days": alarm.repeat_days,
                "snooze_minutes": alarm.snooze_minutes
            }
            for alarm in self.alarms
        ]
        self.save_config()
    
    def _check_alarms(self) -> None:
        """定期检查闹钟（每秒）"""
        def check_loop():
            while True:
                time.sleep(1)
                if not self.alarm_triggered:
                    now = datetime.datetime.now()
                    for alarm in self.alarms:
                        if alarm.is_due(now):
                            self.alarm_triggered = True
                            # 在主线程中触发闹钟
                            self.root.after(0, self._trigger_alarm, alarm)
                            break
        
        # 在后台线程运行
        thread = threading.Thread(target=check_loop, daemon=True)
        thread.start()
    
    def _trigger_alarm(self, alarm: Alarm) -> None:
        """
        触发闹钟（渐入铃声）
        
        Args:
            alarm: 触发的闹钟对象
        """
        label_text = f"闹钟时间到！\n\n{alarm.time}"
        if alarm.label:
            label_text += f"\n{alarm.label}"
        
        # 显示闹钟对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("⏰ 闹钟")
        dialog.geometry("300x200")
        dialog.attributes("-topmost", True)
        
        # 居中显示
        dialog_x = int(self.root.winfo_x() + self.root.winfo_width() / 2 - 150)
        dialog_y = int(self.root.winfo_y() + self.root.winfo_height() / 2 - 100)
        dialog.geometry(f"300x200+{dialog_x}+{dialog_y}")
        
        label = tk.Label(dialog, text=label_text, font=("Arial", 16), pady=20)
        label.pack()
        
        def stop_alarm():
            self.alarm_triggered = False
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="停止闹钟", command=stop_alarm, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="稍后提醒", command=lambda: self._snooze_alarm(dialog, alarm), width=10).pack(side=tk.LEFT, padx=10)
        
        # 渐入铃声：蜂鸣 3 次，每次间隔 1 秒
        for i in range(3):
            try:
                self.root.bell()
            except Exception:
                pass
            if i < 2:
                time.sleep(1)
        
        # 发送系统通知
        self.send_notification("⏰ 闹钟提醒", f"{alarm.time} - {alarm.label}" if alarm.label else alarm.time)
    
    def _snooze_alarm(self, dialog: tk.Toplevel, alarm: Alarm) -> None:
        """
        稍后提醒（小睡功能）
        
        Args:
            dialog: 闹钟对话框
            alarm: 当前闹钟对象
        """
        self.alarm_triggered = False
        dialog.destroy()
        
        # 使用闹钟的 snooze_minutes 设置
        def snooze_callback():
            self.alarm_triggered = True
            self.root.after(0, self._trigger_alarm, alarm)
        
        snooze_ms = alarm.snooze_minutes * 60 * 1000
        self.root.after(snooze_ms, snooze_callback)
    
    def send_notification(self, title: str, message: str) -> None:
        """
        发送系统通知（Linux notify-send）
        
        Args:
            title: 通知标题
            message: 通知内容
        """
        try:
            subprocess.run(['notify-send', title, message], timeout=2, capture_output=True)
        except Exception:
            # 降级处理：不显示通知
            pass
    
    def add_alarm(self, time_str: str, label: str = "", repeat_days: Optional[List[int]] = None, snooze_minutes: int = 5) -> bool:
        """
        添加新闹钟
        
        Args:
            time_str: 时间字符串 (HH:MM)
            label: 闹钟标签
            repeat_days: 重复日期列表 (0=Monday, 6=Sunday)
            snooze_minutes: 小睡时长 (分钟)
        
        Returns:
            bool: 是否添加成功
        """
        # 验证时间格式
        try:
            hour, minute = map(int, time_str.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("时间超出范围")
        except Exception as e:
            print(f"⚠️  无效的时间格式：{e}")
            return False
        
        alarm = Alarm(time=time_str, label=label, repeat_days=repeat_days or [], snooze_minutes=snooze_minutes)
        self.alarms.append(alarm)
        self._save_alarms()
        print(f"✅ 闹钟已添加：{time_str} {label}")
        return True
    
    def remove_alarm(self, index: int) -> bool:
        """
        删除闹钟
        
        Args:
            index: 闹钟索引
        
        Returns:
            bool: 是否删除成功
        """
        if 0 <= index < len(self.alarms):
            self.alarms.pop(index)
            self._save_alarms()
            print(f"✅ 闹钟已删除：索引 {index}")
            return True
        return False
    
    def toggle_alarm(self, index: int) -> bool:
        """
        切换闹钟启用状态
        
        Args:
            index: 闹钟索引
        
        Returns:
            bool: 是否操作成功
        """
        if 0 <= index < len(self.alarms):
            self.alarms[index].enabled = not self.alarms[index].enabled
            self._save_alarms()
            status = "启用" if self.alarms[index].enabled else "禁用"
            print(f"✅ 闹钟已{status}：索引 {index}")
            return True
        return False
    
    def load_themes(self) -> Dict[str, Dict[str, Any]]:
        """
        加载所有可用主题
        
        Returns:
            dict: 主题字典，键为文件名，值为主题数据
        """
        themes_dir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "themes")
        themes: Dict[str, Dict[str, Any]] = {}
        
        if os.path.exists(themes_dir):
            for filename in os.listdir(themes_dir):
                if filename.endswith(".json"):
                    theme_path: str = os.path.join(themes_dir, filename)
                    try:
                        with open(theme_path, "r", encoding="utf-8") as f:
                            theme_data: Dict[str, Any] = json.load(f)
                            theme_name: str = theme_data.get("name", filename.replace(".json", ""))
                            themes[theme_name] = theme_data
                    except Exception as e:
                        print(f"⚠️  加载主题 {filename} 失败：{e}")
        
        # 如果没有找到主题文件，使用内置默认主题
        if not themes:
            themes = {
                "dark": {
                    "name": "dark",
                    "display_name": "Dark - 深色模式",
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
        
        return themes
    
    def apply_theme(self, theme_name: str) -> None:
        """
        应用指定主题
        
        Args:
            theme_name: 主题名称
        """
        if theme_name not in self.themes:
            print(f"⚠️  主题 {theme_name} 不存在，使用默认主题")
            theme_name = "dark"
        
        theme: Dict[str, Any] = self.themes[theme_name]
        colors: Dict[str, str] = theme.get("colors", {})
        
        # 更新颜色
        self.bg_color: str = colors.get("background", "#1a1a2e")
        self.face_color: str = colors.get("face", "#16213e")
        self.hand_color: str = colors.get("hand", "#e94560")
        self.text_color: str = colors.get("text", "#ffffff")
        self.accent_color: str = colors.get("accent", "#0f3460")
        self.seg_color_on: str = colors.get("segment_on", "#ff3333")
        self.seg_color_off: str = colors.get("segment_off", "#331111")
        
        # 更新配置
        self.config["theme"]["name"] = theme_name
        self.config["theme"]["colors"] = colors
        
        # 重新绘制 UI（只在 UI 已初始化后调用）
        if hasattr(self, 'canvas'):
            self.refresh_ui()
        
        # 保存配置
        self.save_config()
        
        print(f"✅ 主题已切换：{theme_name}")
    
    def refresh_ui(self) -> None:
        """
        刷新 UI 以应用新主题（深度递归刷新所有组件）
        """
        # 更新 ttk 样式
        style = ttk.Style()
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        style.configure('TRadiobutton', background=self.bg_color, foreground=self.text_color,
                       selectcolor=self.accent_color)
        style.configure('TCombobox', fieldbackground=self.bg_color, 
                       background=self.accent_color, foreground=self.text_color,
                       arrowcolor=self.text_color)
        style.configure('TButton', background=self.accent_color, foreground=self.text_color)
        style.configure('TCheckbutton', background=self.bg_color, foreground=self.text_color)
        
        # 递归更新所有组件颜色
        self._recursive_update_colors(self.root)
        
        # 更新 Canvas 背景色（与窗口底色相同）
        if hasattr(self, 'canvas'):
            self.canvas.configure(bg=self.bg_color)
        
        # 更新数码管 Canvas 背景色
        if hasattr(self, 'seg_canvas'):
            self.seg_canvas.configure(bg=self.face_color)
        
        # 更新秒表 Label 颜色
        if hasattr(self, 'stopwatch_label'):
            self.stopwatch_label.config(fg=self.seg_color_on)
        
        # 更新计时器 Label 颜色
        if hasattr(self, 'timer_label'):
            self.timer_label.config(fg=self.text_color)
        
        # 重新绘制表盘
        self.draw_clock_face()
        
        # 如果是数字模式，重新绘制数码管
        if self.mode_var.get() == "digital":
            now = datetime.datetime.now()
            time_str = now.strftime("%H:%M:%S")
            self.draw_seven_segment_time(time_str)
        
        # 如果是秒表模式，重新绘制
        if self.mode_var.get() == "stopwatch":
            if hasattr(self, 'stopwatch_elapsed_ms'):
                self.stopwatch_time_var.set(self._format_time_ms(self.stopwatch.elapsed_ms))
        
        # 强制刷新窗口
        self.root.update_idletasks()
    
    def _recursive_update_colors(self, widget: tk.Widget) -> None:
        """
        递归更新组件颜色
        
        Args:
            widget: 要更新的组件
        """
        try:
            # 根据组件类型更新颜色
            if isinstance(widget, (tk.Frame, tk.LabelFrame)):
                widget.configure(bg=self.bg_color)
            elif isinstance(widget, tk.Label):
                widget.configure(bg=self.bg_color, fg=self.text_color)
            elif isinstance(widget, tk.Radiobutton):
                widget.configure(bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                               activebackground=self.bg_color, activeforeground=self.text_color)
            elif isinstance(widget, ttk.Combobox):
                widget.configure(style='TCombobox')
            elif isinstance(widget, tk.Button):
                widget.configure(bg=self.accent_color, fg=self.text_color,
                               activebackground=self.bg_color, activeforeground=self.text_color)
            elif isinstance(widget, ttk.Button):
                widget.configure(style='TButton')
            elif isinstance(widget, tk.Canvas):
                widget.configure(bg=self.face_color)
            elif isinstance(widget, tk.Listbox):
                widget.configure(bg=self.face_color, fg=self.text_color, 
                                selectbackground=self.accent_color, selectforeground=self.text_color)
            elif isinstance(widget, ttk.Checkbutton):
                widget.configure(style='TCheckbutton')
            elif isinstance(widget, tk.Checkbutton):
                widget.configure(bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color)
            
            # 递归更新子组件
            for child in widget.winfo_children():
                self._recursive_update_colors(child)
        except (tk.TclError, AttributeError) as e:
            pass  # 某些组件不支持某些属性
    
    def setup_ui(self) -> None:
        """设置用户界面"""
        # Main frame
        main_frame: tk.Frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Timezone selector - 东西各 12 时区
        tz_frame: tk.Frame = tk.Frame(main_frame, bg=self.bg_color)
        tz_frame.pack(pady=(0, 10))
        
        tk.Label(tz_frame, text="时区:", bg=self.bg_color, fg=self.text_color, font=("Arial", 10)).pack(side=tk.LEFT)
        
        # 格式化时区选项显示
        tz_values: List[str] = [f"{tz[0]} {tz[2]} ({tz[1]})" for tz in self.timezones]
        self.tz_combo: ttk.Combobox = ttk.Combobox(tz_frame, values=tz_values, width=28, state="readonly")
        # 设置默认时区（从配置加载）
        default_tz_display: str = f"UTC+8 上海 (Asia/Shanghai)"
        for tz_val in tz_values:
            if self.timezone in tz_val:
                default_tz_display = tz_val
                break
        self.tz_combo.set(default_tz_display)
        self.tz_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.tz_combo.bind("<<ComboboxSelected>>", self.on_timezone_change)
        
        # Theme selector - 主题选择器
        theme_frame: tk.Frame = tk.Frame(main_frame, bg=self.bg_color)
        theme_frame.pack(pady=(0, 10))
        
        tk.Label(theme_frame, text="主题:", bg=self.bg_color, fg=self.text_color, font=("Arial", 10)).pack(side=tk.LEFT)
        
        # 格式化主题选项显示
        theme_values: List[str] = []
        theme_name_to_display: Dict[str, str] = {}
        for name, data in self.themes.items():
            display_name: str = data.get("display_name", name)
            theme_values.append(display_name)
            theme_name_to_display[display_name] = name
        
        self.theme_combo: ttk.Combobox = ttk.Combobox(theme_frame, values=theme_values, width=28, state="readonly")
        # 设置默认主题（从配置加载）
        current_theme_name: str = self.config.get("theme", {}).get("name", "dark")
        current_display: str = self.themes.get(current_theme_name, {}).get("display_name", theme_values[0] if theme_values else "Dark")
        self.theme_combo.set(current_display)
        self.theme_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
        
        # Store theme name mapping
        self.theme_name_to_display: Dict[str, str] = theme_name_to_display
        self.theme_display_to_name: Dict[str, str] = {v: k for k, v in theme_name_to_display.items()}
        
        # Mode toggle - Analog, Digital, Stopwatch
        self.mode_var: tk.StringVar = tk.StringVar(value=self.display_mode)
        mode_frame: tk.Frame = tk.Frame(main_frame, bg=self.bg_color)
        mode_frame.pack(pady=(0, 10))
        
        tk.Radiobutton(mode_frame, text="Analog", variable=self.mode_var, value="analog", 
                       bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                       command=self.update_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Digital", variable=self.mode_var, value="digital", 
                       bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                       command=self.update_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="⏱️ 秒表", variable=self.mode_var, value="stopwatch", 
                       bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                       command=self.update_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="⏳ 倒计时", variable=self.mode_var, value="timer", 
                       bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                       command=self.update_mode).pack(side=tk.LEFT, padx=5)
        
        # 功能按钮框架
        btn_frame: tk.Frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(pady=(0, 10))
        
        # 闹钟按钮
        tk.Button(btn_frame, text="⏰ 闹钟", command=self.show_alarm_dialog, 
                  bg=self.accent_color, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        
        # 全屏按钮
        self.fullscreen_btn: tk.Button = tk.Button(btn_frame, text="🔲 全屏", command=self.toggle_fullscreen,
                                                    bg=self.accent_color, fg=self.text_color)
        self.fullscreen_btn.pack(side=tk.LEFT, padx=5)
        
        # 置顶按钮
        self.topmost_btn: tk.Button = tk.Button(btn_frame, text="📌 置顶", command=self.toggle_topmost,
                                                 bg=self.accent_color, fg=self.text_color)
        self.topmost_btn.pack(side=tk.LEFT, padx=5)
        
        # 更新按钮状态
        self._update_button_states()
        
        # Canvas for analog clock - 居中显示（底色与窗口底色相同）
        self.canvas: tk.Canvas = tk.Canvas(main_frame, width=300, height=300, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(pady=10)  # 居中显示
        
        # Digital time display - 7 段数码管风格（初始隐藏）
        self.digital_frame: tk.Frame = tk.Frame(main_frame, bg=self.bg_color)
        # 不立即 pack，由 update_mode 控制显示
        
        # 7 段数码管画布 - 计算所需宽度
        canvas_width: int = 560
        canvas_height: int = 130
        self.seg_canvas: tk.Canvas = tk.Canvas(self.digital_frame, width=canvas_width, height=canvas_height, 
                                                bg=self.bg_color, highlightthickness=0)
        self.seg_canvas.pack(expand=True)
        
        self.date_label: tk.Label = tk.Label(self.digital_frame, text="", font=("Arial", 14), 
                                              bg=self.bg_color, fg=self.text_color)
        self.date_label.pack(pady=10)
        
        # 秒表 UI 框架（初始隐藏）
        self.stopwatch_frame: tk.Frame = tk.Frame(main_frame, bg=self.bg_color)
        
        # 秒表时间显示（Label 方式）
        self.stopwatch_time_var: tk.StringVar = tk.StringVar(value="00:00:00.00")  # 毫秒两位显示
        self.stopwatch_label: tk.Label = tk.Label(self.stopwatch_frame, textvariable=self.stopwatch_time_var,
                                                   font=("Courier New", 72, "bold"), bg=self.bg_color, 
                                                   fg=self.seg_color_on, relief=tk.FLAT)
        self.stopwatch_label.pack(pady=20)
        
        # 呼吸灯效果控制
        self.breath_phase: float = 0.0  # 呼吸相位 (0-2π)
        self.breath_job: Optional[str] = None
        
        # 秒表按钮
        sw_btn_frame: tk.Frame = tk.Frame(self.stopwatch_frame, bg=self.bg_color)
        sw_btn_frame.pack(pady=10)
        
        self.sw_start_btn: tk.Button = tk.Button(sw_btn_frame, text="▶️ 开始", command=self.toggle_stopwatch,
                                                  bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10)
        self.sw_start_btn.pack(side=tk.LEFT, padx=10)
        
        self.sw_stop_btn: tk.Button = tk.Button(sw_btn_frame, text="⏸️ 停止", command=self.toggle_stopwatch,
                                                 bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10)
        self.sw_stop_btn.pack(side=tk.LEFT, padx=10)
        self.sw_stop_btn.config(state=tk.DISABLED)  # 初始禁用
        
        self.sw_lap_btn: tk.Button = tk.Button(sw_btn_frame, text="🏁 计次", command=self.record_lap,
                                                bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10)
        self.sw_lap_btn.pack(side=tk.LEFT, padx=10)
        self.sw_lap_btn.config(state=tk.DISABLED)  # 初始禁用
        
        tk.Button(sw_btn_frame, text="🔄 重置", command=self.reset_stopwatch,
                  bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10).pack(side=tk.LEFT, padx=10)
        
        # 计次记录列表
        self.lap_listbox: tk.Listbox = tk.Listbox(self.stopwatch_frame, font=("Courier New", 12),
                                                   bg=self.face_color, fg=self.text_color, height=8, width=30,
                                                   selectbackground=self.accent_color, selectforeground=self.text_color)
        self.lap_listbox.pack(pady=10)
        
        # 倒计时 UI 框架（初始隐藏）
        self.timer_frame: tk.Frame = tk.Frame(main_frame, bg=self.bg_color)
        
        # 倒计时时间显示
        self.timer_time_var: tk.StringVar = tk.StringVar(value="00:00:00")
        self.timer_label: tk.Label = tk.Label(self.timer_frame, textvariable=self.timer_time_var,
                                               font=("Courier New", 72, "bold"), bg=self.bg_color, fg=self.text_color)
        self.timer_label.pack(pady=20)
        
        # 倒计时状态标签
        self.timer_status_var: tk.StringVar = tk.StringVar(value="准备就绪")
        self.timer_status_label: tk.Label = tk.Label(self.timer_frame, textvariable=self.timer_status_var,
                                                      font=("Arial", 14), bg=self.bg_color, fg=self.text_color)
        self.timer_status_label.pack(pady=5)
        
        # 预设时间按钮框架
        timer_preset_frame: tk.Frame = tk.Frame(self.timer_frame, bg=self.bg_color)
        timer_preset_frame.pack(pady=10)
        
        # 预设时间按钮
        preset_configs = [
            ("🍅 番茄钟", 1500, "番茄钟"),
            ("☕ 短休息", 300, "短休息"),
            ("🛌 长休息", 900, "长休息"),
            ("⏱️ 5 分钟", 300, "5 分钟"),
            ("⏱️ 10 分钟", 600, "10 分钟"),
            ("⏱️ 30 分钟", 1800, "30 分钟"),
        ]
        
        self.timer_preset_buttons = []
        for text, seconds, name in preset_configs:
            btn = tk.Button(timer_preset_frame, text=text, command=lambda s=seconds, n=name: self.set_timer_preset(s, n),
                           bg=self.accent_color, fg=self.text_color, font=("Arial", 11), width=11)
            btn.pack(side=tk.LEFT, padx=5)
            self.timer_preset_buttons.append(btn)
        
        # 自定义时间输入框架
        custom_frame = tk.Frame(self.timer_frame, bg=self.bg_color)
        custom_frame.pack(pady=10)
        
        tk.Label(custom_frame, text="自定义:", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
        
        self.timer_hour_entry = tk.Entry(custom_frame, width=4, justify='center')
        self.timer_hour_entry.insert(0, "00")
        self.timer_hour_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(custom_frame, text=":", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
        
        self.timer_min_entry = tk.Entry(custom_frame, width=4, justify='center')
        self.timer_min_entry.insert(0, "00")
        self.timer_min_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(custom_frame, text=":", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
        
        self.timer_sec_entry = tk.Entry(custom_frame, width=4, justify='center')
        self.timer_sec_entry.insert(0, "00")
        self.timer_sec_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Button(custom_frame, text="设置", command=self.set_timer_custom, bg=self.accent_color, 
                  fg=self.text_color).pack(side=tk.LEFT, padx=5)
        
        # 倒计时控制按钮
        timer_btn_frame: tk.Frame = tk.Frame(self.timer_frame, bg=self.bg_color)
        timer_btn_frame.pack(pady=15)
        
        self.timer_start_btn: tk.Button = tk.Button(timer_btn_frame, text="▶️ 开始", command=self.toggle_timer,
                                                     bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10)
        self.timer_start_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(timer_btn_frame, text="🔄 重置", command=self.reset_timer,
                  bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10).pack(side=tk.LEFT, padx=10)
        
        # 声音开关
        self.timer_sound_var: tk.BooleanVar = tk.BooleanVar(value=True)
        tk.Checkbutton(timer_btn_frame, text="🔊 声音", variable=self.timer_sound_var,
                      bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                      command=self.toggle_timer_sound).pack(side=tk.LEFT, padx=10)
        
        # 7 段数码管段定义 (a,b,c,d,e,f,g) - 单个数字的段坐标
        # 优化长宽比，让数码管更接近日常看到的样子
        # 经典数码管比例：宽:高 ≈ 2:3，段宽约为主宽度的1/3
        self.seg_width: int = 60       # 段宽度（适中）
        self.seg_height: int = 100      # 段高度（保证纵向比例）
        self.seg_thickness: int = 14   # 段粗细（适中，不要太粗也不要太细）
        self.digit_spacing: int = 10    # 数字间距（紧凑些）
        self.colon_space: int = 25     # 冒号区空间（稍小）
        
        # Draw clock face
        self.draw_clock_face()
        
        # 绑定键盘快捷键
        self.root.bind('<space>', self.on_space_key)
        self.root.bind('<r>', lambda e: self.on_reset_key())
        self.root.bind('<R>', lambda e: self.on_reset_key())
        self.root.bind('<f>', lambda e: self.toggle_fullscreen())
        self.root.bind('<F>', lambda e: self.toggle_fullscreen())
        self.root.bind('<t>', lambda e: self.toggle_topmost())
        self.root.bind('<T>', lambda e: self.toggle_topmost())
        # 注意：不绑定数字键 1/2/3 到模式切换，避免与输入框冲突
        
        # UI 初始化完成后，应用当前主题（刷新所有组件颜色）
        if hasattr(self, 'canvas'):
            self.refresh_ui()
        
        # 初始化显示模式（确保显示正确的模式）
        self.update_mode()
    
    def _update_button_states(self) -> None:
        """更新按钮状态显示"""
        is_fullscreen = self.config.get("window", {}).get("fullscreen", False)
        is_topmost = self.config.get("window", {}).get("always_on_top", False)
        
        self.fullscreen_btn.config(text="❐ 退出全屏" if is_fullscreen else "🔲 全屏")
        self.topmost_btn.config(text="📍 取消置顶" if is_topmost else "📌 置顶")
    
    def on_space_key(self, event: tk.Event) -> None:
        """
        空格键处理 - 启动/停止当前模式
        
        Args:
            event: Tkinter 事件对象
        """
        mode = self.mode_var.get()
        if mode == 'stopwatch':
            self.toggle_stopwatch()
        elif mode == 'timer':
            self.toggle_timer()
    
    def on_reset_key(self) -> None:
        """重置当前模式"""
        mode = self.mode_var.get()
        if mode == 'stopwatch':
            self.reset_stopwatch()
        elif mode == 'timer':
            self.reset_timer()
    
    def toggle_fullscreen(self) -> None:
        """切换全屏模式"""
        is_fullscreen = self.config.get("window", {}).get("fullscreen", False)
        new_state = not is_fullscreen
        
        self.root.attributes("-fullscreen", new_state)
        self.config["window"]["fullscreen"] = new_state
        self._update_button_states()
        self.save_config()
        
        print(f"✅ 全屏模式：{'开启' if new_state else '关闭'}")
    
    def toggle_topmost(self) -> None:
        """切换窗口置顶"""
        is_topmost = self.config.get("window", {}).get("always_on_top", False)
        new_state = not is_topmost
        
        self.root.attributes("-topmost", new_state)
        self.config["window"]["always_on_top"] = new_state
        self._update_button_states()
        self.save_config()
        
        print(f"✅ 窗口置顶：{'开启' if new_state else '关闭'}")
    
    def show_alarm_dialog(self) -> None:
        """显示闹钟管理对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⏰ 闹钟管理")
        dialog.geometry("400x300")
        dialog.attributes("-topmost", True)
        
        # 居中显示
        dialog_x = int(self.root.winfo_x() + self.root.winfo_width() / 2 - 200)
        dialog_y = int(self.root.winfo_y() + self.root.winfo_height() / 2 - 150)
        dialog.geometry(f"400x300+{dialog_x}+{dialog_y}")
        
        # 闹钟列表框架
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建列表框
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.alarm_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set)
        self.alarm_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.alarm_listbox.yview)
        
        # 填充闹钟列表
        self._refresh_alarm_listbox()
        
        # 按钮框架
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="添加闹钟", command=lambda: self._add_alarm_from_dialog(dialog)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除选中", command=lambda: self._delete_selected_alarm(dialog)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="切换状态", command=lambda: self._toggle_selected_alarm(dialog)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="关闭", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _refresh_alarm_listbox(self) -> None:
        """刷新闹钟列表框"""
        self.alarm_listbox.delete(0, tk.END)
        day_labels = ["一", "二", "三", "四", "五", "六", "日"]
        for i, alarm in enumerate(self.alarms):
            status = "✓" if alarm.enabled else "✗"
            label = f"{status} {alarm.time}"
            if alarm.label:
                label += f" - {alarm.label}"
            # 显示重复周期
            if alarm.repeat_days:
                days_str = "".join(day_labels[d] for d in sorted(alarm.repeat_days))
                label += f" [{days_str}]"
            else:
                label += " [仅一次]"
            self.alarm_listbox.insert(tk.END, label)
    
    def _add_alarm_from_dialog(self, dialog: tk.Toplevel) -> None:
        """从对话框添加闹钟（带重复周期选择）"""
        add_dialog = tk.Toplevel(dialog)
        add_dialog.title("添加闹钟")
        add_dialog.geometry("350x280")
        add_dialog.attributes("-topmost", True)
        
        # 时间输入
        tk.Label(add_dialog, text="时间 (HH:MM):").pack(pady=5)
        time_entry = tk.Entry(add_dialog)
        time_entry.pack(pady=5)
        time_entry.insert(0, "07:00")
        
        # 标签输入
        tk.Label(add_dialog, text="标签 (可选):").pack(pady=5)
        label_entry = tk.Entry(add_dialog)
        label_entry.pack(pady=5)
        
        # 重复周期选择
        tk.Label(add_dialog, text="重复周期:").pack(pady=(10, 5))
        
        # 快捷按钮
        quick_frame = tk.Frame(add_dialog)
        quick_frame.pack(pady=5)
        
        repeat_vars = [tk.BooleanVar() for _ in range(7)]
        
        def set_weekdays():
            """设置工作日（周一到周五）"""
            for i in range(7):
                repeat_vars[i].set(i < 5)
        
        def set_weekends():
            """设置周末（周六、周日）"""
            for i in range(7):
                repeat_vars[i].set(i >= 5)
        
        def set_everyday():
            """设置每天"""
            for i in range(7):
                repeat_vars[i].set(True)
        
        tk.Button(quick_frame, text="工作日", command=set_weekdays, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_frame, text="周末", command=set_weekends, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_frame, text="每天", command=set_everyday, width=8).pack(side=tk.LEFT, padx=2)
        
        # 7 个复选框（周一到周日）
        days_frame = tk.Frame(add_dialog)
        days_frame.pack(pady=5)
        
        day_labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for i in range(7):
            cb = tk.Checkbutton(days_frame, text=day_labels[i], variable=repeat_vars[i])
            cb.pack(side=tk.LEFT, padx=3)
        
        def add():
            time_str = time_entry.get().strip()
            label = label_entry.get().strip()
            # 收集选中的重复日期
            selected_days = [i for i in range(7) if repeat_vars[i].get()]
            if self.add_alarm(time_str, label, selected_days):
                self._refresh_alarm_listbox()
                add_dialog.destroy()
            else:
                messagebox.showerror("错误", "无效的时间格式，请使用 HH:MM 格式")
        
        tk.Button(add_dialog, text="添加", command=add).pack(pady=10)
    
    def _delete_selected_alarm(self, dialog: tk.Toplevel) -> None:
        """删除选中的闹钟"""
        selection = self.alarm_listbox.curselection()
        if selection:
            index = selection[0]
            self.remove_alarm(index)
            self._refresh_alarm_listbox()
        else:
            messagebox.showwarning("提示", "请先选择一个闹钟")
    
    def _toggle_selected_alarm(self, dialog: tk.Toplevel) -> None:
        """切换选中闹钟的状态"""
        selection = self.alarm_listbox.curselection()
        if selection:
            index = selection[0]
            self.toggle_alarm(index)
            self._refresh_alarm_listbox()
        else:
            messagebox.showwarning("提示", "请先选择一个闹钟")
    
    # ==================== 秒表功能 ====================
    
    def toggle_stopwatch(self) -> None:
        """启动/停止秒表（开始/暂停/继续）"""
        if self.stopwatch.is_running:
            # 暂停秒表
            self.stopwatch.is_running = False
            if self.stopwatch_job:
                self.root.after_cancel(self.stopwatch_job)
                self.stopwatch_job = None
            self.sw_start_btn.config(text="▶️ 继续")  # 暂停后显示"继续"
            self.sw_stop_btn.config(state=tk.DISABLED)
            self.sw_lap_btn.config(state=tk.DISABLED)
            # 停止呼吸灯
            self._stop_breath_effect()
            print("⏱️ 秒表已暂停")
        else:
            # 启动/继续秒表
            self.stopwatch.is_running = True
            self.stopwatch.start_time = time.time()
            # 根据已用时间判断显示"开始"还是"继续"
            if self.stopwatch.elapsed_ms == 0:
                self.sw_start_btn.config(text="⏸️ 暂停")  # 首次启动显示"暂停"
            else:
                self.sw_start_btn.config(text="⏸️ 暂停")  # 继续时显示"暂停"
            self.sw_stop_btn.config(state=tk.NORMAL)
            self.sw_lap_btn.config(state=tk.NORMAL)
            self._update_stopwatch_display()
            print("⏱️ 秒表已启动")
    
    def reset_stopwatch(self) -> None:
        """重置秒表"""
        # 如果正在运行，先停止
        if self.stopwatch.is_running:
            self.stopwatch.is_running = False
            if self.stopwatch_job:
                self.root.after_cancel(self.stopwatch_job)
                self.stopwatch_job = None
        
        # 停止呼吸灯
        self._stop_breath_effect()
        
        # 重置状态
        self.stopwatch.elapsed_ms = 0
        self.stopwatch.laps = []
        self.stopwatch_time_var.set(self._format_time_ms(0))  # 使用格式化函数确保一致性
        self.sw_start_btn.config(text="▶️ 开始")
        
        # 清空计次列表
        self.lap_listbox.delete(0, tk.END)
        
        # 恢复主题色
        if hasattr(self, 'seg_color_on'):
            self.stopwatch_label.config(fg=self.seg_color_on)
        
        print("⏱️ 秒表已重置")
    
    def record_lap(self) -> None:
        """记录计次时间"""
        if not self.stopwatch.is_running and self.stopwatch.elapsed_ms == 0:
            messagebox.showinfo("提示", "请先启动秒表")
            return
        
        # 更新累计时间
        if self.stopwatch.is_running:
            current_time = time.time()
            delta_ms = int((current_time - self.stopwatch.start_time) * 1000)
            total_ms = self.stopwatch.elapsed_ms + delta_ms
            self.stopwatch.start_time = current_time
            self.stopwatch.elapsed_ms = total_ms
        
        total_ms = self.stopwatch.elapsed_ms
        
        # 计算单圈时间
        if self.stopwatch.laps:
            last_lap_ms = self.stopwatch.laps[-1].time_ms
            split_ms = total_ms - last_lap_ms
        else:
            split_ms = total_ms
        
        # 创建计次记录
        lap_number = len(self.stopwatch.laps) + 1
        lap = LapRecord(
            lap_number=lap_number,
            time_ms=total_ms,
            split_ms=split_ms
        )
        self.stopwatch.laps.append(lap)
        
        # 更新显示
        self._update_stopwatch_display()
        
        # 添加到列表 (最新在最上面)
        lap_text = f"圈{lap_number:2d} | {self._format_time_ms(total_ms)} | {self._format_time_ms(split_ms)}"
        self.lap_listbox.insert(0, lap_text)
        
        print(f"⏱️ 计次 #{lap_number}: {self._format_time_ms(total_ms)}")
    
    def _update_stopwatch_display(self) -> None:
        """更新秒表显示"""
        # 如果 UI 未初始化，直接返回
        if not hasattr(self, 'stopwatch_time_var'):
            return
        
        if self.stopwatch.is_running:
            # 计算当前时间
            current_time = time.time()
            delta_ms = int((current_time - self.stopwatch.start_time) * 1000)
            total_ms = self.stopwatch.elapsed_ms + delta_ms
            self.stopwatch_time_var.set(self._format_time_ms(total_ms))
            
            # 运行时启动呼吸灯效果
            if not self.breath_job:
                self._start_breath_effect()
            
            # 继续更新 (每 10ms)
            self.stopwatch_job = self.root.after(10, self._update_stopwatch_display)
        else:
            # 停止状态，显示累计时间
            self.stopwatch_time_var.set(self._format_time_ms(self.stopwatch.elapsed_ms))
            # 停止呼吸灯
            self._stop_breath_effect()
            # 恢复主题色
            if hasattr(self, 'seg_color_on'):
                self.stopwatch_label.config(fg=self.seg_color_on)
    
    def _format_time_ms(self, ms: int) -> str:
        """格式化时间为 HH:MM:SS.ms 格式（毫秒保留两位）"""
        hours = ms // 3600000
        minutes = (ms % 3600000) // 60000
        seconds = (ms % 60000) // 1000
        milliseconds = (ms % 1000) // 10  # 保留两位（除以 10 去掉最后一位）
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
    
    def _start_breath_effect(self) -> None:
        """启动呼吸灯效果"""
        self._update_breath_effect()
    
    def _stop_breath_effect(self) -> None:
        """停止呼吸灯效果"""
        if self.breath_job:
            self.root.after_cancel(self.breath_job)
            self.breath_job = None
    
    def _update_breath_effect(self) -> None:
        """更新呼吸灯效果（颜色渐变）"""
        import math
        
        # 更新呼吸相位
        self.breath_phase += 0.1
        if self.breath_phase > 2 * math.pi:
            self.breath_phase -= 2 * math.pi
        
        # 计算呼吸因子 (0.3 - 1.0)
        breath_factor = 0.65 + 0.35 * math.sin(self.breath_phase)
        
        # 根据主题色计算当前颜色
        if hasattr(self, 'seg_color_on'):
            # 将十六进制颜色转换为 RGB
            r = int(self.seg_color_on[1:3], 16)
            g = int(self.seg_color_on[3:5], 16)
            b = int(self.seg_color_on[5:7], 16)
            
            # 应用呼吸因子（变暗）
            r = int(r * breath_factor)
            g = int(g * breath_factor)
            b = int(b * breath_factor)
            
            # 转换回十六进制
            breath_color = f"#{r:02x}{g:02x}{b:02x}"
            self.stopwatch_label.config(fg=breath_color)
        
        # 继续更新
        self.breath_job = self.root.after(50, self._update_breath_effect)
    
    def draw_clock_face(self) -> None:
        """绘制时钟表盘"""
        self.canvas.delete("all")
        cx, cy, r = 150, 150, 130
        
        # Clock face circle
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=self.hand_color, width=3)
        
        # Hour marks
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = cx + (r - 15) * math.cos(angle)
            y1 = cy + (r - 15) * math.sin(angle)
            x2 = cx + (r - 5) * math.cos(angle)
            y2 = cy + (r - 5) * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2, fill=self.text_color, width=2)
        
        # Minute marks
        for i in range(60):
            if i % 5 != 0:
                angle = math.radians(i * 6 - 90)
                x1 = cx + (r - 10) * math.cos(angle)
                y1 = cy + (r - 10) * math.sin(angle)
                x2 = cx + (r - 5) * math.cos(angle)
                y2 = cy + (r - 5) * math.sin(angle)
                self.canvas.create_line(x1, y1, x2, y2, fill=self.text_color, width=1)
        
        # Center dot
        self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill=self.hand_color)
    
    def draw_segment(self, x1: float, y1: float, x2: float, y2: float, active: bool) -> None:
        """绘制单个段（带轻微发光效果）"""
        # 根据 active 状态设置颜色和粗细
        color: str = self.seg_color_on if active else self.seg_color_off
        thickness: int = self.seg_thickness + 2 if active else self.seg_thickness
        
        self.seg_canvas.create_line(x1, y1, x2, y2, fill=color, width=thickness, 
                                    capstyle=tk.ROUND, joinstyle=tk.ROUND)
    
    def draw_digit(self, digit: int, x_offset: float) -> None:
        """绘制 7 段数码管数字"""
        # 数字对应的段 (a,b,c,d,e,f,g)
        digit_segs: Dict[int, List[bool]] = {
            0: [True, True, True, True, True, True, False],
            1: [False, True, True, False, False, False, False],
            2: [True, True, False, True, True, False, True],
            3: [True, True, True, True, False, False, True],
            4: [False, True, True, False, False, True, True],
            5: [True, False, True, True, False, True, True],
            6: [True, False, True, True, True, True, True],
            7: [True, True, True, False, False, False, False],
            8: [True, True, True, True, True, True, True],
            9: [True, True, True, True, False, True, True],
        }
        
        segs: List[bool] = digit_segs.get(digit, [False, False, False, False, False, False, False])
        
        # 段坐标定义（相对于数字左上角）
        w: int = self.seg_width      # 40px 宽度
        h: int = self.seg_height     # 65px 高度
        t: int = self.seg_thickness  # 10px 粗细
        margin: int = 5              # 数字边缘留白（加大一点让段更饱满）
        
        # a: 上横
        self.draw_segment(x_offset + margin + t, margin, x_offset + w - margin - t, margin, segs[0])
        # b: 右上竖
        self.draw_segment(x_offset + w - margin, margin + t, x_offset + w - margin, h // 2 - t, segs[1])
        # c: 右下竖
        self.draw_segment(x_offset + w - margin, h // 2 + t, x_offset + w - margin, h - margin - t, segs[2])
        # d: 下横
        self.draw_segment(x_offset + margin + t, h - margin, x_offset + w - margin - t, h - margin, segs[3])
        # e: 左下竖
        self.draw_segment(x_offset + margin, h // 2 + t, x_offset + margin, h - margin - t, segs[4])
        # f: 左上竖
        self.draw_segment(x_offset + margin, margin + t, x_offset + margin, h // 2 - t, segs[5])
        # g: 中横
        self.draw_segment(x_offset + margin + t, h // 2, x_offset + w - margin - t, h // 2, segs[6])
    
    def draw_colon(self, x_offset: float) -> None:
        """绘制冒号分隔符（直径与数码字笔画宽度相同）"""
        r: int = self.seg_thickness // 2  # 冒号半径 = 笔画宽度的一半（直径=笔画宽度）
        h: int = self.seg_height
        cx: float = x_offset
        cy1: float = h // 3      # 上圆点垂直位置
        cy2: float = h * 2 // 3  # 下圆点垂直位置
        self.seg_canvas.create_oval(cx-r, cy1-r, cx+r, cy1+r, fill=self.seg_color_on)
        self.seg_canvas.create_oval(cx-r, cy2-r, cx+r, cy2+r, fill=self.seg_color_on)
    
    def draw_seven_segment_time(self, time_str: str) -> None:
        """绘制 7 段数码管时间显示（时分秒间隔一个数码字宽度）"""
        self.seg_canvas.delete("all")
        
        # 解析时间 HH:MM:SS
        parts: List[str] = time_str.split(":")
        if len(parts) >= 3:
            digits: List[int] = [int(parts[0][0]), int(parts[0][1]),  # 小时
                          int(parts[1][0]), int(parts[1][1]),  # 分钟
                          int(parts[2][0]), int(parts[2][1])]  # 秒
            
            # 计算每位数字的 x 偏移量
            w: int = self.seg_width      # 数字宽度
            s: int = self.digit_spacing  # 数字间距
            c: int = w                   # 冒号区空间 = 一个数码字宽度（时分秒间隔一个数码字）
            margin: int = 15             # 左右边距
            
            # 逐步计算每个位置的起始 x 坐标
            x0: float = margin                                    # 小时十位
            x1: float = x0 + w + s                                # 小时个位
            x2: float = x1 + w + s + c                            # 分钟十位（跳过一个数码字宽度的间隔）
            x3: float = x2 + w + s                                # 分钟个位
            x4: float = x3 + w + s + c                            # 秒钟十位（跳过一个数码字宽度的间隔）
            x5: float = x4 + w + s                                # 秒钟个位
            
            offsets: List[float] = [x0, x1, x2, x3, x4, x5]
            
            for i, digit in enumerate(digits):
                self.draw_digit(digit, offsets[i])
            
            # 绘制冒号（在间隔正中央）
            colon1_x: float = x1 + w + s + c // 2    # 时分之间的冒号（间隔中间）
            colon2_x: float = x3 + w + s + c // 2    # 分秒之间的冒号（间隔中间）
            self.draw_colon(colon1_x)
            self.draw_colon(colon2_x)
    
    def update_clock(self) -> None:
        """更新时钟显示"""
        # Get current time in selected timezone
        try:
            tz = datetime.timezone(datetime.timedelta(hours=0))
            if self.timezone != "UTC":
                import zoneinfo
                tz = zoneinfo.ZoneInfo(self.timezone)
            
            now = datetime.datetime.now(tz)
        except Exception:
            now = datetime.datetime.now()
        
        hour: int = now.hour
        minute: int = now.minute
        second: int = now.second
        microsecond: int = now.microsecond
        
        # Update analog clock
        if self.mode_var.get() == "analog":
            self.draw_analog_clock(hour, minute, second)
        
        # Update digital clock - 7 段数码管显示
        if self.mode_var.get() == "digital":
            time_str: str = now.strftime("%H:%M:%S")
            self.draw_seven_segment_time(time_str)
            date_str: str = now.strftime("%Y-%m-%d %A")
            tz_info: Optional[Tuple[str, str, str]] = next((tz for tz in self.timezones if tz[1] == self.timezone), None)
            tz_display: str = f"{tz_info[0]} {tz_info[2]}" if tz_info else self.timezone
            self.date_label.config(text=f"{date_str}\n{tz_display}")
        
        # Schedule next update
        self.root.after(50, self.update_clock)
    
    def draw_analog_clock(self, hour: int, minute: int, second: int) -> None:
        """绘制模拟时钟"""
        cx, cy, r = 150, 150, 130
        
        # Clear previous hands
        self.canvas.delete("hands")
        
        # Second hand
        sec_angle = math.radians(second * 6 - 90)
        sec_len = r - 20
        x2 = cx + sec_len * math.cos(sec_angle)
        y2 = cy + sec_len * math.sin(sec_angle)
        self.canvas.create_line(cx, cy, x2, y2, fill="#ff6b6b", width=2, tags="hands")
        
        # Minute hand
        min_angle = math.radians(minute * 6 - 90)
        min_len = r - 30
        x2 = cx + min_len * math.cos(min_angle)
        y2 = cy + min_len * math.sin(min_angle)
        self.canvas.create_line(cx, cy, x2, y2, fill=self.text_color, width=4, tags="hands")
        
        # Hour hand
        hour_angle = math.radians((hour % 12 + minute / 60) * 30 - 90)
        hour_len = r - 60
        x2 = cx + hour_len * math.cos(hour_angle)
        y2 = cy + hour_len * math.sin(hour_angle)
        self.canvas.create_line(cx, cy, x2, y2, fill=self.hand_color, width=6, tags="hands")
    
    def on_timezone_change(self, event: tk.Event) -> None:
        """时区切换事件处理"""
        # 从显示格式中提取时区 ID
        selected: str = self.tz_combo.get()
        # 格式："UTC+X 城市名 (timezone.id)"
        try:
            tz_id: str = selected.split("(")[1].split(")")[0]
            self.timezone = tz_id
            # 更新配置并保存
            self.config["timezone"] = tz_id
            self.save_config()
        except Exception:
            self.timezone = selected
            # 更新配置并保存
            self.config["timezone"] = selected
            self.save_config()
    
    def on_theme_change(self, event: tk.Event) -> None:
        """主题切换事件处理"""
        selected: str = self.theme_combo.get()
        # 从显示名映射到主题名
        theme_name: str = self.theme_display_to_name.get(selected, "dark")
        # 应用新主题
        self.apply_theme(theme_name)
    
    def update_mode(self) -> None:
        """切换显示模式"""
        mode: str = self.mode_var.get()
        
        if mode == "analog":
            self.canvas.pack(pady=10)  # 居中显示
            self.digital_frame.pack_forget()
            self.stopwatch_frame.pack_forget()
            self.timer_frame.pack_forget()
        elif mode == "digital":
            self.canvas.pack_forget()
            self.digital_frame.pack(pady=10)  # 居中显示
            self.stopwatch_frame.pack_forget()
            self.timer_frame.pack_forget()
        elif mode == "stopwatch":
            self.canvas.pack_forget()
            self.digital_frame.pack_forget()
            self.stopwatch_frame.pack(pady=10)  # 居中显示
            self.timer_frame.pack_forget()
            self.update_stopwatch_display()  # 刷新秒表显示
        elif mode == "timer":
            self.canvas.pack_forget()
            self.digital_frame.pack_forget()
            self.stopwatch_frame.pack_forget()
            self.timer_frame.pack(pady=10)  # 居中显示
            self.update_timer_display()  # 刷新倒计时显示
        
        # 更新配置并保存
        self.config["display_mode"] = mode
        self.save_config()
    
    # ========== 秒表功能方法 ==========
    
    def format_stopwatch_time(self, elapsed_ms: int) -> str:
        """
        格式化秒表时间为显示字符串
        
        Args:
            elapsed_ms: 毫秒数
        
        Returns:
            str: 格式化后的时间字符串 MM:SS.ms
        """
        total_seconds = elapsed_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        milliseconds = (elapsed_ms % 1000) // 10  # 显示 2 位毫秒
        
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
    
    # ========== 以下旧的 stopwatch_* 方法已废弃，使用 toggle_stopwatch 等新方法 ==========
    
    def stopwatch_start(self) -> None:
        """开始秒表计时"""
        if not self.stopwatch.is_running:
            self.stopwatch.is_running = True
            self.stopwatch.start_time = time.time()
            # 启动显示更新（如果 root 存在）
            if hasattr(self, 'root') and hasattr(self.root, 'after'):
                self.stopwatch_job = self.root.after(50, self._update_stopwatch_display_loop)
            
            # 更新按钮状态（如果按钮存在）
            if hasattr(self, 'sw_start_btn'):
                self.sw_start_btn.config(state=tk.DISABLED)
                self.sw_stop_btn.config(state=tk.NORMAL)
                self.sw_lap_btn.config(state=tk.NORMAL)
            
            print("⏱️ 秒表已开始计时")
    
    def _update_stopwatch_display_loop(self) -> None:
        """秒表显示更新循环（用于旧的 stopwatch_start 方法）"""
        if not self.stopwatch.is_running:
            return
        
        if hasattr(self, 'stopwatch_time_var'):
            current_time = time.time()
            delta_ms = int((current_time - self.stopwatch.start_time) * 1000)
            total_ms = self.stopwatch.elapsed_ms + delta_ms
            self.stopwatch_time_var.set(self._format_time_ms(total_ms))
            # 启动呼吸灯
            if not self.breath_job:
                self._start_breath_effect()
        
        # 继续更新
        if hasattr(self, 'root') and hasattr(self.root, 'after'):
            self.stopwatch_job = self.root.after(50, self._update_stopwatch_display_loop)
    
    def stopwatch_stop(self) -> None:
        """停止秒表计时"""
        if self.stopwatch.is_running:
            # 计算并保存已用时间
            current_time = time.time()
            elapsed = int((current_time - self.stopwatch.start_time) * 1000)
            self.stopwatch.elapsed_ms += elapsed
            self.stopwatch.is_running = False
            
            # 取消定时器
            if self.stopwatch_job:
                self.root.after_cancel(self.stopwatch_job)
                self.stopwatch_job = None
            
            # 更新按钮状态（如果按钮存在）
            if hasattr(self, 'sw_start_btn'):
                self.sw_start_btn.config(state=tk.NORMAL)
                self.sw_stop_btn.config(state=tk.DISABLED)
                self.sw_lap_btn.config(state=tk.DISABLED)
            
            # 刷新显示（如果 UI 存在）
            if hasattr(self, 'stopwatch_time_var'):
                self.stopwatch_time_var.set(self._format_time_ms(self.stopwatch.elapsed_ms))
            
            print("⏱️ 秒表已停止")
    
    def stopwatch_reset(self) -> None:
        """复位秒表（归零并清除计圈记录）"""
        # 如果正在运行，先停止
        if self.stopwatch.is_running:
            self.stopwatch_stop()
        
        # 重置状态
        self.stopwatch.elapsed_ms = 0
        self.stopwatch.laps = []
        
        # 清空计圈列表（如果存在）
        if hasattr(self, 'lap_listbox'):
            self.lap_listbox.delete(0, tk.END)
        
        # 更新显示（如果 UI 存在）
        if hasattr(self, 'stopwatch_time_var'):
            self.stopwatch_time_var.set("00:00:00.00")
        
        # 更新按钮状态（如果按钮存在）
        if hasattr(self, 'sw_start_btn'):
            self.sw_start_btn.config(state=tk.NORMAL)
            self.sw_stop_btn.config(state=tk.DISABLED)
            self.sw_lap_btn.config(state=tk.DISABLED)
        
        print("⏱️ 秒表已复位")
    
    def stopwatch_lap(self) -> None:
        """记录当前圈次时间"""
        if self.stopwatch.is_running:
            current_time = time.time()
            total_elapsed = int((current_time - self.stopwatch.start_time) * 1000) + self.stopwatch.elapsed_ms
            
            # 计算单圈时间
            if self.stopwatch.laps:
                last_lap_time = self.stopwatch.laps[-1].time_ms
                split_ms = total_elapsed - last_lap_time
            else:
                split_ms = total_elapsed
            
            # 创建计圈记录
            lap_number = len(self.stopwatch.laps) + 1
            lap_record = LapRecord(
                lap_number=lap_number,
                time_ms=total_elapsed,
                split_ms=split_ms
            )
            self.stopwatch.laps.append(lap_record)
            
            # 添加到列表框（显示在顶部）
            lap_str = f"圈{lap_number:2d}: {self.format_stopwatch_time(total_elapsed)} (单圈：{self.format_stopwatch_time(split_ms)})"
            self.lap_listbox.insert(0, lap_str)
            
            # 自动滚动到顶部
            self.lap_listbox.yview_moveto(0.0)
            
            print(f"⏱️ 计圈 #{lap_number}: {self.format_stopwatch_time(total_elapsed)}")
    
    def save_stopwatch_config(self) -> None:
        """保存秒表配置到 config.json"""
        # 秒表配置通常不需要持久化（因为计时状态是临时的）
        # 但可以保存一些设置，如计圈记录（如果需要）
        pass
    
    def load_stopwatch_config(self) -> None:
        """从 config.json 加载秒表配置"""
        # 秒表状态在应用重启后重置
        self.stopwatch = StopwatchState()
    
    # ========== 倒计时功能方法 ==========
    
    def set_timer_preset(self, seconds: int, name: str) -> None:
        """
        设置预设倒计时
        
        Args:
            seconds: 总秒数
            name: 预设名称
        """
        # 如果正在运行，先停止
        if self.timer.is_running:
            self.timer_stop()
        
        self.timer.total_seconds = seconds
        self.timer.remaining_seconds = float(seconds)
        self.timer.preset_name = name
        self.timer.is_running = False
        
        # 更新显示
        self.update_timer_display()
        self.timer_status_var.set(f"已设置：{name}")
        
        # 保存配置
        self.save_timer_config()
        
        print(f"⏳ 倒计时已设置：{name} ({seconds}秒)")
    
    def set_timer_custom(self) -> None:
        """
        设置自定义倒计时时间
        
        从小时、分钟、秒输入框读取时间并设置倒计时。
        """
        try:
            hours = int(self.timer_hour_entry.get().strip() or 0)
            minutes = int(self.timer_min_entry.get().strip() or 0)
            seconds = int(self.timer_sec_entry.get().strip() or 0)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds
            
            if total_seconds <= 0:
                messagebox.showinfo("提示", "请输入有效的时间")
                return
            
            # 如果正在运行，先停止
            if self.timer.is_running:
                self.timer_stop()
            
            self.timer.total_seconds = total_seconds
            self.timer.remaining_seconds = float(total_seconds)
            self.timer.preset_name = "自定义"
            self.timer.is_running = False
            
            # 更新显示
            self.update_timer_display()
            self.timer_status_var.set(f"已设置：{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # 保存配置
            self.save_timer_config()
            
            print(f"⏳ 自定义倒计时已设置：{hours:02d}:{minutes:02d}:{seconds:02d}")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def toggle_timer(self) -> None:
        """启动/停止倒计时"""
        if self.timer.is_running:
            self.timer_stop()
        else:
            self.timer_start()
    
    def timer_start(self) -> None:
        """启动倒计时"""
        if self.timer.remaining_seconds <= 0:
            messagebox.showinfo("提示", "请先设置倒计时时间")
            return
        
        self.timer.is_running = True
        self.timer.start_time = time.time()
        self.timer_start_btn.config(text="⏸️ 暂停")
        # 启动呼吸灯效果
        self._start_timer_breath_effect()
        self._update_timer_loop()
        
        print("⏳ 倒计时已启动")
    
    def timer_stop(self) -> None:
        """暂停倒计时"""
        if self.timer.is_running:
            # 计算已流逝的时间
            elapsed = time.time() - self.timer.start_time
            self.timer.remaining_seconds = max(0, self.timer.remaining_seconds - elapsed)
            self.timer.is_running = False
            
            if self.timer_job:
                self.root.after_cancel(self.timer_job)
                self.timer_job = None
            
            # 停止呼吸灯
            self._stop_timer_breath_effect()
            
            self.timer_start_btn.config(text="▶️ 继续")
            self.timer_status_var.set("已暂停")
            self.update_timer_display()
            
            print("⏳ 倒计时已暂停")
    
    def reset_timer(self) -> None:
        """重置倒计时"""
        # 如果正在运行，先停止
        if self.timer.is_running:
            self.timer_stop()
        
        # 重置为预设时间或总时间
        if self.timer.preset_name:
            self.timer.remaining_seconds = float(self.timer.total_seconds)
        else:
            self.timer.remaining_seconds = float(self.timer.total_seconds)
        
        self.timer.is_running = False
        self.timer_start_btn.config(text="▶️ 开始")
        self.timer_status_var.set("准备就绪")
        # 停止呼吸灯和闪烁
        self._stop_timer_breath_effect()
        self._stop_timer_blink()
        self.update_timer_display()
        
        # 保存配置
        self.save_timer_config()
        
        print("⏳ 倒计时已重置")
    
    def toggle_timer_sound(self) -> None:
        """切换声音提醒"""
        self.timer.sound_enabled = self.timer_sound_var.get()
        self.save_timer_config()
        print(f"🔊 倒计时声音：{'开启' if self.timer.sound_enabled else '关闭'}")
    
    def _update_timer_loop(self) -> None:
        """倒计时更新循环"""
        if self.timer.is_running:
            elapsed = time.time() - self.timer.start_time
            self.timer.remaining_seconds = max(0, self.timer.remaining_seconds - elapsed)
            
            self.update_timer_display()
            
            # 检查是否完成
            if self.timer.remaining_seconds <= 0:
                self._on_timer_complete()
            else:
                # 继续更新（每秒）
                self.timer_job = self.root.after(100, self._update_timer_loop)
    
    def update_timer_display(self) -> None:
        """更新倒计时显示"""
        remaining = int(self.timer.remaining_seconds)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.timer_time_var.set(time_str)
    
    def _on_timer_complete(self) -> None:
        """倒计时完成处理"""
        self.timer.is_running = False
        self.timer_start_btn.config(text="▶️ 开始")
        self.timer_status_var.set("⏰ 时间到！")
        
        # 视觉提醒：闪烁
        self._start_timer_blink()
        
        # 声音提醒
        if self.timer.sound_enabled:
            self.root.bell()
        
        # 发送系统通知
        preset_name = self.timer.preset_name if self.timer.preset_name else "倒计时"
        self.send_notification("⏰ 倒计时完成", preset_name)
        
        print("⏰ 倒计时完成！")
    
    def _start_timer_blink(self) -> None:
        """开始闪烁提醒"""
        self.timer_is_blinking = True
        self._timer_blink_state = True
        self._timer_blink_loop()
    
    def _timer_blink_loop(self) -> None:
        """闪烁循环"""
        if not self.timer_is_blinking:
            return
        
        self._timer_blink_state = not self._timer_blink_state
        if self._timer_blink_state:
            self.timer_label.config(fg="#ff0000")
            self.timer_frame.config(bg="#330000")
        else:
            self.timer_label.config(fg=self.text_color)
            self.timer_frame.config(bg=self.bg_color)
        
        self.timer_blink_job = self.root.after(500, self._timer_blink_loop)
    
    def _stop_timer_blink(self) -> None:
        """停止闪烁"""
        self.timer_is_blinking = False
        if self.timer_blink_job:
            self.root.after_cancel(self.timer_blink_job)
            self.timer_blink_job = None
        self.timer_label.config(fg=self.text_color)
        self.timer_frame.config(bg=self.bg_color)
    
    # ========== 计时器呼吸灯效果 ==========
    
    def _start_timer_breath_effect(self) -> None:
        """启动计时器呼吸灯效果"""
        self.timer_breath_phase = 0.0
        self._update_timer_breath_effect()
    
    def _stop_timer_breath_effect(self) -> None:
        """停止计时器呼吸灯效果"""
        if hasattr(self, 'timer_breath_job') and self.timer_breath_job:
            self.root.after_cancel(self.timer_breath_job)
            self.timer_breath_job = None
        # 恢复主题色
        self.timer_label.config(fg=self.text_color)
    
    def _update_timer_breath_effect(self) -> None:
        """更新计时器呼吸灯效果（颜色渐变）"""
        import math
        
        if not self.timer.is_running:
            return
        
        # 更新呼吸相位
        self.timer_breath_phase += 0.1
        if self.timer_breath_phase > 2 * math.pi:
            self.timer_breath_phase -= 2 * math.pi
        
        # 计算呼吸因子 (0.5 - 1.0)
        breath_factor = 0.75 + 0.25 * math.sin(self.timer_breath_phase)
        
        # 根据主题色计算当前颜色
        if hasattr(self, 'seg_color_on'):
            # 将十六进制颜色转换为 RGB
            r = int(self.seg_color_on[1:3], 16)
            g = int(self.seg_color_on[3:5], 16)
            b = int(self.seg_color_on[5:7], 16)
            
            # 应用呼吸因子（亮度变化）
            r = int(r * breath_factor)
            g = int(g * breath_factor)
            b = int(b * breath_factor)
            
            # 转换回十六进制
            breath_color = f"#{r:02x}{g:02x}{b:02x}"
            self.timer_label.config(fg=breath_color)
        
        # 继续更新
        self.timer_breath_job = self.root.after(50, self._update_timer_breath_effect)
    
    def save_timer_config(self) -> None:
        """保存倒计时配置到 config.json"""
        timer_config = {
            "total_duration": self.timer.total_seconds,
            "remaining_time": self.timer.remaining_seconds,
            "sound_enabled": self.timer.sound_enabled,
            "last_preset": self.timer.preset_name
        }
        
        # 加载现有配置
        config = self.load_config()
        config["timer"] = timer_config
        self.save_config(config)
    
    def load_timer_config(self) -> None:
        """从 config.json 加载倒计时配置"""
        timer_config = self.config.get("timer", {})
        if timer_config:
            self.timer.total_seconds = timer_config.get("total_duration", 0)
            self.timer.remaining_seconds = timer_config.get("remaining_time", 0)
            self.timer.sound_enabled = timer_config.get("sound_enabled", True)
            self.timer.preset_name = timer_config.get("last_preset", "")
            self.timer_sound_var.set(self.timer.sound_enabled)
            self.update_timer_display()
    
    # ========== 窗口关闭方法 ==========
    
    def on_close(self) -> None:
        """
        窗口关闭事件处理
        保存当前窗口位置、大小和可调整状态
        """
        # 停止秒表定时器（如果正在运行）
        if self.stopwatch.is_running:
            self.stopwatch_stop()
        
        # 停止倒计时定时器（如果正在运行）
        if self.timer.is_running:
            self.timer_stop()
        
        # 获取当前窗口几何信息
        geometry: str = self.root.geometry()
        # geometry 格式："WIDTHxHEIGHT+X+Y"
        try:
            # 解析窗口位置和大小
            parts: List[str] = geometry.split("+")
            size_part: str = parts[0]  # "WIDTHxHEIGHT"
            width: int = int(size_part.split("x")[0])
            height: int = int(size_part.split("x")[1])
            
            # 保存窗口配置
            self.config["window"]["width"] = width
            self.config["window"]["height"] = height
            # resizable() 返回元组 (width, height)，转换为布尔值
            resizable_state = self.root.resizable()
            self.config["window"]["resizable"] = bool(resizable_state[0]) if isinstance(resizable_state, tuple) else True
            
            # 如果有位置信息，也保存
            if len(parts) >= 3:
                x: int = int(parts[1])
                y: int = int(parts[2])
                self.config["window"]["x"] = x
                self.config["window"]["y"] = y
            
            # 保存配置
            self.save_config()
            print("✅ 窗口配置已保存")
        except Exception as e:
            print(f"⚠️  保存窗口配置失败：{e}")
        
        # 销毁窗口
        self.root.destroy()


def main() -> None:
    """主函数 - 启动时钟应用"""
    print("🕐 启动 ClawClock...")
    print(f"   Python 版本：{sys.version.split()[0]}")
    print(f"   Tkinter 版本：{tk.TkVersion}")
    print()
    
    root: tk.Tk = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')  # 使用现代主题
    
    app = ClockApp(root)
    
    print("✅ ClawClock 已启动")
    print("   提示：关闭窗口退出应用")
    print()
    
    root.mainloop()
    
    print("👋 ClawClock 已退出")


if __name__ == "__main__":
    main()
