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
    - 全屏支持
    - 窗口置顶

使用方法:
    python3 clock.py

依赖:
    - Python 3.8+
    - tkinter

作者：ClawClock Development Team
许可证：MIT
版本：1.1.0
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


@dataclass
class Alarm:
    """闹钟数据类"""
    time: str  # HH:MM 格式
    enabled: bool = True
    label: str = ""
    sound: str = "default"
    repeat_days: List[int] = field(default_factory=list)  # 0=Monday, 6=Sunday
    
    def is_due(self, current_time: datetime.datetime) -> bool:
        """检查当前时间是否触发闹钟"""
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
        self.root.title("ClawClock - 图形时钟")
        
        # 加载配置文件
        self.config: Dict[str, Any] = self.load_config()
        
        # 加载主题
        self.themes: Dict[str, Dict[str, Any]] = self.load_themes()
        
        # 初始化闹钟列表
        self.alarms: List[Alarm] = []
        self.alarm_triggered: bool = False
        self._load_alarms()
        
        # 应用窗口配置
        width: int = self.config.get("window", {}).get("width", 600)
        height: int = self.config.get("window", {}).get("height", 500)
        resizable: bool = self.config.get("window", {}).get("resizable", False)
        x: Optional[int] = self.config.get("window", {}).get("x", None)
        y: Optional[int] = self.config.get("window", {}).get("y", None)
        always_on_top: bool = self.config.get("window", {}).get("always_on_top", False)
        fullscreen: bool = self.config.get("window", {}).get("fullscreen", False)
        
        # 设置窗口几何信息（包括位置，如果有）
        if x is not None and y is not None:
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.root.geometry(f"{width}x{height}")
        
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
        self.display_mode: str = self.config.get("display_mode", "analog")
        
        # 应用主题（会设置所有颜色）
        self.apply_theme(theme_name)
        
        # Setup UI
        self.setup_ui()
        
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
            "display_mode": "analog",
            "window": {
                "width": 600,
                "height": 500,
                "resizable": False,
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
            "alarms": []
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
                repeat_days=alarm_data.get("repeat_days", [])
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
                "repeat_days": alarm.repeat_days
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
        """触发闹钟"""
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
        tk.Button(btn_frame, text="稍后提醒", command=lambda: self._snooze_alarm(dialog), width=10).pack(side=tk.LEFT, padx=10)
        
        # 播放提示音（系统蜂鸣）
        try:
            self.root.bell()
        except Exception:
            pass
    
    def _snooze_alarm(self, dialog: tk.Toplevel) -> None:
        """稍后提醒（5 分钟后）"""
        self.alarm_triggered = False
        dialog.destroy()
        
        # 5 分钟后重新触发
        def snooze_callback():
            for alarm in self.alarms:
                if alarm.enabled:
                    self.alarm_triggered = True
                    self.root.after(0, self._trigger_alarm, alarm)
                    break
        
        self.root.after(300000, snooze_callback)  # 300000ms = 5 分钟
    
    def add_alarm(self, time_str: str, label: str = "") -> bool:
        """
        添加新闹钟
        
        Args:
            time_str: 时间字符串 (HH:MM)
            label: 闹钟标签
        
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
        
        alarm = Alarm(time=time_str, label=label)
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
        
        # 重新绘制 UI
        if hasattr(self, 'canvas'):
            self.refresh_ui()
        
        # 保存配置
        self.save_config()
        
        print(f"✅ 主题已切换：{theme_name}")
    
    def refresh_ui(self) -> None:
        """
        刷新 UI 以应用新主题
        """
        # 更新主框架背景色
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.bg_color)
                # 更新子组件
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        child.configure(bg=self.bg_color)
                    elif isinstance(child, tk.Label):
                        child.configure(bg=self.bg_color, fg=self.text_color)
                    elif isinstance(child, tk.Radiobutton):
                        child.configure(bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color)
        
        # 重新绘制表盘
        self.draw_clock_face()
        
        # 如果是数字模式，重新绘制数码管
        if self.mode_var.get() == "digital":
            now = datetime.datetime.now()
            time_str = now.strftime("%H:%M:%S")
            self.draw_seven_segment_time(time_str)
    
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
        
        # Mode toggle - 只保留 Analog 和 Digital（从配置加载）
        self.mode_var: tk.StringVar = tk.StringVar(value=self.display_mode)
        mode_frame: tk.Frame = tk.Frame(main_frame, bg=self.bg_color)
        mode_frame.pack(pady=(0, 10))
        
        tk.Radiobutton(mode_frame, text="Analog", variable=self.mode_var, value="analog", 
                       bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                       command=self.update_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Digital", variable=self.mode_var, value="digital", 
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
        
        # Canvas for analog clock - 居中显示
        self.canvas: tk.Canvas = tk.Canvas(main_frame, width=300, height=300, bg=self.face_color, highlightthickness=0)
        self.canvas.pack(pady=10)  # 居中显示
        
        # Digital time display - 7 段数码管风格（初始隐藏）
        self.digital_frame: tk.Frame = tk.Frame(main_frame, bg=self.bg_color)
        # 不立即 pack，由 update_mode 控制显示
        
        # 7 段数码管画布 - 计算所需宽度
        canvas_width: int = 330
        canvas_height: int = 80
        self.seg_canvas: tk.Canvas = tk.Canvas(self.digital_frame, width=canvas_width, height=canvas_height, 
                                                bg=self.bg_color, highlightthickness=0)
        self.seg_canvas.pack(expand=True)
        
        self.date_label: tk.Label = tk.Label(self.digital_frame, text="", font=("Arial", 14), 
                                              bg=self.bg_color, fg=self.text_color)
        self.date_label.pack(pady=10)
        
        # 7 段数码管段定义 (a,b,c,d,e,f,g) - 单个数字的段坐标
        self.seg_width: int = 35
        self.seg_height: int = 60
        self.seg_thickness: int = 5
        self.digit_spacing: int = 10
        self.colon_space: int = 25
        
        # Draw clock face
        self.draw_clock_face()
    
    def _update_button_states(self) -> None:
        """更新按钮状态显示"""
        is_fullscreen = self.config.get("window", {}).get("fullscreen", False)
        is_topmost = self.config.get("window", {}).get("always_on_top", False)
        
        self.fullscreen_btn.config(text="❐ 退出全屏" if is_fullscreen else "🔲 全屏")
        self.topmost_btn.config(text="📍 取消置顶" if is_topmost else "📌 置顶")
    
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
        for i, alarm in enumerate(self.alarms):
            status = "✓" if alarm.enabled else "✗"
            label = f"{status} {alarm.time}"
            if alarm.label:
                label += f" - {alarm.label}"
            self.alarm_listbox.insert(tk.END, label)
    
    def _add_alarm_from_dialog(self, dialog: tk.Toplevel) -> None:
        """从对话框添加闹钟"""
        add_dialog = tk.Toplevel(dialog)
        add_dialog.title("添加闹钟")
        add_dialog.geometry("250x150")
        add_dialog.attributes("-topmost", True)
        
        tk.Label(add_dialog, text="时间 (HH:MM):").pack(pady=5)
        time_entry = tk.Entry(add_dialog)
        time_entry.pack(pady=5)
        time_entry.insert(0, "07:00")
        
        tk.Label(add_dialog, text="标签 (可选):").pack(pady=5)
        label_entry = tk.Entry(add_dialog)
        label_entry.pack(pady=5)
        
        def add():
            time_str = time_entry.get().strip()
            label = label_entry.get().strip()
            if self.add_alarm(time_str, label):
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
        """绘制单个段"""
        color: str = self.seg_color_on if active else self.seg_color_off
        # 绘制梯形段，模拟真实数码管
        thickness: int = self.seg_thickness
        self.seg_canvas.create_line(x1, y1, x2, y2, fill=color, width=thickness, capstyle=tk.ROUND)
    
    def draw_digit(self, digit: int, x_offset: float) -> None:
        """绘制 7 段数码管数字"""
        # 数字对应的段 (a,b,c,d,e,f,g)
        digit_segs: Dict[int, List[int]] = {
            0: [1, 1, 1, 1, 1, 1, 0],
            1: [0, 1, 1, 0, 0, 0, 0],
            2: [1, 1, 0, 1, 1, 0, 1],
            3: [1, 1, 1, 1, 0, 0, 1],
            4: [0, 1, 1, 0, 0, 1, 1],
            5: [1, 0, 1, 1, 0, 1, 1],
            6: [1, 0, 1, 1, 1, 1, 1],
            7: [1, 1, 1, 0, 0, 0, 0],
            8: [1, 1, 1, 1, 1, 1, 1],
            9: [1, 1, 1, 1, 0, 1, 1],
        }
        
        segs: List[int] = digit_segs.get(digit, [0, 0, 0, 0, 0, 0, 0])
        
        # 段坐标定义（相对于数字左上角）
        w: int = self.seg_width
        h: int = self.seg_height
        t: int = self.seg_thickness
        margin: int = 3  # 数字边缘留白
        
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
        """绘制冒号分隔符"""
        r: int = 3
        h: int = self.seg_height
        cx: float = x_offset
        cy1: float = h // 3      # 上圆点垂直位置
        cy2: float = h * 2 // 3  # 下圆点垂直位置
        self.seg_canvas.create_oval(cx-r, cy1-r, cx+r, cy1+r, fill=self.seg_color_on)
        self.seg_canvas.create_oval(cx-r, cy2-r, cx+r, cy2+r, fill=self.seg_color_on)
    
    def draw_seven_segment_time(self, time_str: str) -> None:
        """绘制 7 段数码管时间显示"""
        self.seg_canvas.delete("all")
        
        # 解析时间 HH:MM:SS
        parts: List[str] = time_str.split(":")
        if len(parts) >= 3:
            digits: List[int] = [int(parts[0][0]), int(parts[0][1]),  # 小时
                          int(parts[1][0]), int(parts[1][1]),  # 分钟
                          int(parts[2][0]), int(parts[2][1])]  # 秒
            
            # 计算每位数字的 x 偏移量
            w: int = self.seg_width      # 数字宽度 (35px)
            s: int = self.digit_spacing  # 数字间距 (10px)
            c: int = self.colon_space    # 冒号区空间 (25px)
            margin: int = 15             # 左右边距
            
            # 逐步计算每个位置的起始 x 坐标
            x0: float = margin                                    # 小时十位
            x1: float = x0 + w + s                                # 小时个位
            x2: float = x1 + w + s + c                            # 分钟十位（跳过冒号区）
            x3: float = x2 + w + s                                # 分钟个位
            x4: float = x3 + w + s + c                            # 秒钟十位（跳过冒号区）
            x5: float = x4 + w + s                                # 秒钟个位
            
            offsets: List[float] = [x0, x1, x2, x3, x4, x5]
            
            for i, digit in enumerate(digits):
                self.draw_digit(digit, offsets[i])
            
            # 绘制冒号（在冒号区正中央）
            colon1_x: float = x1 + w + c // 2    # 时分之间的冒号
            colon2_x: float = x3 + w + c // 2    # 分秒之间的冒号
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
        elif mode == "digital":
            self.canvas.pack_forget()
            self.digital_frame.pack(pady=10)  # 居中显示
        
        # 更新配置并保存
        self.config["display_mode"] = mode
        self.save_config()
    
    def on_close(self) -> None:
        """
        窗口关闭事件处理
        保存当前窗口位置、大小和可调整状态
        """
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
            self.config["window"]["resizable"] = self.root.resizable()
            
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
